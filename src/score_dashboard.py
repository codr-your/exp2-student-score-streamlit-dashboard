import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ===================== 任务2：数据生成、保存为CSV/Excel、读取数据集 =====================
np.random.seed(66)  # 固定随机种子，每次运行数据不变
student_count = 80
names = [f"学生{i+1}" for i in range(student_count)]
chinese = np.random.randint(40, 100, size=student_count)
math = np.random.randint(35, 100, size=student_count)
english = np.random.randint(45, 98, size=student_count)
physics = np.random.randint(30, 96, size=student_count)

# 构造原始DataFrame
df_raw = pd.DataFrame({
    "姓名": names,
    "语文": chinese,
    "数学": math,
    "英语": english,
    "物理": physics
})

# 计算总分、平均分
df_raw["总分"] = df_raw[["语文", "数学", "英语", "物理"]].sum(axis=1)
df_raw["平均分"] = round(df_raw["总分"] / 4, 2)

# 保存数据集到本地文件（实验要求保存CSV/Excel）
df_raw.to_csv("student_score.csv", index=False, encoding="utf-8-sig")
df_raw.to_excel("student_score.xlsx", index=False)

# 从CSV文件读取数据（模拟真实读取外部数据集流程）
df = pd.read_csv("student_score.csv", encoding="utf-8-sig")

# -------- 数据预处理：清洗，本模拟数据无空值异常，这里写处理流程演示 --------
# 去除空值
df = df.dropna()
# 过滤异常分数（0~100）
df = df[(df["语文"] <= 100) & (df["数学"] <= 100) & (df["英语"] <= 100) & (df["物理"] <= 100)]

# 增加成绩等级字段
def get_level(avg):
    if avg >= 85:
        return "优秀(85-100)"
    elif avg >= 70:
        return "良好(70‑84)"
    elif avg >= 60:
        return "及格(60‑69)"
    else:
        return "不及格(<60)"

df["等级"] = df["平均分"].apply(get_level)

# ===================== 任务1：页面布局、配色设计 =====================
st.set_page_config(page_title="班级学生成绩看板", layout="wide")

# 自定义页面样式
st.markdown("""
<style>
.main {
    background-color:#f7f9fc;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 班级学生成绩数据看板")
st.divider()

# ===================== 任务3：【数据概览区】数据卡片展示核心指标 =====================
col1, col2, col3, col4 = st.columns(4)
total_stu = len(df)
avg_total = round(df["平均分"].mean(), 2)
max_score = df["总分"].max()
pass_rate = round(len(df[df["平均分"] >= 60]) / total_stu * 100, 2)

with col1:
    st.metric(label="👥班级总人数", value=total_stu)
with col2:
    st.metric(label="📐全班平均分数", value=avg_total)
with col3:
    st.metric(label="🏆最高总分", value=max_score)
with col4:
    st.metric(label="✅及格率(>=60分)", value=f"{pass_rate}%")

st.divider()

# =====================【维度统计区】柱状图、环形饼图 =====================
col_left, col_right = st.columns(2)

# 各科平均分柱状图
subject_mean = pd.DataFrame({
    "科目": ["语文", "数学", "英语", "物理"],
    "平均分": [df["语文"].mean(), df["数学"].mean(), df["英语"].mean(), df["物理"].mean()]
})
fig_bar = px.bar(subject_mean, x="科目", y="平均分", title="📈各科平均分对比", color="科目", text_auto=".1f")
col_left.plotly_chart(fig_bar, width="stretch")

# 成绩等级环形饼图
level_cnt = df["等级"].value_counts().reset_index()
level_cnt.columns = ["等级", "人数"]
fig_pie = px.pie(level_cnt, values="人数", names="等级", title="🥧学生成绩等级占比", hole=0.3)
col_right.plotly_chart(fig_pie, width="stretch")

st.divider()

# =====================【趋势分析区】分布直方图、总分TOP10排行榜 =====================
col_a, col_b = st.columns(2)

# 平均分分布直方图
fig_hist = px.histogram(df, x="平均分", nbins=12, title="📊学生平均分分布", labels={"平均分": "个人平均分"})
col_a.plotly_chart(fig_hist, width="stretch")

# 总分TOP10横向条形图
top10 = df.sort_values("总分", ascending=False).head(10)
fig_rank = px.bar(top10, y="姓名", x="总分", orientation="h", title="🏅总分TOP10学生", color="总分")
col_b.plotly_chart(fig_rank, width="stretch")

st.divider()

# =====================【明细数据区】原始数据表 =====================
st.subheader("📋学生成绩明细数据")
st.dataframe(df, width="stretch", height=350)

# 提示信息
st.info("💡本地已生成 student_score.csv 与 student_score.xlsx 数据集文件")
