import streamlit as st
import pandas as pd
from utils.prediction import LoanPredictor
import io

def prediction_page():
    st.title("預測頁面")
    
    # 檢查令牌管理器是否已初始化
    if 'token_manager' not in st.session_state:
        st.error("令牌管理器未初始化，請重新啟動應用程式")
        return
    
    # 上傳檔案部分
    uploaded_file = st.file_uploader("上傳預測資料檔案 (CSV)", type=["csv"])
    
    if uploaded_file is not None:
        try:
            # 讀取上傳的CSV檔案
            df = pd.read_csv(uploaded_file)
            
            # 顯示資料預覽
            st.subheader("資料預覽")
            st.dataframe(df.head())
            
            # 選擇要預測的欄位
            st.subheader("選擇要預測的欄位")
            
            # 從資料框獲取列名
            columns = df.columns.tolist()
            
            # 使用者選擇要預測的欄位 (單選)
            prediction_col = st.selectbox(
                "選擇預測欄位",
                options=columns
            )
            

            st.markdown(
                """
                <style>
                .stButton>button {
                    width: 80%; /* 調整按鈕寬度 */
                    display: block;
                    margin: 0 auto; /* 讓按鈕置中 */
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            # 預測按鈕
            if st.button("開始預測"):
                with st.spinner("正在處理預測..."):
                    try:
                        # 從 session_state 獲取令牌管理器
                        token_manager = st.session_state.token_manager
                        
                        # 創建預測器實例並傳入令牌管理器
                        predictor = LoanPredictor(token_manager=token_manager)
                        
                        # 進行預測，只傳入選定的欄位
                        result_df = predictor.predict(df, prediction_col)
                        
                        # 顯示預測結果
                        st.subheader("預測結果")
                        st.dataframe(result_df)
                        
                        # 提供下載功能
                        csv = result_df.to_csv(index=False)
                        st.download_button(
                            label="下載預測結果",
                            data=csv,
                            file_name="loan_prediction_results.csv",
                            mime="text/csv"
                        )
                        
                    except Exception as e:
                        st.error(f"預測過程中發生錯誤: {str(e)}")
                        st.info("請檢查 API 連接設定和預測環境")
                    
        except Exception as e:
            st.error(f"處理檔案時發生錯誤: {str(e)}")