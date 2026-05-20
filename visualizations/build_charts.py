from __future__ import annotations

import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from config.settings import settings


def get_connection() -> mysql.connector.MySQLConnection:
    return mysql.connector.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_database,
    )


def main() -> None:
    query = """
    SELECT
        year_of_study,
        student_count,
        anxiety_prevalence_pct,
        depression_prevalence_pct,
        panic_attack_prevalence_pct,
        treatment_uptake_pct
    FROM agg_yearly_mental_health
    ORDER BY year_of_study
    """

    cnx = get_connection()
    try:
        df = pd.read_sql(query, cnx)
    finally:
        cnx.close()

    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(11, 6))
    plt.plot(df["year_of_study"], df["anxiety_prevalence_pct"], marker="o", label="Anxiety %")
    plt.plot(df["year_of_study"], df["depression_prevalence_pct"], marker="o", label="Depression %")
    plt.plot(df["year_of_study"], df["panic_attack_prevalence_pct"], marker="o", label="Panic Attack %")
    plt.title("Mental Health Prevalence by Year of Study")
    plt.xlabel("Year of Study")
    plt.ylabel("Prevalence (%)")
    plt.legend()

    for _, row in df.iterrows():
        plt.annotate(f"n={int(row['student_count'])}", (row["year_of_study"], row["anxiety_prevalence_pct"]), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8)

    plt.tight_layout()
    plt.savefig("visualizations/mental_health_prevalence_by_year.png", dpi=150)

    plt.figure(figsize=(11, 6))
    sns.heatmap(
        df[["anxiety_prevalence_pct", "depression_prevalence_pct", "panic_attack_prevalence_pct", "treatment_uptake_pct"]].T,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",
        cbar_kws={"label": "Percent"},
    )
    plt.yticks(rotation=0)
    plt.title("KPI Heatmap by Metric")
    plt.tight_layout()
    plt.savefig("visualizations/kpi_heatmap.png", dpi=150)


if __name__ == "__main__":
    main()