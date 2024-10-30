import streamlit as st
from utils.prediction import PredictionAPI
import os
from dotenv import load_dotenv

load_dotenv()

class PredictionPage:
    def __init__(self):
        self.api = PredictionAPI(os.getenv("IAM_TOKEN"), os.getenv("DEPLOYMENT_ID"))

    def render(self):
        st.title("Customer Churn Prediction")

        # Create input form
        with st.form("prediction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                age = st.number_input("Age", min_value=0, max_value=120)
                gender = st.selectbox("Gender", ["Male", "Female"])
                tenure = st.number_input("Tenure (months)", min_value=0)
                usage_freq = st.number_input("Usage Frequency", min_value=0)
                support_calls = st.number_input("Support Calls", min_value=0)

            with col2:
                payment_delay = st.number_input("Payment Delay (days)", min_value=0)
                subscription = st.selectbox("Subscription Type", ["Basic", "Standard", "Premium"])
                contract_length = st.selectbox("Contract Length", ["Monthly","Quarterly", "Yearly"])
                total_spend = st.number_input("Total Spend ($)", min_value=0)
                last_interaction = st.number_input("Last Interaction (days)", min_value=0)

            submitted = st.form_submit_button("Predict")

            if submitted:
                input_data = [
                    "0",  # Customer ID
                    age,
                    gender,
                    tenure,
                    usage_freq,
                    support_calls,
                    payment_delay,
                    subscription,
                    contract_length,
                    total_spend,
                    last_interaction
                ]

                with st.spinner("Predicting..."):
                    result = self.api.predict(input_data)
                    
                    if result and 'predictions' in result:
                        prediction = result['predictions'][0]['values'][0][0]
                        probability = result['predictions'][0]['values'][0][1][1]
                        
                        # Display prediction results
                        st.success("Prediction Complete!")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(
                                "Prediction Result", 
                                "Likely to Churn" if prediction == 1 else "Unlikely to Churn"
                            )
                        with col2:
                            st.metric("Churn Probability", f"{probability:.2%}")