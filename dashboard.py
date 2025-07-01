# dashboard.py
import sqlite3
import pandas as pd
import streamlit as st
import altair as alt
from pathlib import Path

DB_PATH = Path("data/stats.db")

st.set_page_config(page_title="Smart-Mail-Agent Dashboard", layout="wide")
st.title("Smart-Mail-Agent  處理統計")

if not DB_PATH.exists():
    st.warning("尚未產生統計資料，請先執行一些郵件流程。")
    st.stop()

@st.cache_data
def load_stats(path: Path) -> pd.DataFrame:
    conn = sqlite3.connect(path)
    df = pd.read_sql_query(
        """
        SELECT dt AS 日期,
               label AS 分類,
               count AS 次數,
               ROUND(total_sec, 2) AS 總耗時秒
        FROM daily_stats
        ORDER BY dt DESC, 分類
        """,
        conn,
    )
    conn.close()
    return df

df = load_stats(DB_PATH)

# 整體總覽
st.subheader("每日處理量")
daily = df.groupby("日期", as_index=False)["次數"].sum()
bar = (
    alt.Chart(daily)
    .mark_bar()
    .encode(x="日期:T", y="次數:Q", tooltip=["日期", "次數"])
    .properties(height=300)
)
st.altair_chart(bar, use_container_width=True)

# 各分類分佈
st.subheader("分類佔比（最近一天）")
latest_date = df["日期"].max()
latest_df = df[df["日期"] == latest_date]
pie = (
    alt.Chart(latest_df)
    .mark_arc()
    .encode(theta="次數", color="分類", tooltip=["分類", "次數"])
)
st.altair_chart(pie, use_container_width=True)

# 明細
st.subheader("明細資料")
st.dataframe(df, use_container_width=True)
