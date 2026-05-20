from __future__ import annotations

import mysql.connector
import pandas as pd
import plotly.express as px
import streamlit as st

from config.settings import settings


@st.cache_data(ttl=300)
def load_kpis() -> pd.DataFrame:
    cnx = mysql.connector.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_database,
    )
    try:
        return pd.read_sql(
            "SELECT * FROM agg_yearly_mental_health ORDER BY year_of_study", cnx
        )
    finally:
        cnx.close()


def main() -> None:
    st.set_page_config(page_title="Student Mental Health Dashboard", layout="wide")
    st.title("Student Mental Health Analytics")

    df = load_kpis()
    if df.empty:
        st.warning("No data available. Run ETL and analytics refresh first.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg Anxiety %", f"{df['anxiety_prevalence_pct'].mean():.1f}")
    c2.metric("Avg Depression %", f"{df['depression_prevalence_pct'].mean():.1f}")
    c3.metric("Avg Panic Attack %", f"{df['panic_attack_prevalence_pct'].mean():.1f}")
    c4.metric("Avg Treatment Uptake %", f"{df['treatment_uptake_pct'].mean():.1f}")

    fig = px.line(
        df,
        x="year_of_study",
        y=["anxiety_prevalence_pct", "depression_prevalence_pct", "panic_attack_prevalence_pct"],
        markers=True,
        title="Mental Health Trends by Year of Study",
    )
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()