import streamlit as st
import pandas as pd

def styled_table(df: pd.DataFrame):
    st.dataframe(
        df,
        use_container_width=True,
        height=400
    )


def ranking_table(df, coluna_score="score"):
    df = df.sort_values(by=coluna_score, ascending=False)
    st.dataframe(df, use_container_width=True)