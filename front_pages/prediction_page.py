import streamlit as st
from utils.prediction import MortgagePredictor

def prediction_page():
    st.title("房貸審核預測")
    st.markdown("### 請填寫客戶資料進行房貸審核預測")
    
    # Initialize predictor if needed
    if 'predictor' not in st.session_state:
        st.session_state.predictor = MortgagePredictor(st.session_state.token_manager)
    
    # Create form layout
    with st.form(key="mortgage_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("客戶年齡", min_value=20, max_value=70, value=35)
            income = st.number_input("年收入 (新台幣)", min_value=300000, max_value=5000000, value=800000, step=50000)
            credit_score = st.slider("信用評分", min_value=300, max_value=850, value=750)
            occupation = st.selectbox("職業", 
                                    ["上班族", "公務員", "軍人", "自營業主", "專業人士 (醫生/律師等)", "退休人士"])
            work_years = st.number_input("工作年資", min_value=0, max_value=40, value=5)
        
        with col2:
            loan_amount = st.number_input("貸款金額 (新台幣)", min_value=500000, max_value=30000000, value=5000000, step=500000)
            property_value = st.number_input("房屋價值 (新台幣)", min_value=1000000, max_value=50000000, value=8000000, step=500000)
            loan_term = st.selectbox("貸款期限 (年)", [10, 15, 20, 25, 30], index=3)
            has_other_loans = st.radio("是否有其他貸款", ["是", "否"], index=1)
            has_guarantor = st.radio("是否有擔保人", ["是", "否"], index=1)
        
        submit_button = st.form_submit_button(label="提交預測", use_container_width=True)

    # Handle form submission
    if submit_button:
        with st.spinner("正在評估您的申請..."):
            # Prepare data
            data = {
                "age": age,
                "income": f"{income:,} 元",
                "credit_score": credit_score,
                "occupation": occupation,
                "work_years": f"{work_years} 年",
                "loan_amount": f"{loan_amount:,} 元",
                "property_value": f"{property_value:,} 元",
                "loan_term": f"{loan_term} 年",
                "has_other_loans": has_other_loans,
                "has_guarantor": has_guarantor
            }
            
            # Predict using WatsonX
            result = st.session_state.predictor.predict(data)
            
            # Create result containers
            result_container = st.container()
            details_container = st.container()
            
            with result_container:
                # Display results
                if "error" in result:
                    st.error(result["error"])
                else:
                    # Check for structured JSON result
                    if "approval" in result:
                        approval_status = result.get("approval", "未知")
                        loan_to_value = result.get("loan_to_value", "未知")
                        interest_rate = result.get("interest_rate", "未知")
                        explanation = result.get("explanation", "未提供詳細信息")
                        risk_assessment = result.get("risk_assessment", "未提供風險評估")
                        
                        # Set style based on result
                        bg_color = "#d4edda" if "通過" in approval_status else "#f8d7da"
                        border_color = "#c3e6cb" if "通過" in approval_status else "#f5c6cb"
                        
                        st.markdown(f"""
                        <div style="padding: 20px; border-radius: 10px; margin-bottom: 20px; background-color: {bg_color}; border: 1px solid {border_color};">
                            <h3>審核結果: {approval_status}</h3>
                            <p><strong>建議房貸成數:</strong> {loan_to_value}</p>
                            <p><strong>建議利率:</strong> {interest_rate}</p>
                            <p><strong>審核說明:</strong> {explanation}</p>
                            <p><strong>風險評估:</strong> {risk_assessment}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Display unstructured result
                        st.markdown("### 預測結果")
                        st.write(result.get("result", "無法獲取預測結果"))
            
            with details_container:
                # Show customer data summary
                with st.expander("客戶資料摘要"):
                    st.json(data)
                
                col1, col2 = st.columns(2)
                with col1:
                    # LTV calculation
                    ltv = loan_amount / property_value * 100
                    st.metric("貸款成數 (LTV)", f"{ltv:.2f}%")
                
                with col2:
                    # Monthly payment estimation
                    monthly_payment = st.session_state.predictor.calculate_monthly_payment(
                        loan_amount, 
                        2.0,  # 2% interest
                        loan_term
                    )
                    st.metric("估計月付款 (年利率 2%)", f"{monthly_payment:,.2f} 元")