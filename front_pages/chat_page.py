import streamlit as st
from utils.agent_setting import Agent, Document
from utils.document_store import DocumentStore

def chat_page():
    st.title("房貸專員聊天助手")
    
    # Initialize chat components
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Initialize WatsonX
    if 'watsonx' not in st.session_state:
        st.session_state.watsonx = Agent(st.session_state.token_manager)
        
    # Initialize document store
    if 'document_store' not in st.session_state:
        st.session_state.document_store = DocumentStore()
    
    # Create chat interface
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