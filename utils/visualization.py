import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

class Visualizer:
    @staticmethod
    def create_time_series(df, x_col, y_col, title="Analytics"):
        return px.line(
            df,
            x=x_col,
            y=y_col,
            title=title,
            template="plotly_white"
        )
    
    @staticmethod
    def create_distribution(df, x_col, color_col, title="Distribution"):
        return px.histogram(
            df,
            x=x_col,
            color=color_col,
            title=title,
            template="plotly_white"
        )