import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ===================== 任务2：数据生成、保存为CSV/Excel、读取数据集 =====================
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
df_all = df_all[(df_all["语文"] <= 100) & (df_all["数学"] <= 100) & (df_all["英语"] <= 100) & (df_all["物理"] <= 100)]

def get_level(avg):
    if avg >= 85:
        return "优秀(85-100)"
    elif avg >= 70:
        return "良好(70‑84)"
    elif avg >= 60:
        return "及格(60‑69)"
    else:
        return "不及格(<60)"

df_all["等级"] = df_all["平均分"].apply(get_level)

# ===================== 页面全局配置 =====================
st.set_page_config(page_title="班级学生成绩看板【进阶版】", layout="wide")
st.markdown("""
<style>
.main {
    background-color:#f7f9fc;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 班级学生成绩数据看板【进阶交互版】")
st.divider()

# ===================== 【进阶2：侧边栏筛选功能】 =====================
st.sidebar.header("🔍 数据筛选面板")
# 等级下拉筛选
select_level = st.sidebar.multiselect(
    "选择成绩等级",
    options=df_all["等级"].unique(),
    default=df_all["等级"].unique()
)
# 平均分滑块筛选
min_avg, max_avg = st.sidebar.slider(
    "筛选平均分范围",
    min_value=float(df_all["平均分"].min()),
    max_value=float(df_all["平均分"].max()),
    value=(float(df_all["平均分"].min()), float(df_all["平均分"].max()))
)

# 根据筛选条件过滤数据（所有图表共用一份过滤后的数据，实现图表联动更新）
df = df_all[
    (df_all["等级"].isin(select_level)) &
    (df_all["平均分"] >= min_avg) &
    (df_all["平均分"] <= max_avg)
]

st.sidebar.info(f"筛选后学生数量：{len(df)} 人")

# ===================== 【数据概览区】数据卡片 +【进阶3：仪表盘】 =====================
col1, col2, col3, col4, col5 = st.columns(5)
total_stu = len(df)
if total_stu > 0:
    avg_total = round(df["平均分"].mean(), 2)
    max_score = df["总分"].max()
    pass_rate = round(len(df[df["平均分"] >= 60]) / total_stu *100,2)
else:
    avg_total = 0
    max_score = 0
    pass_rate = 0

with col1:
    st.metric(label="👥筛选后人数", value=total_stu)
with col2:
    st.metric(label="📐平均分数", value=avg_total)
with col3:
    st.metric(label="🏆最高总分", value=max_score)
with col4:
    st.metric(label="✅及格率", value=f"{pass_rate}%")

# 进阶3：进度仪表盘，展示及格率
fig_gauge = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = pass_rate,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "及格率仪表盘(%)"},
    gauge = {'axis': {'range': [0, 100]}}
))
col5.plotly_chart(fig_gauge, width="stretch")

st.divider()

# =====================【维度统计区】柱状图、环形饼图（筛选联动，自带hover提示【进阶1】） =====================
col_left, col_right = st.columns(2)

if total_stu >0:
    subject_mean = pd.DataFrame({
        "科目":["语文","数学","英语","物理"],
        "平均分":[df["语文"].mean(),df["数学"].mean(),df["英语"].mean(),df["物理"].mean()]
    })
    fig_bar = px.bar(subject_mean, x="科目", y="平均分", title="📈各科平均分对比", color="科目", text_auto=".1f")
    col_left.plotly_chart(fig_bar, width="stretch")

    level_cnt = df["等级"].value_counts().reset_index()
    level_cnt.columns=["等级","人数"]
    fig_pie = px.pie(level_cnt, values="人数", names="等级", title="🥧学生成绩等级占比", hole=0.3)
    col_right.plotly_chart(fig_pie, width="stretch")
else:
    col_left.warning("当前筛选条件无数据，请修改侧边筛选条件！")

st.divider()

# =====================【趋势分析区】直方图、TOP排行榜【进阶3排行榜】 =====================
col_a, col_b = st.columns(2)
if total_stu>0:
    fig_hist = px.histogram(df, x="平均分", nbins=12, title="📊平均分分布直方图",labels={"平均分":"个人平均分"})
    col_a.plotly_chart(fig_hist, width="stretch")

    top10 = df.sort_values("总分",ascending=False).head(10)
    fig_rank = px.bar(top10,y="姓名",x="总分",orientation="h",title="🏅筛选范围内总分TOP10",color="总分")
    col_b.plotly_chart(fig_rank, width="stretch")
else:
    col_a.warning("无匹配数据")

st.divider()

# =====================【明细数据区】 =====================
st.subheader("📋筛选后的学生成绩明细")
st.dataframe(df, width="stretch", height=350)

st.info("💡进阶功能说明：侧边栏修改筛选条件，页面全部图表、指标、表格自动联动刷新；Plotly图表鼠标悬浮自带hover提示；增加及格率仪表盘组件")
