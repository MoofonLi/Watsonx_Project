import requests
import streamlit as st
from typing import Optional, Dict, Any, List
import numpy as np
import re
from dataclasses import dataclass
import os


@dataclass
class Document:
    content: str
    metadata: Dict[str, Any]

class Agent:
    def __init__(self, token_manager=None):
        # Initialize WatsonX API and vector storage
        self.token_manager = token_manager
        
        # API settings
        self.url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
        
    
    def _get_headers(self):
        # Get headers with fresh token
        token = self.token_manager.get_token() if self.token_manager else None
        
        if not token:
            st.error("Unable to get WatsonX API Token")
            return None
            
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
