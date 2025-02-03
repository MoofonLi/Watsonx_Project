import streamlit as st
from utils.data_processor import DataProcessor
from utils.visualization import Visualizer
class DashboardPage:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.visualizer = Visualizer()
        self.data = self.data_processor.load_data()
    def render(self):
        st.title("Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_time_series()
        
        with col2:
            self._render_distribution()
        
        self._render_data_table()
    def _render_time_series(self):
        fig = self.visualizer.create_time_series(
            self.data, 'date', 'value'
        )
        st.plotly_chart(fig, use_container_width=True)
    def _render_distribution(self):
        fig = self.visualizer.create_distribution(
            self.data, 'value', 'category'
        )
        st.plotly_chart(fig, use_container_width=True)
    def _render_data_table(self):
        with st.expander("Origin Data"):
            st.dataframe(self.data)
