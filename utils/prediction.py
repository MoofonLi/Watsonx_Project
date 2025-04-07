import pandas as pd
import requests
import streamlit as st
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

class LoanPredictor:
    def __init__(self, token_manager=None):

        load_dotenv()
        
        
        try:
            self.api_key = st.secrets["WATSONX_API_KEY"]
            self.url = st.secrets("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
            self.deployment_id = st.secrets("WATSONX_DEPLOYMENT_ID")
            self.space_id = st.secrets("WATSONX_SPACE_ID")
        except:
            # local
            self.api_key = os.getenv("WATSONX_API_KEY")
            self.url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
            self.deployment_id = os.getenv("WATSONX_DEPLOYMENT_ID")
            self.space_id = os.getenv("WATSONX_SPACE_ID")

        self.token_manager = token_manager
        

        try:

            self.base_url = f"{self.url}/ml/v4/deployments/{self.deployment_id}/predictions?version=2021-05-01"
            
            if self.space_id:
                self.base_url += f"&space_id={self.space_id}"
            

            self.headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
        except Exception as e:
            st.error(f"API連接初始化錯誤: {str(e)}")
            if hasattr(e, 'response') and e.response:
                st.error(f"回應內容: {e.response.text}")
            raise
    
    def predict(self, df: pd.DataFrame, target_column: str) -> pd.DataFrame:
        """預測貸款核准金額"""
        if not self.token_manager:
            raise Exception("令牌管理器未初始化，無法進行預測")
        
        result_df = df.copy()
        

        try:
            # Get Newest Token
            token = self.token_manager.get_token()
            if not token:
                raise Exception("無法獲取有效的API令牌")
            

            self.headers['Authorization'] = f'Bearer {token}'
            

            required_fields = [
                "Gender", "Age", "Income (USD)", "Income Stability", 
                "Profession", "Type of Employment", "Location", 
                "Loan Amount Request (USD)", "Current Loan Expenses (USD)", 
                "Expense Type 1", "Expense Type 2", "Dependents", 
                "Credit Score", "No. of Defaults", "Has Active Credit Card", 
                "Property ID", "Property Age", "Property Type", 
                "Property Location", "Co-Applicant", "Property Price"
            ]
            
            # Check Required Fields
            missing_fields = [field for field in required_fields if field not in df.columns]
            if missing_fields:
                st.warning(f"注意：上傳數據缺少以下API需要的欄位: {', '.join(missing_fields)}")
                st.info("將嘗試使用可用欄位進行預測")
            

            values = []
            for _, row in df.iterrows():
                row_values = [
                    row[field] if field in df.columns and pd.notna(row[field]) else None 
                    for field in required_fields
                ]
                values.append(row_values)
            
            
            payload = {
                "input_data": [{
                    "fields": required_fields,
                    "values": values
                }]
            }
            
            
            with st.spinner("預測中"):
                response = requests.post(
                    self.base_url,
                    json=payload,
                    headers=self.headers,
                    timeout=60
                )
            

            if response.status_code == 401:
                st.warning("Token過期，正在嘗試重新獲取...")
                token = self.token_manager.refresh_token()
                if not token:
                    raise Exception("Cannot refresh token")
                
                self.headers['Authorization'] = f'Bearer {token}'
                with st.spinner("Use new token resent request..."):
                    response = requests.post(
                        self.base_url,
                        json=payload,
                        headers=self.headers,
                        timeout=60
                    )
            
            
            if response.status_code != 200:
                raise Exception(f"API request fail: {response.status_code}, Response: {response.text}")
            
            # Prediction Scuccess
            predictions = response.json()
            
            if 'predictions' in predictions and len(predictions['predictions']) > 0:
                prediction_values = predictions['predictions'][0]['values']
                result_df[f"Predicted_{target_column}"] = [
                    row[0] if row and len(row) > 0 else None 
                    for row in prediction_values
                ]
                st.success("預測結果如下")
                return result_df
            else:
                raise Exception(f"Prediction Error: {predictions}")
                    
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            raise