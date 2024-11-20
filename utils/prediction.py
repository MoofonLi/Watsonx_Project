import requests
import streamlit as st
from typing import List, Dict, Any

class PredictionAPI:
    def __init__(self, api_key: str, deployment_id: str):

        token_response = requests.post(
            'https://iam.cloud.ibm.com/identity/token', 
            data={
                "apikey": api_key,
                "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'
            }
        )
        mltoken = token_response.json()["access_token"]
        
        self.base_url = f"https://us-south.ml.cloud.ibm.com/ml/v4/deployments/{deployment_id}/predictions?version=2021-05-01"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {mltoken}'
        }

    def predict(self, input_data: List) -> Dict[str, Any]:
        payload = {
            "input_data": [{
                "fields": [
                    "credit_score",
                    "country",
                    "gender",
                    "age",
                    "tenure",
                    "balance",
                    "products_number",
                    "credit_card",
                    "active_member",
                    "estimated_salary"
                ],
                "values": [input_data]
            }]
        }

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Request Failed: {str(e)}")
            return None