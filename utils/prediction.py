import requests
import streamlit as st
import json
from typing import Dict, Any

class MortgagePredictor:
    def __init__(self, token_manager=None):
        self.token_manager = token_manager
        self.url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    
    def _get_headers(self):
        # Get token from manager
        token = self.token_manager.get_token() if self.token_manager else None
        
        if not token:
            st.error("Unable to get WatsonX API Token")
            return None
            
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Get headers with fresh token
        headers = self._get_headers()
        if not headers:
            return {"error": "API connection failed"}
        
        # Build prompt for prediction
        prompt = f"""<|start_of_role|>system<|end_of_role|>You are a mortgage approval assistant for Taishin Bank. Based on customer data, predict:
1. Approval result (approve/reject)
2. Loan-to-value ratio
3. Interest rate
4. Detailed explanation
5. Risk assessment

Return results in JSON format.
<|end_of_text|>
<|start_of_role|>user<|end_of_role|>
Predict mortgage approval for:

Age: {data.get('age', 'N/A')}
Annual Income: {data.get('income', 'N/A')}
Credit Score: {data.get('credit_score', 'N/A')}
Occupation: {data.get('occupation', 'N/A')}
Work Experience: {data.get('work_years', 'N/A')}
Loan Amount: {data.get('loan_amount', 'N/A')}
Property Value: {data.get('property_value', 'N/A')}
Loan Term: {data.get('loan_term', 'N/A')}
Other Loans: {data.get('has_other_loans', 'N/A')}
Guarantor: {data.get('has_guarantor', 'N/A')}
<|end_of_text|>
<|start_of_role|>assistant<|end_of_role|>"""

        payload = {
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 500,
                "min_new_tokens": 0,
                "repetition_penalty": 1
            },
            "model_id": "ibm/granite-3-8b-instruct",
            "project_id": "d91fb3ca-54ec-462a-9a26-491104a1d49d"
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            result_text = response.json().get('results', [{}])[0].get('generated_text', "")
            
            # Try to parse JSON from response
            try:
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_text = result_text[json_start:json_end]
                    result_json = json.loads(json_text)
                    return result_json
                else:
                    return {"result": result_text}
                    
            except json.JSONDecodeError:
                return {"result": result_text}
            
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {str(e)}")
            return {"error": "API request failed"}
            
    def calculate_monthly_payment(self, loan_amount, interest_rate, loan_term_years):
        # Calculate estimated monthly payment
        monthly_rate = interest_rate / 12 / 100
        num_payments = loan_term_years * 12
        
        if monthly_rate == 0:
            return loan_amount / num_payments
            
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
        return monthly_payment