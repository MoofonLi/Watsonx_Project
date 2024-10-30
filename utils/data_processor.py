import pandas as pd
import numpy as np
from typing import Union, List, Dict
import streamlit as st

class DataProcessor:
    @staticmethod
    @st.cache_data
    def load_data(file_path: str = None) -> pd.DataFrame:
        """Load Data"""
        if file_path:
            return pd.read_csv(file_path)
        # 示例數據
        return pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=100),
            'value': np.random.normal(100, 15, 100),
            'category': np.random.choice(['A', 'B', 'C'], 100)
        })
    
    @staticmethod
    def process_time_series(df: pd.DataFrame, 
                          value_column: str,
                          date_column: str) -> pd.DataFrame:
        """Data Process"""
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        return df.sort_values(date_column)