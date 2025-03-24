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
        # 初始化令牌管理器
        self.api_key = os.getenv("WATSONX_API_KEY")
        self.token = None
        self.token_expiry = None
        self.token_lock = threading.Lock()
        self.refresh_token()
        
        # 啟動背景線程進行令牌自動刷新
        self._start_token_refresh_thread()
    
    def refresh_token(self):
        try:
            with self.token_lock:
                # 檢查API金鑰是否存在
                if not self.api_key:
                    st.error("WATSONX_API_KEY 環境變數未設置")
                    return None
                    
                # 請求新令牌
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
                    # 設置過期時間為55分鐘（而非1小時）
                    self.token_expiry = datetime.datetime.now() + datetime.timedelta(minutes=55)
                    return self.token
                else:
                    st.error(f"令牌刷新失敗: 狀態碼 {token_response.status_code} - {token_response.text}")
                    return None
        except Exception as e:
            st.error(f"令牌刷新過程中發生錯誤: {str(e)}")
            return None
    
    def get_token(self):
        with self.token_lock:
            current_time = datetime.datetime.now()
            
            # 如果令牌將在5分鐘內過期，則刷新
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
                    
                    # 當令牌即將過期時刷新
                    if status["is_valid"] and status["remaining_time"] < 5:
                        self.refresh_token()
                    
                    # 每60秒檢查一次
                    time.sleep(60)
                except Exception as e:
                    # 捕獲線程中的異常以防止線程意外終止
                    print(f"令牌刷新線程發生錯誤: {str(e)}")
                    time.sleep(60)  # 發生錯誤時等待後重試
        
        # 啟動背景線程
        refresh_thread = threading.Thread(target=auto_refresh, daemon=True)
        refresh_thread.start()