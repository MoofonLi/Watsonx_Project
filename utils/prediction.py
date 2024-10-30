import requests
import streamlit as st
from typing import List, Dict, Any


class PredictionAPI:
    def __init__(self, iam_token: str, deployment_id: str):
        self.iam_token = iam_token
        self.deployment_id = deployment_id
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {iam_token}'
        }

    def predict(self, input_data: List) -> Dict[str, Any]:
        payload = {
            "input_data": [{
                "fields": [
                    "CustomerID",
                    "Age",
                    "Gender",
                    "Tenure",
                    "Usage Frequency",
                    "Support Calls",
                    "Payment Delay",
                    "Subscription Type",
                    "Contract Length",
                    "Total Spend",
                    "Last Interaction"
                ],
                "values": [input_data]
            }]
        }

        try:
            response = requests.post(
                self.deployment_id,
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Request Failed: {str(e)}")
            return None