import streamlit as st
import plotly.graph_objects as go
from utils.data_processor import DataProcessor
import os
from dotenv import load_dotenv
from config import OpenScaleConfig

class DashboardPage:
    def __init__(self):
        load_dotenv()
        self.client = DataProcessor(
            apikey=os.getenv("API_KEY"),
            instance_id=os.getenv("INSTANCE_ID")
        )

    def render(self):
        st.title(f"Model Monitoring - {OpenScaleConfig.MODEL_NAME}")
        
        # 顯示模型資訊
        with st.expander("Model Information", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Model Details:**")
                st.write(f"• Model Name: {OpenScaleConfig.MODEL_NAME}")
                st.write(f"• Model Type: {OpenScaleConfig.MODEL_TYPE}")
                st.write(f"• Target Column: {OpenScaleConfig.TARGET_COLUMN}")
            with col2:
                st.write("**Deployment Details:**")
                st.write(f"• Deployment ID: {OpenScaleConfig.DEPLOYMENT_ID}")
                st.write(f"• Runtime Environment: {OpenScaleConfig.RUNTIME_ENV}")

        try:
            # 使用spinner顯示加載狀態
            with st.spinner("Loading metrics..."):
                quality_data = self.client.get_quality_metrics()
                fairness_data = self.client.get_fairness_metrics()
                model_metrics = self.client.get_model_metrics()

                # 顯示主要指標
                st.subheader("Key Metrics")
                col1, col2, col3 = st.columns(3)
                
                # 從回應中提取指標
                latest_quality = quality_data.get('measurements', [{}])[0] if quality_data.get('measurements') else {}
                latest_fairness = fairness_data.get('measurements', [{}])[0] if fairness_data.get('measurements') else {}
                
                with col1:
                    accuracy = latest_quality.get('metrics', {}).get('accuracy', 0)
                    st.metric("Accuracy", f"{accuracy:.2%}")
                    
                with col2:
                    f1 = latest_quality.get('metrics', {}).get('f1', 0)
                    st.metric("F1 Score", f"{f1:.2%}")
                    
                with col3:
                    fairness = latest_fairness.get('value', 0)
                    st.metric("Fairness Score", f"{fairness:.2%}")

                # 時間序列圖表
                st.subheader("Performance Over Time")
                if quality_data.get('measurements'):
                    fig = go.Figure()
                    
                    # 提取時間序列數據
                    timestamps = []
                    accuracies = []
                    f1_scores = []
                    
                    for measurement in quality_data['measurements']:
                        timestamps.append(measurement.get('timestamp'))
                        metrics = measurement.get('metrics', {})
                        accuracies.append(metrics.get('accuracy', 0))
                        f1_scores.append(metrics.get('f1', 0))
                    
                    # 添加準確率曲線
                    fig.add_trace(go.Scatter(
                        x=timestamps,
                        y=accuracies,
                        name='Accuracy',
                        line=dict(color='blue')
                    ))
                    
                    # 添加F1分數曲線
                    fig.add_trace(go.Scatter(
                        x=timestamps,
                        y=f1_scores,
                        name='F1 Score',
                        line=dict(color='red')
                    ))
                    
                    fig.update_layout(
                        title='Model Performance Metrics Over Time',
                        xaxis_title='Time',
                        yaxis_title='Score',
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No historical data available")

        except Exception as e:
            st.error(f"Error loading metrics: {str(e)}")
            st.exception(e)  # 在開發時顯示詳細錯誤信息
            
            # 顯示調試信息
            with st.expander("Debug Information"):
                st.write("Error Details:", str(e))
                st.write("OpenScale Config:", {
                    "SUBSCRIPTION_ID": OpenScaleConfig.SUBSCRIPTION_ID,
                    "DEPLOYMENT_ID": OpenScaleConfig.DEPLOYMENT_ID,
                    "SERVICE_PROVIDER_ID": OpenScaleConfig.SERVICE_PROVIDER_ID,
                    "API_VERSION": OpenScaleConfig.API_VERSION
                })