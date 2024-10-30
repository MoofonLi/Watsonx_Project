from typing import List, Dict
import streamlit as st

class ChatManager:
    def __init__(self):
        if 'messages' not in st.session_state:
            st.session_state.messages = []

    def add_message(self, role: str, content: str):
        """Add to history"""
        st.session_state.messages.append({"role": role, "content": content})

    def get_messages(self) -> List[Dict[str, str]]:
        """Get chat history"""
        return st.session_state.messages

    def clear_history(self):
        """Clear chat history"""
        st.session_state.messages = []