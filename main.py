import streamlit as st
from components.prediction_page import PredictionPage
from components.dashboard_page import DashboardPage
from components.chatbot_page import ChatbotPage
from components.model_page import ModelPage

def main():
    st.set_page_config(
        page_title="Churn Analysis",
        page_icon="📊",
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
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state for navigation if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Prediction Page'

    # Navigation sidebar
    with st.sidebar:
        # Centered title
        st.markdown('<p class="sidebar-title">台新銀行</p>', unsafe_allow_html=True)
        
        # Navigation buttons
        if st.button('Prediction Page', use_container_width=True):
            st.session_state.current_page = 'Prediction Page'
            st.rerun()
            
        if st.button('Dashboard Page', use_container_width=True):
            st.session_state.current_page = 'Dashboard Page'
            st.rerun()

        if st.button('Model Page', use_container_width=True):
            st.session_state.current_page = 'Model Page'
            st.rerun()
            
        if st.button('Chatbot Page', use_container_width=True):
            st.session_state.current_page = 'Chatbot Page'
            st.rerun()

    # Page routing
    pages = {
        'Prediction Page': PredictionPage,
        'Dashboard Page': DashboardPage,
        'Model Page': ModelPage,
        'Chatbot Page': ChatbotPage
    }

    # Render the selected page
    page = pages[st.session_state.current_page]()
    page.render()

if __name__ == "__main__":
    main()