import streamlit as st
import pandas as pd
from utils.watsonx import WatsonX, Document
from utils.document_store import DocumentStore

def chat_page():
    st.title("房貸專員聊天助手")
    
    # Initialize chat components
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Initialize WatsonX
    if 'watsonx' not in st.session_state:
        st.session_state.watsonx = WatsonX(st.session_state.token_manager)
        
    # Initialize document store
    if 'document_store' not in st.session_state:
        st.session_state.document_store = DocumentStore()
    
    # Initialize context document
    if 'current_doc' not in st.session_state:
        st.session_state.current_doc = None
    
    # Create a layout with chat area and sidebar
    chat_col, config_col = st.columns([3, 1])
    
    with config_col:
        st.subheader("上傳參考CSV檔")
        
        uploaded_file = st.file_uploader(
            "上傳CSV檔",
            type=['csv'],
            help="上傳一個CSV檔來增強當前對話的上下文"
        )
        
        if uploaded_file:
            if st.button("處理文件", use_container_width=True):
                with st.spinner("處理文件中..."):
                    try:
                        file_content = st.session_state.document_store.read_csv(uploaded_file.read())
                        
                        if file_content:
                            st.session_state.current_doc = {
                                'name': uploaded_file.name,
                                'content': file_content
                            }
                            
                            # Initialize vector storage
                            st.session_state.watsonx.process_document(
                                file_content,
                                {'filename': uploaded_file.name}
                            )
                            
                            st.success(f"CSV檔 '{uploaded_file.name}' 已成功處理！")
                        else:
                            st.error("CSV檔處理失敗")
                            
                    except Exception as e:
                        st.error(f"處理失敗: {str(e)}")
        
        # Knowledge base integration
        st.subheader("知識庫設置")
        use_knowledge_base = st.checkbox("使用知識庫", value=True)
        
        if use_knowledge_base:
            documents = st.session_state.document_store.get_all_documents()
            if not documents:
                st.info("知識庫中沒有CSV檔。請前往文件庫頁面上傳。")
            else:
                st.success(f"已連接知識庫，包含 {len(documents)} 個CSV檔")
        
        if st.button("刷新知識庫連接", use_container_width=True):
            with st.spinner("更新知識庫連接..."):
                try:
                    # Process all documents for RAG
                    if st.session_state.current_doc and use_knowledge_base:
                        # Get all KB documents
                        knowledge_docs = []
                        for doc in st.session_state.document_store.get_all_documents():
                            content = st.session_state.document_store.get_document_content(doc['id'])
                            if content:
                                knowledge_docs.append(Document(
                                    content=content,
                                    metadata={'filename': doc['name']}
                                ))
                        
                        # Add current context document
                        knowledge_docs.append(Document(
                            content=st.session_state.current_doc['content'],
                            metadata={'filename': st.session_state.current_doc['name']}
                        ))
                        
                        # Process all documents
                        num_chunks = st.session_state.watsonx.process_multiple_documents(knowledge_docs)
                        st.success(f"成功處理 {len(knowledge_docs)} 個CSV檔，共 {num_chunks} 個文本片段")
                        
                    # If only KB
                    elif use_knowledge_base:
                        # Get all KB documents
                        knowledge_docs = []
                        for doc in st.session_state.document_store.get_all_documents():
                            content = st.session_state.document_store.get_document_content(doc['id'])
                            if content:
                                knowledge_docs.append(Document(
                                    content=content,
                                    metadata={'filename': doc['name']}
                                ))
                        
                        if knowledge_docs:
                            # Process all documents
                            num_chunks = st.session_state.watsonx.process_multiple_documents(knowledge_docs)
                            st.success(f"成功處理 {len(knowledge_docs)} 個CSV檔，共 {num_chunks} 個文本片段")
                        else:
                            st.warning("知識庫中沒有CSV檔")
                    
                    # If only context document
                    elif st.session_state.current_doc:
                        # Process current context document
                        num_chunks = st.session_state.watsonx.process_document(
                            st.session_state.current_doc['content'],
                            {'filename': st.session_state.current_doc['name']}
                        )
                        st.success(f"成功處理 1 個CSV檔，共 {num_chunks} 個文本片段")
                    
                    else:
                        st.warning("沒有可用的CSV檔來源")
                        
                except Exception as e:
                    st.error(f"更新知識庫失敗: {str(e)}")
        
        # Conversation controls
        st.subheader("對話控制")
        if st.button("清除對話", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
        if st.button("清除當前CSV檔", use_container_width=True):
            st.session_state.current_doc = None
            st.rerun()
    
    with chat_col:
        # Display current context document if any
        if st.session_state.current_doc:
            with st.expander(f"當前參考CSV檔: {st.session_state.current_doc['name']}"):
                try:
                    # Try to display as dataframe
                    lines = st.session_state.current_doc['content'].strip().split('\n')
                    header = lines[0].split(',')
                    rows = [line.split(',') for line in lines[1:]]
                    
                    if all(len(row) == len(header) for row in rows):
                        df = pd.DataFrame(rows, columns=header)
                        st.dataframe(df, height=150)
                    else:
                        st.text_area(
                            "CSV內容", 
                            st.session_state.current_doc['content'][:1000] + "..." if len(st.session_state.current_doc['content']) > 1000 else st.session_state.current_doc['content'],
                            height=150,
                            disabled=True
                        )
                except:
                    st.text_area(
                        "CSV內容", 
                        st.session_state.current_doc['content'][:1000] + "..." if len(st.session_state.current_doc['content']) > 1000 else st.session_state.current_doc['content'],
                        height=150,
                        disabled=True
                    )
        
        # Create chat container with custom styling
        chat_container = st.container()
        
        # Display conversation history
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("輸入您的問題"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("思考中..."):
                    try:
                        # Get relevant context
                        context = st.session_state.watsonx.find_relevant_context(prompt)
                        
                        # Generate response
                        response = st.session_state.watsonx.generate_response(context, prompt)
                        
                        if response:
                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                        else:
                            default_response = "抱歉，我暫時無法處理您的請求。請稍後再試。"
                            st.markdown(default_response)
                            st.session_state.messages.append({"role": "assistant", "content": default_response})
                            
                    except Exception as e:
                        error_msg = f"處理請求時出錯: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})