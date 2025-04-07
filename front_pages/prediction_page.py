import streamlit as st
import pandas as pd
from utils.prediction import LoanPredictor
import io

def prediction_page():
    # 初始化 session state 來追蹤聊天是否已加載
    if "chat_loaded" not in st.session_state:
        st.session_state.chat_loaded = False
    
    st.title("預測頁面")
    
    if 'token_manager' not in st.session_state:
        st.error("Token Manager have not been initialized")
        return
    
    uploaded_file = st.file_uploader("上傳預測資料檔案 (CSV)", type=["csv"])
    
    if uploaded_file is not None:
        try:
            # User Operations
            df = pd.read_csv(uploaded_file)
            
            st.subheader("資料預覽")
            st.dataframe(df.head())
            
            st.subheader("選擇要預測的欄位")
            
            columns = df.columns.tolist()
            
            prediction_col = st.selectbox(
                "選擇預測欄位",
                options=columns,
                index=len(columns) - 1
            )
            
            st.markdown(
                """
                <style>
                .stButton>button {
                    width: 80%;
                    display: block;
                    margin: 0 auto;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            if st.button("開始預測"):
                with st.spinner("正在預測..."):
                    try:
                        token_manager = st.session_state.token_manager
                        
                        predictor = LoanPredictor(token_manager=token_manager)
                        
                        result_df = predictor.predict(df, prediction_col)
                        
                        # display result
                        st.subheader("預測結果")
                        st.dataframe(result_df)
                        
                        # download result   
                        csv = result_df.to_csv(index=False)
                        st.download_button(
                            label="下載預測結果",
                            data=csv,
                            file_name="loan_prediction_results.csv",
                            mime="text/csv"
                        )
                        
                    except Exception as e:
                        st.error(f"Error during predicting: {str(e)}")
                        st.info("Please try again")
                    
        except Exception as e:
            st.error(f"Error during process file: {str(e)}")
    
    # 添加自定義的聊天按鈕和聊天容器
    st.markdown(
        """
        <script>
        window.watsonAssistantChatOptions = {
        integrationID: "2ac6044d-d3f2-4885-8371-d57ed2328d21", // The ID of this integration.
        region: "wxo-us-south", // The region your integration is hosted in.
        serviceInstanceID: "9d741992-6a46-45bb-aa83-615af926e368", // The ID of your service instance.
        onLoad: async (instance) => { await instance.render(); }
        };
        setTimeout(function(){
            const t=document.createElement('script');
            t.src="https://web-chat.global.assistant.watson.appdomain.cloud/versions/" + (window.watsonAssistantChatOptions.clientVersion || 'latest') + "/WatsonAssistantChatEntry.js";
            document.head.appendChild(t);
        });
        </script>        
        """,
        unsafe_allow_html=True
    )