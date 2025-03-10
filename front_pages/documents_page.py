import streamlit as st
import pandas as pd
from utils.document_store import DocumentStore

def documents_page():
    st.title("房貸知識庫文件管理")
    
    # Initialize document store if needed
    if 'document_store' not in st.session_state:
        st.session_state.document_store = DocumentStore()
    
    # Create a layout with two columns
    main_col, sidebar_col = st.columns([3, 1])
    
    with sidebar_col:
        st.subheader("上傳新文件")
        
        uploaded_file = st.file_uploader(
            "選擇CSV檔",
            type=['csv'],
            help="支援的文件格式：CSV (10MB)"
        )
        
        if uploaded_file:
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
            
            if file_size > 10:
                st.error(f"文件大小超過限制 (10MB)")
            else:
                if st.button("確認上傳", use_container_width=True):
                    with st.spinner("處理文件中..."):
                        try:
                            file_content = st.session_state.document_store.read_csv(uploaded_file.read())
                            
                            if file_content:
                                doc_id = st.session_state.document_store.add_document(
                                    uploaded_file.name,
                                    file_content
                                )
                                
                                st.success(f"文件 '{uploaded_file.name}' 已成功上傳！")
                                st.rerun()
                            else:
                                st.error("文件處理失敗")
                                
                        except Exception as e:
                            st.error(f"上傳失敗: {str(e)}")
        
        # Document stats
        documents = st.session_state.document_store.get_all_documents()
        st.metric("已上傳文件數", len(documents))
    
    with main_col:
        tab1, tab2 = st.tabs(["文件列表", "全文檢索"])
        
        with tab1:
            st.subheader("已上傳的CSV檔")
            
            documents = st.session_state.document_store.get_all_documents()
            
            if not documents:
                st.info("目前沒有上傳的CSV檔。請使用側欄上傳文件。")
            else:
                for doc in documents:
                    # Create an expander for each document
                    with st.expander(f"{doc['name']} ({doc['size_kb']} KB)"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            doc_content = st.session_state.document_store.get_document_content(doc['id'])
                            
                            # Display as dataframe if possible
                            try:
                                lines = doc_content.strip().split('\n')
                                header = lines[0].split(',')
                                rows = [line.split(',') for line in lines[1:]]
                                
                                # Check if all rows have same length as header
                                if all(len(row) == len(header) for row in rows):
                                    df = pd.DataFrame(rows, columns=header)
                                    st.dataframe(df, height=250)
                                else:
                                    st.text_area(
                                        "文件內容", 
                                        doc_content, 
                                        height=250,
                                        disabled=True,
                                        key=f"content_{doc['id']}"
                                    )
                            except:
                                st.text_area(
                                    "文件內容", 
                                    doc_content, 
                                    height=250,
                                    disabled=True,
                                    key=f"content_{doc['id']}"
                                )
                        
                        with col2:
                            st.download_button(
                                "下載CSV",
                                doc_content,
                                file_name=doc['name'],
                                mime="text/csv",
                                key=f"download_{doc['id']}"
                            )
                            
                            st.write("")
                            
                            if st.button("刪除文件", key=f"delete_{doc['id']}"):
                                if st.session_state.document_store.delete_document(doc['id']):
                                    st.success(f"文件 '{doc['name']}' 已刪除！")
                                    st.rerun()
                                else:
                                    st.error("刪除失敗")
        
        with tab2:
            st.subheader("CSV檔搜索")
            
            search_query = st.text_input("輸入搜索關鍵詞")
            
            if search_query:
                # Simple text search
                results = []
                
                for doc in documents:
                    doc_content = st.session_state.document_store.get_document_content(doc['id'])
                    if search_query.lower() in doc_content.lower():
                        results.append({
                            "id": doc['id'],
                            "name": doc['name'],
                            "content": doc_content
                        })
                
                if not results:
                    st.info(f"沒有找到包含 '{search_query}' 的文件")
                else:
                    st.success(f"找到 {len(results)} 個結果")
                    
                    for result in results:
                        with st.expander(result['name']):
                            # Try to display as dataframe with highlighted cells
                            try:
                                lines = result['content'].strip().split('\n')
                                header = lines[0].split(',')
                                rows = [line.split(',') for line in lines[1:]]
                                
                                if all(len(row) == len(header) for row in rows):
                                    df = pd.DataFrame(rows, columns=header)
                                    
                                    # Apply styling to highlight matches
                                    def highlight_cells(val):
                                        if search_query.lower() in str(val).lower():
                                            return 'background-color: yellow'
                                        return ''
                                    
                                    st.dataframe(df.style.applymap(highlight_cells))
                                else:
                                    # Highlight results in text
                                    content = result['content']
                                    highlighted_content = content.replace(
                                        search_query, 
                                        f"**{search_query}**"
                                    )
                                    st.markdown(highlighted_content)
                            except:
                                # Fallback to text with highlighting
                                content = result['content']
                                highlighted_content = content.replace(
                                    search_query, 
                                    f"**{search_query}**"
                                )
                                st.markdown(highlighted_content)