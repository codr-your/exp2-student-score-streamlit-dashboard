"""
UI层模块
负责：主题样式切换、侧边栏数据源+筛选面板
"""
import streamlit as st
import pandas as pd
from .data_layer import generate_default_data, load_and_clean

def apply_theme(theme_mode):
    """应用亮/暗主题，返回 chart_template"""
    if theme_mode == "🌙 暗色模式":
        css = """
        <style>
        [data-testid="stMain"] { background-color: #1a1d27; }
        [data-testid="stMainBlockContainer"] { color: #e9edf5 !important; }
        [data-testid="stMainBlockContainer"] h1,
        [data-testid="stMainBlockContainer"] h2,
        [data-testid="stMainBlockContainer"] h3 { color: #ffffff !important; }
        [data-testid="stMetricLabel"] { color: #cbd5e1 !important; }
        [data-testid="stMetricValue"] { color: #ffffff !important; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
        [data-testid="stSidebar"] * { color: #f1f5f9 !important; }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 { color: #ffffff !important; }
        </style>
        """
        chart_template = "plotly_dark"
    else:
        css = """
        <style>
        [data-testid="stMain"] { background-color: #f7f9fc; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%); }
        .stMetric { background: #eef2ff; border-radius: 12px; padding: 8px; }
        </style>
        """
        chart_template = "plotly_white"
    st.markdown(css, unsafe_allow_html=True)
    return chart_template

def build_sidebar():
    """构建侧边栏，返回 (df_all, df, chart_template)"""
    st.sidebar.title("⚙ 设置中心")

    # --- 主题切换 ---
    theme_mode = st.sidebar.radio("🎨 主题模式", ["🌞 亮色模式", "🌙 暗色模式"])
    chart_template = apply_theme(theme_mode)

    # --- 数据源 ---
    st.sidebar.divider()
    st.sidebar.header("📦 数据源")
    data_source = st.sidebar.radio("选择方式", ["使用示例数据", "上传我的数据"])

    if data_source == "上传我的数据":
        uploaded_file = st.sidebar.file_uploader("上传 CSV / Excel", type=["csv", "xlsx"])
        if uploaded_file:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_raw = pd.read_csv(uploaded_file, encoding="utf-8-sig")
                else:
                    df_raw = pd.read_excel(uploaded_file)
            except Exception as e:
                st.error(f"文件读取失败：{e}")
                st.stop()
        else:
            st.sidebar.info("未上传文件，将使用示例数据")
            df_raw = generate_default_data()
    else:
        df_raw = generate_default_data()

    df_all = load_and_clean(df_raw)

    # --- 筛选面板 ---
    st.sidebar.divider()
    st.sidebar.header("🔍 多维筛选")

    select_gender = st.sidebar.multiselect(
        "性别", options=df_all["性别"].unique(), default=df_all["性别"].unique()
    )
    select_class = st.sidebar.multiselect(
        "班级", options=sorted(df_all["班级"].unique()), default=sorted(df_all["班级"].unique())
    )
    select_level = st.sidebar.multiselect(
        "成绩等级", options=df_all["等级"].unique(), default=df_all["等级"].unique()
    )
    min_avg, max_avg = st.sidebar.slider(
        "平均分范围",
        min_value=float(df_all["平均分"].min()),
        max_value=float(df_all["平均分"].max()),
        value=(float(df_all["平均分"].min()), float(df_all["平均分"].max()))
    )

    df = df_all[
        (df_all["性别"].isin(select_gender)) &
        (df_all["班级"].isin(select_class)) &
        (df_all["等级"].isin(select_level)) &
        (df_all["平均分"] >= min_avg) &
        (df_all["平均分"] <= max_avg)
    ]

    st.sidebar.success(f"✅ 筛选后：{len(df)} / 共 {len(df_all)} 人")
    return df_all, df, chart_template