import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import io

# ===================== 任务2：数据生成、保存为CSV/Excel、读取数据集 =====================
@st.cache_data
def generate_data():
    """生成示例数据"""
    np.random.seed(66)
    student_count = 80
    names = [f"学生{i+1}" for i in range(student_count)]
    df_raw = pd.DataFrame({
        "姓名": names,
        "语文": np.random.randint(40, 100, size=student_count),
        "数学": np.random.randint(35, 100, size=student_count),
        "英语": np.random.randint(45, 98, size=student_count),
        "物理": np.random.randint(30, 96, size=student_count)
    })
    return df_raw


def get_level(avg):
    if avg >= 85:
        return "优秀(85-100)"
    elif avg >= 70:
        return "良好(70-84)"
    elif avg >= 60:
        return "及格(60-69)"
    else:
        return "不及格(<60)"


def load_and_clean(df_raw):
    """【兼容文本脏数据，转NaN，不再直接dropna】计算总分平均分等级"""
    df = df_raw.copy()
    subjects = ["语文", "数学", "英语", "物理"]
    for col in subjects:
        if col in df.columns:
            # 字符串转为NaN
            df[col] = pd.to_numeric(df[col], errors="coerce")
            # 超出0-100也置NaN
            df.loc[(df[col] < 0) | (df[col] > 100), col] = np.nan
    # 按科目求和，自动跳过NaN
    df["总分"] = df[subjects].sum(axis=1)
    # 有效科目数量，防止全部为空时分母为0
    valid_cnt = df[subjects].notna().sum(axis=1)
    df["平均分"] = np.where(valid_cnt > 0, round(df["总分"] / valid_cnt, 2), np.nan)
    df["等级"] = df["平均分"].apply(lambda x: get_level(x) if pd.notna(x) else "无效成绩")
    return df


# ---------- 功能1：侧边栏数据源切换 ----------
st.sidebar.header("📦 数据源")
data_source = st.sidebar.radio("选择数据来源", ["使用示例数据", "上传我的CSV/Excel"])

if data_source == "上传我的CSV/Excel":
    uploaded_file = st.sidebar.file_uploader("上传文件", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_raw = pd.read_csv(uploaded_file, encoding="utf-8-sig")
            else:
                df_raw = pd.read_excel(uploaded_file)
            st.sidebar.success(f"✅ 已读取 {len(df_raw)} 条数据")
        except Exception as e:
            st.error(f"文件读取失败：{e}")
            st.stop()
    else:
        st.sidebar.info("未上传文件，将使用示例数据")
        df_raw = generate_data()
else:
    df_raw = generate_data()

# 保存到本地
df_raw.to_csv("student_score.csv", index=False, encoding="utf-8-sig")
df_raw.to_excel("student_score.xlsx", index=False)

# 清洗
df_all = load_and_clean(df_raw)

# ---------- 功能2：简单等级筛选 ----------
st.sidebar.divider()
st.sidebar.header("🔍 等级筛选")
select_level = st.sidebar.multiselect(
    "选择要展示的成绩等级",
    options=df_all["等级"].unique(),
    default=df_all["等级"].unique()
)
df = df_all[df_all["等级"].isin(select_level)]
st.sidebar.info(f"筛选后：{len(df)} 人 / 共 {len(df_all)} 人")

# ===================== 任务1：页面布局、配色设计 =====================
st.set_page_config(page_title="班级学生成绩看板", layout="wide")

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

if total_stu > 0:
    avg_total = round(df["平均分"].mean(), 2)
    max_score = df["总分"].max()
    pass_rate = round(len(df[df["平均分"] >= 60]) / total_stu * 100, 2)
else:
    avg_total, max_score, pass_rate = 0, 0, 0

with col1:
    st.metric(label="👥筛选后人数", value=total_stu)
with col2:
    st.metric(label="📐全班平均分数", value=avg_total)
with col3:
    st.metric(label="🏆最高总分", value=max_score)
with col4:
    st.metric(label="✅及格率(>=60分)", value=f"{pass_rate}%")

if total_stu == 0:
    st.warning("⚠️ 当前筛选条件无数据，请修改侧边栏筛选条件！")
    st.stop()

st.divider()

# =====================【维度统计区】柱状图、环形饼图 =====================
col_left, col_right = st.columns(2)

subject_mean = pd.DataFrame({
    "科目": ["语文", "数学", "英语", "物理"],
    "平均分": [df["语文"].mean(), df["数学"].mean(), df["英语"].mean(), df["物理"].mean()]
})
fig_bar = px.bar(subject_mean, x="科目", y="平均分", title="📈各科平均分对比", color="科目", text_auto=".1f")
col_left.plotly_chart(fig_bar, width="stretch")

level_cnt = df["等级"].value_counts().reset_index()
level_cnt.columns = ["等级", "人数"]
fig_pie = px.pie(level_cnt, values="人数", names="等级", title="🥧学生成绩等级占比", hole=0.3)
col_right.plotly_chart(fig_pie, width="stretch")

st.divider()

# =====================【趋势分析区】分布直方图、总分TOP10排行榜 =====================
col_a, col_b = st.columns(2)

fig_hist = px.histogram(df, x="平均分", nbins=12, title="📊学生平均分分布", labels={"平均分": "个人平均分"})
col_a.plotly_chart(fig_hist, width="stretch")

top10 = df.sort_values("总分", ascending=False).head(10)
fig_rank = px.bar(top10, y="姓名", x="总分", orientation="h", title="🏅总分TOP10学生", color="总分")
col_b.plotly_chart(fig_rank, width="stretch")

st.divider()

# =====================【明细数据区】原始数据表 + 下载 =====================
dl_col1, dl_col2 = st.columns([3, 1])
dl_col1.subheader("📋学生成绩明细数据")

# 功能2：下载筛选后的数据
output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="成绩明细")
dl_col2.download_button(
    label="📥 导出Excel",
    data=output.getvalue(),
    file_name="student_score_export.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

st.dataframe(df, width="stretch", height=350)

st.info("💡 新增功能：上传自定义数据 · 按等级筛选 · 一键导出Excel")