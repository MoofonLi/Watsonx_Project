import streamlit as st
from .watsonx import WatsonX
import docx
import PyPDF2
import pandas as pd
import io
from typing import Optional, Tuple

class ChatPage:
    def __init__(self):
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'current_file' not in st.session_state:
            st.session_state.current_file = None
        if 'watsonx' not in st.session_state:
            st.session_state.watsonx = None
        
    def init_watsonx(self, api_key=None):
        """初始化 WatsonX 實例"""
        try:
            if not st.session_state.watsonx:
                st.session_state.watsonx = WatsonX(api_key)
        except Exception as e:
            st.error(f"WatsonX 初始化失敗: {str(e)}")
            st.session_state.watsonx = None

    @property
    def watsonx(self):
        """獲取 WatsonX 實例"""
        return st.session_state.watsonx

    def read_docx(self, file_bytes) -> str:
        """讀取 DOCX 文件"""
        doc = docx.Document(io.BytesIO(file_bytes))
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

    def read_pdf(self, file_bytes) -> str:
        """讀取 PDF 文件"""
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text() + '\n'
        return text
        
    def read_csv(self, file_bytes) -> str:
        """讀取 CSV 文件"""
        try:
            csv_file = io.BytesIO(file_bytes)
            
            encodings = ['utf-8', 'big5', 'gb18030']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_file, encoding=encoding)
                    csv_file.seek(0)
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    st.error(f"CSV讀取錯誤: {str(e)}")
                    return None
            
            if df is None:
                st.error("無法識別CSV文件編碼")
                return None
                
            text_content = []
            text_content.append(",".join(df.columns.astype(str)))
            
            for _, row in df.iterrows():
                text_content.append(",".join(row.astype(str)))
            
            return '\n'.join(text_content)
            
        except Exception as e:
            st.error(f"CSV處理錯誤: {str(e)}")
            return None

    def handle_file_upload(self, uploaded_file) -> Optional[Tuple[str, str]]:
        """處理上傳的文件"""
        try:
            file_content = None
            file_type = uploaded_file.name.split('.')[-1].lower()
            
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
            size_limits = {
                'pptx': 300,
                'pdf': 50,
                'docx': 10,
                'txt': 5,
                'csv': 10
            }
            
            if file_size > size_limits.get(file_type, 5):
                st.error(f"文件大小超過限制 ({size_limits.get(file_type, 5)}MB)")
                return None
            
            if file_type == 'txt':
                file_content = uploaded_file.read().decode('utf-8')
            elif file_type in ['doc', 'docx']:
                file_content = self.read_docx(uploaded_file.read())
            elif file_type == 'pdf':
                file_content = self.read_pdf(uploaded_file.read())
            elif file_type == 'csv':
                file_content = self.read_csv(uploaded_file.read())
            else:
                st.error("不支援的文件類型")
                return None

            st.session_state.current_file = {
                'name': uploaded_file.name,
                'content': file_content
            }
            
            if self.watsonx:
                num_chunks = self.watsonx.process_document(
                    file_content,
                    {'filename': uploaded_file.name}
                )
            
        except Exception as e:
            st.error(f"文件處理錯誤: {str(e)}")
            return None

    def render_chat(self):
        """渲染聊天界面"""
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt := st.chat_input("輸入您的問題"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            try:
                # Initialize WatsonX if not already initialized
                if not self.watsonx:
                    self.init_watsonx()
                    
                context = self.watsonx.find_relevant_context(prompt)
                response = self.watsonx.generate_response(context, prompt)
                
                if response:
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.markdown(response)
            except Exception as e:
                # Add default response in case of error
                default_response = "抱歉，我暫時無法處理您的請求。請稍後再試。"
                st.session_state.messages.append({"role": "assistant", "content": default_response})
                with st.chat_message("assistant"):
                    st.markdown(default_response)

    def clear_chat(self):
        st.session_state.messages = []
        st.rerun()

    def clear_file(self):
        st.session_state.current_file = None
        if self.watsonx:
            self.watsonx.vector_store = None
            self.watsonx.chunks = []
        st.rerun()