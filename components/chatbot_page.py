import streamlit as st
from utils.chat_utils import ChatManager

class ChatbotPage:
    def __init__(self):
        self.chat_manager = ChatManager()

    def render(self):
        st.title("AI Assistant")
        
        self._display_chat_history()
        self._render_input_area()

    def _display_chat_history(self):
        messages = self.chat_manager.get_messages()
        for message in messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    def _render_input_area(self):
        if prompt := st.chat_input("Enter your question"):
            # Add message to chat history
            self.chat_manager.add_message("user", prompt)
            response = self._get_bot_response(prompt)
            self.chat_manager.add_message("assistant", response)
            st.rerun()  # Refresh page to show new messages

    def _get_bot_response(self, prompt: str) -> str:
        return prompt