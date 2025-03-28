import streamlit as st
import pandas as pd
from utils.document_store import DocumentStore

def documents_page():
    st.title("文件管理")
    
    # 初始化 QA 文件存儲
    if 'qa_document_store' not in st.session_state:
        st.session_state.qa_document_store = DocumentStore(storage_dir="QA_files")
    
    # 初始化數據文件存儲
    if 'data_document_store' not in st.session_state:
        st.session_state.data_document_store = DocumentStore(storage_dir="Data_files")
    
    # 創建兩列佈局
    main_col, sidebar_col = st.columns([3, 1])
    
    with sidebar_col:
        st.subheader("上傳新文件")
        
        # 選擇文件類型
        doc_type = st.radio("選擇文件類型", ["QA問答文件", "模型資料"])
        
        uploaded_file = st.file_uploader(
            "選擇CSV檔",
            type=['csv'],
            help="支援的文件格式：CSV (10MB)",
            key=f"uploader_{doc_type}"
        )
        
        if uploaded_file:
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
            
            if file_size > 10:
                st.error(f"文件大小超過限制 (10MB)")
            else:
                if st.button("確認上傳", use_container_width=True):
                    with st.spinner("處理文件中..."):
                        try:
                            # 根據選擇的文件類型使用相應的文件存儲
                            doc_store = st.session_state.qa_document_store if doc_type == "QA問答文件" else st.session_state.data_document_store
                            
                            file_content = doc_store.read_csv(uploaded_file.read())
                            
                            if file_content:
                                doc_id = doc_store.add_document(
                                    uploaded_file.name,
                                    file_content
                                )
                                
                                st.success(f"文件 '{uploaded_file.name}' 已成功上傳！")
                                st.rerun()
                            else:
                                st.error("文件處理失敗")
                                
                        except Exception as e:
                            st.error(f"上傳失敗: {str(e)}")
        
        # 文件統計
        qa_documents = st.session_state.qa_document_store.get_all_documents()
        data_documents = st.session_state.data_document_store.get_all_documents()
        st.metric("QA文件數", len(qa_documents))
        st.metric("模型資料數", len(data_documents))
    
    with main_col:
        tab1, tab2 = st.tabs(["QA問答文件", "模型資料"])
        
        with tab1:
            st.subheader("已上傳的QA問答CSV檔")
            
            qa_documents = st.session_state.qa_document_store.get_all_documents()
            
            if not qa_documents:
                st.info("目前沒有上傳的QA問答文件。請使用側欄上傳文件。")
            else:
                # 搜索功能
                search_query = st.text_input("輸入搜索關鍵詞", key="qa_search_query")
                
                if search_query:
                    # 簡單文本搜索
                    results = []
                    
                    for doc in qa_documents:
                        doc_content = st.session_state.qa_document_store.get_document_content(doc['id'])
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
                                # 嘗試以數據框形式顯示並高亮匹配單元格
                                try:
                                    lines = result['content'].strip().split('\n')
                                    header = lines[0].split(',')
                                    rows = [line.split(',') for line in lines[1:]]
                                    
                                    if all(len(row) == len(header) for row in rows):
                                        df = pd.DataFrame(rows, columns=header)
                                        
                                        # 應用樣式以高亮匹配項
                                        def highlight_cells(val):
                                            if search_query.lower() in str(val).lower():
                                                return 'background-color: yellow'
                                            return ''
                                        
                                        st.dataframe(df.style.applymap(highlight_cells))
                                    else:
                                        # 在文本中高亮結果
                                        content = result['content']
                                        highlighted_content = content.replace(
                                            search_query, 
                                            f"**{search_query}**"
                                        )
                                        st.markdown(highlighted_content)
                                except:
                                    # 退回到帶高亮的文本
                                    content = result['content']
                                    highlighted_content = content.replace(
                                        search_query, 
                                        f"**{search_query}**"
                                    )
                                    st.markdown(highlighted_content)
                else:
                    # 顯示所有 QA 問答文件
                    for doc in qa_documents:
                        # 為每個文件創建展開器
                        with st.expander(f"{doc['name']} ({doc['size_kb']} KB)"):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                doc_content = st.session_state.qa_document_store.get_document_content(doc['id'])
                                
                                # 嘗試以數據框形式顯示
                                try:
                                    lines = doc_content.strip().split('\n')
                                    header = lines[0].split(',')
                                    rows = [line.split(',') for line in lines[1:]]
                                    
                                    # 檢查所有行的長度是否與標題一致
                                    if all(len(row) == len(header) for row in rows):
                                        df = pd.DataFrame(rows, columns=header)
                                        st.dataframe(df, height=250)
                                    else:
                                        st.text_area(
                                            "文件內容", 
                                            doc_content, 
                                            height=250,
                                            disabled=True,
                                            key=f"qa_content_{doc['id']}"
                                        )
                                except:
                                    st.text_area(
                                        "文件內容", 
                                        doc_content, 
                                        height=250,
                                        disabled=True,
                                        key=f"qa_content_{doc['id']}"
                                    )
                            
                            with col2:
                                st.download_button(
                                    "下載CSV",
                                    doc_content,
                                    file_name=doc['name'],
                                    mime="text/csv",
                                    key=f"qa_download_{doc['id']}"
                                )
                                
                                st.write("")
                                
                                if st.button("刪除文件", key=f"qa_delete_{doc['id']}"):
                                    if st.session_state.qa_document_store.delete_document(doc['id']):
                                        st.success(f"文件 '{doc['name']}' 已刪除！")
                                        st.rerun()
                                    else:
                                        st.error("刪除失敗")
        
        with tab2:
            st.subheader("已上傳的模型資料CSV檔")
            
            data_documents = st.session_state.data_document_store.get_all_documents()
            
            if not data_documents:
                st.info("目前沒有上傳的模型資料。請使用側欄上傳文件。")
            else:
                # 搜索功能
                search_query = st.text_input("輸入搜索關鍵詞")
                
                if search_query:
                    # 簡單文本搜索
                    results = []
                    
                    for doc in data_documents:
                        doc_content = st.session_state.data_document_store.get_document_content(doc['id'])
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
                                # 嘗試以數據框形式顯示並高亮匹配單元格
                                try:
                                    lines = result['content'].strip().split('\n')
                                    header = lines[0].split(',')
                                    rows = [line.split(',') for line in lines[1:]]
                                    
                                    if all(len(row) == len(header) for row in rows):
                                        df = pd.DataFrame(rows, columns=header)
                                        
                                        # 應用樣式以高亮匹配項
                                        def highlight_cells(val):
                                            if search_query.lower() in str(val).lower():
                                                return 'background-color: yellow'
                                            return ''
                                        
                                        st.dataframe(df.style.applymap(highlight_cells))
                                    else:
                                        # 在文本中高亮結果
                                        content = result['content']
                                        highlighted_content = content.replace(
                                            search_query, 
                                            f"**{search_query}**"
                                        )
                                        st.markdown(highlighted_content)
                                except:
                                    # 退回到帶高亮的文本
                                    content = result['content']
                                    highlighted_content = content.replace(
                                        search_query, 
                                        f"**{search_query}**"
                                    )
                                    st.markdown(highlighted_content)
                else:
                    # 顯示所有模型資料文件
                    for doc in data_documents:
                        # 為每個文件創建展開器
                        with st.expander(f"{doc['name']} ({doc['size_kb']} KB)"):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                doc_content = st.session_state.data_document_store.get_document_content(doc['id'])
                                
                                # 嘗試以數據框形式顯示
                                try:
                                    lines = doc_content.strip().split('\n')
                                    header = lines[0].split(',')
                                    rows = [line.split(',') for line in lines[1:]]
                                    
                                    # 檢查所有行的長度是否與標題一致
                                    if all(len(row) == len(header) for row in rows):
                                        df = pd.DataFrame(rows, columns=header)
                                        st.dataframe(df, height=250)
                                    else:
                                        st.text_area(
                                            "文件內容", 
                                            doc_content, 
                                            height=250,
                                            disabled=True,
                                            key=f"data_content_{doc['id']}"
                                        )
                                except:
                                    st.text_area(
                                        "文件內容", 
                                        doc_content, 
                                        height=250,
                                        disabled=True,
                                        key=f"data_content_{doc['id']}"
                                    )
                            
                            with col2:
                                st.download_button(
                                    "下載CSV",
                                    doc_content,
                                    file_name=doc['name'],
                                    mime="text/csv",
                                    key=f"data_download_{doc['id']}"
                                )
                                
                                st.write("")
                                
                                if st.button("刪除文件", key=f"data_delete_{doc['id']}"):
                                    if st.session_state.data_document_store.delete_document(doc['id']):
                                        st.success(f"文件 '{doc['name']}' 已刪除！")
                                        st.rerun()
                                    else:
                                        st.error("刪除失敗")