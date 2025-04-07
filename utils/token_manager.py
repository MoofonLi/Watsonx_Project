import requests
import datetime
import time
import os
import dotenv
import streamlit as st
import threading

dotenv.load_dotenv()

class TokenManager:
    def __init__(self):
        # initialize token manager
        try:
            self.api_key = st.secrets["WATSONX_API_KEY"]
        except:
            self.api_key = os.getenv("WATSONX_API_KEY")
        self.token = None
        self.token_expiry = None
        self.token_lock = threading.Lock()
        self.refresh_token()
        
        # start token refresh thread
        self._start_token_refresh_thread()
    
    def refresh_token(self):
        try:
            with self.token_lock:
                    
                # request new token
                token_response = requests.post(
                    'https://iam.cloud.ibm.com/identity/token',
                    data={
                        "apikey": self.api_key,
                        "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'
                    }
                )
                
                if token_response.status_code == 200:
                    token_data = token_response.json()
                    self.token = token_data["access_token"]
                    # set token expiry to 55 minutes
                    self.token_expiry = datetime.datetime.now() + datetime.timedelta(minutes=55)
                    return self.token
                else:
                    st.error(f"Token refresh failed: {token_response.status_code} - {token_response.text}")
                    return None
        except Exception as e:
            st.error(f"Error during refresh Token: {str(e)}")
            return None
    
    def get_token(self):
        with self.token_lock:
            current_time = datetime.datetime.now()
            
            # refresh token if it is not available or expired
            if not self.token or not self.token_expiry or \
               (self.token_expiry - current_time).total_seconds() < 300:
                return self.refresh_token()
                
            return self.token
    
    def get_token_status(self):
        with self.token_lock:
            current_time = datetime.datetime.now()
            
            if not self.token or not self.token_expiry:
                return {
                    "is_valid": False,
                    "remaining_time": 0
                }
            
            remaining_seconds = (self.token_expiry - current_time).total_seconds()
            
            return {
                "is_valid": remaining_seconds > 0,
                "remaining_time": round(remaining_seconds / 60, 1)  # 分鐘
            }
    
    def _start_token_refresh_thread(self):
        def auto_refresh():
            while True:
                try:
                    status = self.get_token_status()
                    
                    # Refresh token if it is about to expire
                    if status["is_valid"] and status["remaining_time"] < 5:
                        self.refresh_token()
                    
                    # Check every 60 seconds
                    time.sleep(60)
                except Exception as e:
                    print(f"Refresh Token Failed: {str(e)}")
                    time.sleep(60)
        
        # Start token refresh thread
        refresh_thread = threading.Thread(target=auto_refresh, daemon=True)
        refresh_thread.start()