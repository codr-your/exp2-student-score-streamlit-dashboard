# -*- coding: utf-8 -*-
"""
班级学生成绩数据看板 - 课程设计终极版（主入口）
架构：模块化设计 → data_layer + ui_theme + tabs
"""

import streamlit as st
import sys
import os

# 确保能找到 modules 包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.ui_theme import build_sidebar
from modules.tabs import (
    tab_overview,
    tab_analysis,
    tab_student_detail,
    tab_report
)

# 页面全局配置
st.set_page_config(
    page_title="班级学生成绩看板",
    page_icon="🎓",
    layout="wide"
)

def main():
    # 侧边栏（数据源 + 筛选 + 主题）
    df_all, df, chart_template = build_sidebar()

    # 页面标题
    st.title("🎓 班级学生成绩数据看板【课程设计终极版】")
    st.caption("基于 Streamlit + Plotly 构建 | 支持多维筛选、智能分析、报告生成、主题切换")
    st.divider()

    # Tab 切换
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 概览面板",
        "📈 多维分析",
        "👤 学生详情",
        "🤖 智能报告"
    ])

    with tab1:
        tab_overview(df, df_all, chart_template)
    with tab2:
        tab_analysis(df, chart_template)
    with tab3:
        tab_student_detail(df, df_all, chart_template)
    with tab4:
        tab_report(df, df_all)

    # 页脚
    st.divider()
    st.info(
        "💡 课程设计功能清单："
        "多维筛选 · 亮/暗主题切换 · 预警提示 · Excel导出 · "
        "箱线图/热力图/雷达图 · 学生详情 · 智能文字报告"
    )

if __name__ == "__main__":
    main()