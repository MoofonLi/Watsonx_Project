import streamlit as st
from front_pages.prediction_page import prediction_page
from front_pages.documents_page import documents_page
from front_pages.chat_page import chat_page
from utils.token_manager import TokenManager
import time

def main():
    st.set_page_config(
        page_title="台新房貸專員系統",
        page_icon="🏦",
        layout="wide"
    )
    # Custom CSS for the sidebar
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Reduce sidebar width */
        [data-testid="stSidebar"][aria-expanded="true"] {
            min-width: 200px;
            max-width: 200px;
        }
        
        /* Centered sidebar title */
        .sidebar-title {
            font-size: 2rem !important;
            font-weight: 700;
            padding: 1rem 0.5rem 1.5rem 0.5rem;
            margin: 0;
            color: #0F52BA;
            text-align: center;
            border-bottom: 2px solid #f0f2f6;
            margin-bottom: 1rem;
        }
        
        /* Remove padding from sidebar */
        section[data-testid="stSidebar"] > div {
            padding-top: 1rem;
        }
        
        /* Navigation button styling */
        .stButton > button {
            width: 100%;
            border: none;
            padding: 15px 15px;
            font-weight: 500;
            text-align: left;
            background-color: transparent;
            color: #1E1E1E;
        }
        
        .stButton > button:hover {
            color: #0F52BA;
            background-color: #f8f9fb;
        }
        
        .stButton > button:active, .stButton > button:focus {
            color: #0F52BA;
            background-color: #f0f2f6;
            border-right: 3px solid #0F52BA;
        }
        
        /* Hide hamburger menu */
        button[data-testid="StyledFullScreenButton"] {
            display: none;
        }
        
        /* White background for sidebar */
        [data-testid="stSidebar"] {
            background-color: white;
        }
        
        /* Add some spacing between buttons */
        .stButton {
            margin-bottom: 0.5rem;
        }
        
        /* Status indicator for token */
        .token-status {
            font-size: 0.8rem;
            margin-top: 0.5rem;
            padding: 0.5rem;
            border-radius: 0.3rem;
            text-align: center;
        }
        .token-valid {
            background-color: #d4edda;
            color: #155724;
        }
        .token-invalid {
            background-color: #f8d7da;
            color: #721c24;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize token manager
    if 'token_manager' not in st.session_state:
        st.session_state.token_manager = TokenManager()
    
    # Initialize session state for navigation if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'chat_page'
    
    # Navigation sidebar
    with st.sidebar:
        # Centered title
        st.markdown('<p class="sidebar-title">台新銀行</p>', unsafe_allow_html=True)
        
        # Navigation buttons
        if st.button('預測頁面', use_container_width=True):
            st.session_state.current_page = 'prediction_page'
            st.rerun()
            
        if st.button('文件頁面', use_container_width=True):
            st.session_state.current_page = 'documents_page'
            st.rerun()
            
        if st.button('聊天頁面', use_container_width=True):
            st.session_state.current_page = 'chat_page'
            st.rerun()
        
        
    
    # Page routing
    if st.session_state.current_page == 'prediction_page':
        prediction_page()
    elif st.session_state.current_page == 'documents_page':
        documents_page()
    else:  # Default to chat_page
        chat_page()

if __name__ == "__main__":
    main()