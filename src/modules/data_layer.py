"""
数据层模块
负责：模拟数据生成、数据清洗、等级划分、公共常量
"""
import pandas as pd
import numpy as np

# ============ 公共常量 ============
SUBJECTS = ["语文", "数学", "英语", "物理"]

COLOR_MAP = {
    "优秀(85-100)": "#10b981",
    "良好(70-84)": "#3b82f6",
    "及格(60-69)": "#f59e0b",
    "不及格(<60)": "#ef4444"
}

# ============ 函数 ============
def generate_default_data():
    """生成带性别、班级字段的模拟数据"""
    np.random.seed(66)
    student_count = 90
    names = [f"学生{i+1}" for i in range(student_count)]
    genders = np.random.choice(["男", "女"], size=student_count)
    classes = np.random.choice(["1班", "2班", "3班"], size=student_count, p=[0.34, 0.33, 0.33])

    df_raw = pd.DataFrame({
        "姓名": names,
        "性别": genders,
        "班级": classes,
        "语文": np.random.randint(40, 100, size=student_count),
        "数学": np.random.randint(35, 100, size=student_count),
        "英语": np.random.randint(45, 98, size=student_count),
        "物理": np.random.randint(30, 96, size=student_count)
    })
    df_raw["总分"] = df_raw[SUBJECTS].sum(axis=1)
    df_raw["平均分"] = round(df_raw["总分"] / len(SUBJECTS), 2)
    return df_raw

def get_level(avg):
    """成绩等级划分"""
    if avg >= 85:
        return "优秀(85-100)"
    elif avg >= 70:
        return "良好(70-84)"
    elif avg >= 60:
        return "及格(60-69)"
    else:
        return "不及格(<60)"

def load_and_clean(df_raw):
    """数据清洗 + 派生字段"""
    df = df_raw.dropna()
    for col in SUBJECTS:
        if col in df.columns:
            df = df[(df[col] <= 100) & (df[col] >= 0)]
    if "总分" not in df.columns:
        df["总分"] = df[SUBJECTS].sum(axis=1)
    if "平均分" not in df.columns:
        df["平均分"] = round(df["总分"] / len(SUBJECTS), 2)
    df["等级"] = df["平均分"].apply(get_level)
    for col in ["性别", "班级"]:
        if col not in df.columns:
            df[col] = "未填写"
    return df