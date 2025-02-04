import streamlit as st
from .watsonx import WatsonX
import docx
import PyPDF2
import io
from pptx import Presentation
from typing import Optional, Tuple

class ChatPage:
    def __init__(self):
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'current_file' not in st.session_state:
            st.session_state.current_file = None
        if 'watsonx' not in st.session_state:
            st.session_state.watsonx = None
            
    def init_watsonx(self, api_token):
        if not st.session_state.watsonx:
            st.session_state.watsonx = WatsonX(api_token)

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
        
    def read_pptx(self, file_bytes) -> str:
        """讀取 PPTX 文件"""
        prs = Presentation(io.BytesIO(file_bytes))
        text = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text.append(shape.text)
        return '\n'.join(text)

    def handle_file_upload(self, uploaded_file) -> Optional[Tuple[str, str]]:
        """處理上傳的文件"""
        try:
            file_content = None
            file_type = uploaded_file.name.split('.')[-1].lower()
            
            # 檢查文件大小
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Convert to MB
            size_limits = {
                'pptx': 300,
                'pdf': 50,
                'docx': 10,
                'txt': 5
            }
            
            if file_size > size_limits.get(file_type, 5):
                st.error(f"文件大小超過限制 ({size_limits.get(file_type, 5)}MB)")
                return None
            
            # 根據文件類型讀取內容
            if file_type == 'txt':
                file_content = uploaded_file.read().decode('utf-8')
            elif file_type in ['doc', 'docx']:
                file_content = self.read_docx(uploaded_file.read())
            elif file_type == 'pdf':
                file_content = self.read_pdf(uploaded_file.read())
            elif file_type == 'pptx':
                file_content = self.read_pptx(uploaded_file.read())
            else:
                st.error("不支援的文件類型")
                return None

            st.session_state.current_file = {
                'name': uploaded_file.name,
                'content': file_content
            }
            
            # 處理文檔生成向量
            if st.session_state.watsonx:
                num_chunks = st.session_state.watsonx.process_document(
                    file_content,
                    {'filename': uploaded_file.name}
                )
                #st.success(f"文件已處理完成，共分為 {num_chunks} 個片段")
            
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
            
            if st.session_state.watsonx and st.session_state.current_file:
                context = st.session_state.watsonx.find_relevant_context(prompt)
                response = st.session_state.watsonx.generate_response(context, prompt)
                
                if response:
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.markdown(response)
            else:
                st.error("請先輸入 API token 並上傳知識庫文件")

    def clear_chat(self):
        st.session_state.messages = []
        st.rerun()

    def clear_file(self):
        st.session_state.current_file = None
        if st.session_state.watsonx:
            st.session_state.watsonx.vector_store = None
            st.session_state.watsonx.chunks = []
        st.rerun()