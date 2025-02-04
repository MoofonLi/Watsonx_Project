import streamlit as st
from utils.chatpage import ChatPage

def set_page_config():
    st.set_page_config(
        page_title="台新房貸專員系統",
        page_icon="🏦",
        layout="wide"
    )

def main():
    set_page_config()

    st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0;
    }
    .simple-header {
        color: white;
        font-size: 2.5em;
        font-weight: 500;
        text-align: center;
        margin: 2rem 0;
    }
    .stButton > button {
        background-color: #1f487e;
        color: white;
    }
    .upload-text {
        display: none;
    }
    .block-container {
        padding: 0 !important;
    }
    .css-1544g2n {
        padding: 0 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize chat page
    if 'chat_page' not in st.session_state:
        st.session_state.chat_page = ChatPage()

    st.markdown("<h1 class='simple-header'>台新銀行房貸專員系統</h1>", unsafe_allow_html=True)

    api_token = st.text_input("WatsonX API Token", type="password", key="api_token")
    if api_token:
        st.session_state.chat_page.init_watsonx(api_token)

    uploaded_file = st.file_uploader(
        "上傳知識庫文件",
        type=['txt', 'pdf', 'doc', 'docx', 'pptx'],
        help="支援的文件格式：PPTX (300MB)、PDF (50MB)、DOCX (10MB)、TXT (5MB)"
    )
    
    if uploaded_file:
        st.session_state.chat_page.handle_file_upload(uploaded_file)

    col1, col2 = st.columns(2)
    with col1:
        if 'watsonx' in st.session_state and st.session_state.watsonx:
            st.success("API 已連接")
        else:
            st.error("需要 API Token")
    with col2:
        if hasattr(st.session_state, 'current_file') and st.session_state.current_file:
            st.success("知識庫已載入")
        else:
            st.error("需要上傳知識庫")

    st.session_state.chat_page.render_chat()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("清除對話", use_container_width=True):
            st.session_state.chat_page.clear_chat()
    with col2:
        if st.button("清除文件", use_container_width=True):
            st.session_state.chat_page.clear_file()

if __name__ == "__main__":
    main()