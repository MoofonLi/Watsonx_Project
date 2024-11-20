import streamlit as st
from utils.prediction import PredictionAPI
import os
from dotenv import load_dotenv

load_dotenv()

class PredictionPage:
    def __init__(self):

        api_key = os.getenv("API_KEY")
        deployment_id = os.getenv("DEPLOYMENT_ID")
        
        if not api_key or not deployment_id:
            st.error("Missing required environment variables. Please check .env file.")
            st.stop()
            
        self.api = PredictionAPI(api_key, deployment_id)

    def render(self):
        st.title("Customer Churn Prediction")

        # Create input form
        with st.form("prediction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                credit_score = st.number_input("Credit Score", value=600)
                country = st.selectbox("Country", ["Spain", "Germany", "France"])
                gender = st.selectbox("Gender", ["Female", "Male"])
                age = st.number_input("Age", min_value=18, max_value=100, value=44)
                tenure = st.number_input("Tenure", min_value=0, max_value=20, value=4)


            with col2:
                balance = st.number_input("Balance", value=0)
                products_number = st.number_input("Number of Products", value=2)
                credit_card = st.selectbox("Has Credit Card", [0, 1])
                active_member = st.selectbox("Is Active Member", [0, 1])
                estimated_salary = st.number_input("Estimated Salary", value=58560)

            submitted = st.form_submit_button("Predict")

            if submitted:
                try:
                    input_data = [
                        credit_score,    
                        country,     
                        gender,           
                        age,            
                        tenure,        
                        balance,         
                        products_number, 
                        credit_card, 
                        active_member,
                        estimated_salary 
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
                        else:
                            st.error("Failed to get prediction results")
                            
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")