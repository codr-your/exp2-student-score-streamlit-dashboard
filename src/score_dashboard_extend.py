import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ===================== 数据生成、保存与读取 =====================
np.random.seed(66)
student_count = 80
names = [f"学生{i+1}" for i in range(student_count)]
chinese = np.random.randint(40, 100, size=student_count)
math = np.random.randint(35, 100, size=student_count)
english = np.random.randint(45, 98, size=student_count)
physics = np.random.randint(30, 96, size=student_count)

df_raw = pd.DataFrame({
    "姓名": names,
    "语文": chinese,
    "数学": math,
    "英语": english,
    "物理": physics
})

df_raw["总分"] = df_raw[["语文", "数学", "英语", "物理"]].sum(axis=1)
df_raw["平均分"] = round(df_raw["总分"] / 4, 2)

df_raw.to_csv("student_score.csv", index=False, encoding="utf-8-sig")
df_raw.to_excel("student_score.xlsx", index=False)

df_all = pd.read_csv("student_score.csv", encoding="utf-8-sig")
df_all = df_all.dropna()
df_all = df_all[
    (df_all["语文"] <= 100) &
    (df_all["数学"] <= 100) &
    (df_all["英语"] <= 100) &
    (df_all["物理"] <= 100)
]

def get_level(avg):
    if avg >= 85:
        return "优秀(85-100)"
    elif avg >= 70:
        return "良好(70-84)"
    elif avg >= 60:
        return "及格(60-69)"
    else:
        return "不及格(<60)"

df_all["等级"] = df_all["平均分"].apply(get_level)

# ===================== 页面配置 =====================
st.set_page_config(page_title="班级学生成绩看板【拓展版】", layout="wide")

# ===================== 主题切换：重点修复暗色文字可见性 =====================
st.sidebar.header("⚙系统设置")
theme_mode = st.sidebar.radio("页面主题模式", ["🌞亮色模式", "🌙暗色模式"])

if theme_mode == "🌙暗色模式":
    css = """
    <style>
    /* 主背景 */
    [data-testid="stMain"] {
        background-color: #262c3a;
    }

    /* 主内容文字强制浅色 */
    [data-testid="stMainBlockContainer"] {
        color: #ffffff !important;
    }

    /* 标题文字 */
    [data-testid="stMainBlockContainer"] h1,
    [data-testid="stMainBlockContainer"] h2,
    [data-testid="stMainBlockContainer"] h3 {
        color: #ffffff !important;
    }

    /* 普通段落文字 */
    [data-testid="stMainBlockContainer"] p {
        color: #e9edf5 !important;
    }

    /* metric指标文字 */
    [data-testid="stMetricLabel"] {
        color: #e9edf5 !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }

    /* 侧边栏整体深色 */
    [data-testid="stSidebar"] {
        background-color: #1e2433;
    }

    /* 侧边栏所有文字强制浅色 */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* 侧边栏标题更亮 */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    /* dataframe文字保护 */
    [data-testid="stDataFrame"] {
        color: #000000;
    }
    </style>
    """
    chart_template = "plotly_dark"

else:
    css = """
    <style>
    [data-testid="stMain"] {
        background-color: #f7f9fc;
    }

    [data-testid="stMainBlockContainer"] {
        color: #000000;
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff;
    }
    </style>
    """
    chart_template = "plotly"

st.markdown(css, unsafe_allow_html=True)

st.title("📊 班级学生成绩数据看板【拓展版｜预警+主题切换】")
st.divider()

# ===================== 侧边栏筛选 =====================
st.sidebar.header("🔍 数据筛选面板")

select_level = st.sidebar.multiselect(
    "选择成绩等级",
    options=df_all["等级"].unique(),
    default=df_all["等级"].unique()
)

min_avg, max_avg = st.sidebar.slider(
    "筛选平均分范围",
    min_value=float(df_all["平均分"].min()),
    max_value=float(df_all["平均分"].max()),
    value=(float(df_all["平均分"].min()), float(df_all["平均分"].max()))
)

df = df_all[
    (df_all["等级"].isin(select_level)) &
    (df_all["平均分"] >= min_avg) &
    (df_all["平均分"] <= max_avg)
]

st.sidebar.info(f"筛选后学生数量：{len(df)} 人")

csv_data = df.to_csv(index=False, encoding="utf-8-sig")
st.sidebar.download_button(
    label="📥导出当前筛选数据CSV",
    data=csv_data,
    file_name="filter_score.csv",
    mime="text/csv"
)

# ===================== 指标卡与仪表盘 =====================
col1, col2, col3, col4, col5 = st.columns(5)

total_stu = len(df)
avg_total = 0
max_score = 0
pass_rate = 0

if total_stu > 0:
    avg_total = round(df["平均分"].mean(), 2)
    max_score = df["总分"].max()
    pass_rate = round(len(df[df["平均分"] >= 60]) / total_stu * 100, 2)

with col1:
    st.metric(label="👥筛选后人数", value=total_stu)

with col2:
    st.metric(label="📐平均分数", value=avg_total)

with col3:
    st.metric(label="🏆最高总分", value=max_score)

with col4:
    st.metric(label="✅及格率", value=f"{pass_rate}%")

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=pass_rate,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "及格率仪表盘(%)"},
    gauge={'axis': {'range': [0, 100]}}
))
fig_gauge.update_layout(template=chart_template)
col5.plotly_chart(fig_gauge, width="stretch", theme=None)

# ===================== 预警 =====================
WARNING_THRESHOLD = 60

if total_stu > 0:
    if pass_rate < WARNING_THRESHOLD:
        st.error(f"⚠【业务预警】当前及格率 {pass_rate}%，低于阈值{WARNING_THRESHOLD}%！成绩整体水平偏低，请关注学生学习情况！")
    else:
        st.success(f"✔正常：当前及格率 {pass_rate}%，高于预警阈值{WARNING_THRESHOLD}%")
else:
    st.warning("⚠当前筛选条件没有匹配学生数据，请调整筛选条件。")

st.divider()

# ===================== 维度统计区 =====================
col_left, col_right = st.columns(2)

if total_stu > 0:
    subject_mean = pd.DataFrame({
        "科目": ["语文", "数学", "英语", "物理"],
        "平均分": [
            df["语文"].mean(),
            df["数学"].mean(),
            df["英语"].mean(),
            df["物理"].mean()
        ]
    })

    fig_bar = px.bar(
        subject_mean,
        x="科目",
        y="平均分",
        title="📈各科平均分对比",
        color="科目",
        text_auto=".1f"
    )
    fig_bar.update_layout(template=chart_template)
    col_left.plotly_chart(fig_bar, width="stretch", theme=None)

    level_cnt = df["等级"].value_counts().reset_index()
    level_cnt.columns = ["等级", "人数"]

    fig_pie = px.pie(
        level_cnt,
        values="人数",
        names="等级",
        title="🥧学生成绩等级占比",
        hole=0.3
    )
    fig_pie.update_layout(template=chart_template)
    col_right.plotly_chart(fig_pie, width="stretch", theme=None)

st.divider()

# ===================== 趋势分析区 =====================
col_a, col_b = st.columns(2)

if total_stu > 0:
    fig_hist = px.histogram(
        df,
        x="平均分",
        nbins=12,
        title="📊平均分分布直方图",
        labels={"平均分": "个人平均分"}
    )
    fig_hist.update_layout(template=chart_template)
    col_a.plotly_chart(fig_hist, width="stretch", theme=None)

    top10 = df.sort_values("总分", ascending=False).head(10)

    fig_rank = px.bar(
        top10,
        y="姓名",
        x="总分",
        orientation="h",
        title="🏅筛选范围内总分TOP10",
        color="总分"
    )
    fig_rank.update_layout(template=chart_template)
    col_b.plotly_chart(fig_rank, width="stretch", theme=None)

st.divider()

# ===================== 明细数据 =====================
st.subheader("📋筛选后的学生成绩明细")
st.dataframe(df, width="stretch", height=350)

st.info("✨拓展任务功能：1.及格率阈值预警；2.亮色/暗色主题切换；3.导出筛选后的数据集文件")
