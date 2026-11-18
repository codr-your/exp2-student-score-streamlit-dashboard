"""
页面层模块
负责：四个 Tab 的渲染函数
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

from .data_layer import SUBJECTS, COLOR_MAP

# ===================== Tab1：概览面板 =====================
def tab_overview(df, df_all, chart_template):
    """数据概览 + 基础图表 + 预警 + 下载"""
    total_stu = len(df)

    # --- 指标卡 ---
    c1, c2, c3, c4, c5 = st.columns(5)
    if total_stu > 0:
        avg_total = round(df["平均分"].mean(), 2)
        max_score = int(df["总分"].max())
        min_score = int(df["总分"].min())
        pass_rate = round(len(df[df["平均分"] >= 60]) / total_stu * 100, 2)
    else:
        avg_total, max_score, min_score, pass_rate = 0, 0, 0, 0

    c1.metric("👥 筛选后人数", f"{total_stu}", f"占比 {round(total_stu / max(len(df_all), 1) * 100, 1)}%")
    c2.metric("📐 平均分", f"{avg_total}")
    c3.metric("🏆 最高总分", f"{max_score}", f"最低 {min_score}")
    c4.metric("✅ 及格率", f"{pass_rate}%")

    # 仪表盘
    gauge_color = "#10b981" if pass_rate >= 60 else "#ef4444"
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pass_rate,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "及格率(%)", 'font': {'size': 14}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': gauge_color},
            'steps': [
                {'range': [0, 60], 'color': "#fee2e2"},
                {'range': [60, 80], 'color': "#fef3c7"},
                {'range': [80, 100], 'color': "#d1fae5"}
            ],
            'threshold': {'line': {'color': '#0ea5e9', 'width': 3}, 'value': 80}
        }
    ))
    fig_gauge.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10), template=chart_template)
    c5.plotly_chart(fig_gauge, width="stretch")

    # --- 预警 ---
    st.divider()
    if total_stu == 0:
        st.warning("⚠️ 当前筛选条件无数据，请修改侧边栏筛选条件！")
        return

    if pass_rate < 60:
        st.error(f"🚨 预警：及格率 {pass_rate}% 低于阈值 60%！")
    elif pass_rate < 80:
        st.warning(f"⚠️ 注意：及格率 {pass_rate}%，建议加强辅导。")
    else:
        st.success(f"✅ 及格率 {pass_rate}%，表现良好！")

    st.divider()

    # --- 柱状图 + 饼图 ---
    col_left, col_right = st.columns(2)

    subject_mean = pd.DataFrame({
        "科目": SUBJECTS,
        "平均分": [df[s].mean() for s in SUBJECTS]
    })
    fig_bar = px.bar(subject_mean, x="科目", y="平均分", title="📈 各科平均分对比",
                     color="科目", text_auto=".1f", height=380)
    fig_bar.update_layout(showlegend=False, template=chart_template)
    col_left.plotly_chart(fig_bar, width="stretch", theme=None)

    level_cnt = df["等级"].value_counts().reset_index()
    level_cnt.columns = ["等级", "人数"]
    fig_pie = px.pie(level_cnt, values="人数", names="等级",
                     title="🥧 成绩等级占比", hole=0.4,
                     color="等级", color_discrete_map=COLOR_MAP, height=380)
    fig_pie.update_traces(textinfo="label+percent+value")
    fig_pie.update_layout(template=chart_template)
    col_right.plotly_chart(fig_pie, width="stretch", theme=None)

    # --- 直方图 + TOP10 ---
    col_a, col_b = st.columns(2)

    fig_hist = px.histogram(df, x="平均分", nbins=12, title="📊 平均分分布直方图",
                            color="等级", color_discrete_map=COLOR_MAP, height=380)
    fig_hist.update_layout(bargap=0.05, template=chart_template)
    col_a.plotly_chart(fig_hist, width="stretch", theme=None)

    top10 = df.sort_values("总分", ascending=False).head(10)
    fig_rank = px.bar(top10, y="姓名", x="总分", orientation="h",
                      title="🏅 总分 TOP 10", color="总分", height=380,
                      color_continuous_scale="Viridis")
    fig_rank.update_layout(template=chart_template)
    col_b.plotly_chart(fig_rank, width="stretch", theme=None)

    # --- 箱线图 + 班级堆叠柱 ---
    col_box, col_stack = st.columns(2)

    fig_box = go.Figure()
    for s in SUBJECTS:
        fig_box.add_trace(go.Box(y=df[s], name=s, marker_color="#6366f1"))
    fig_box.update_layout(title="📦 各科成绩分布箱线图", height=380,
                          yaxis_title="分数", showlegend=False, template=chart_template)
    col_box.plotly_chart(fig_box, width="stretch", theme=None)

    class_subj = df.groupby("班级")[SUBJECTS].mean().reset_index()
    class_melt = class_subj.melt(id_vars="班级", value_vars=SUBJECTS,
                                 var_name="科目", value_name="平均分")
    fig_stack = px.bar(class_melt, x="班级", y="平均分", color="科目",
                       barmode="group", title="🏫 各班各科平均分对比", height=380)
    fig_stack.update_layout(template=chart_template)
    col_stack.plotly_chart(fig_stack, width="stretch", theme=None)

    # --- 明细 + 下载 ---
    st.divider()
    dl_col1, dl_col2 = st.columns([3, 1])
    dl_col1.subheader("📋 筛选后的学生成绩明细")

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="筛选结果")
    dl_col2.download_button(
        label="📥 导出 Excel",
        data=output.getvalue(),
        file_name="student_score_filtered.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch"
    )
    st.dataframe(df, width="stretch", height=380, hide_index=True)

# ===================== Tab2：多维分析 =====================
def tab_analysis(df, chart_template):
    """相关性热力图 + 散点矩阵 + 雷达图 + 性别对比"""
    if len(df) <= 1:
        st.warning("⚠️ 数据量不足，无法进行多维分析")
        return

    # 相关性热力图
    st.subheader("🔥 科目相关性热力图")
    corr = df[SUBJECTS].corr()
    fig_heat = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                         zmin=-1, zmax=1, title="各科目 Pearson 相关系数", height=450)
    fig_heat.update_layout(template=chart_template)
    st.plotly_chart(fig_heat, width="stretch", theme=None)

    # 散点图矩阵
    st.subheader("🌐 散点图矩阵（科目两两关系）")
    fig_scatter = px.scatter_matrix(df, dimensions=SUBJECTS, color="等级",
                                    color_discrete_map=COLOR_MAP,
                                    hover_data=["姓名", "班级"], height=600)
    fig_scatter.update_layout(template=chart_template)
    st.plotly_chart(fig_scatter, width="stretch", theme=None)

    # 雷达图：班级能力对比
    st.subheader("📡 各班平均能力雷达图")
    class_avg = df.groupby("班级")[SUBJECTS].mean()
    fig_radar = go.Figure()
    for cls in sorted(df["班级"].unique()):
        if cls in class_avg.index:
            vals = class_avg.loc[cls].tolist()
            fig_radar.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=SUBJECTS + [SUBJECTS[0]],
                fill="toself", name=cls, opacity=0.6
            ))
    fig_radar.update_layout(
        height=500, template=chart_template,
        polar=dict(radialaxis=dict(visible=True, range=[0, 100]))
    )
    st.plotly_chart(fig_radar, use_container_width=True, theme=None)

    # 性别对比
    st.subheader("👫 性别维度对比")
    gender_mean = df.groupby("性别")[SUBJECTS].mean().reset_index()
    fig_gender = go.Figure()
    for _, row in gender_mean.iterrows():
        fig_gender.add_trace(go.Bar(name=row["性别"], x=SUBJECTS,
                                     y=[row[s] for s in SUBJECTS]))
    fig_gender.update_layout(barmode="group", title="男女生各科平均分对比",
                              height=400, template=chart_template)
    st.plotly_chart(fig_gender, use_container_width=True, theme=None)

# ===================== Tab3：学生详情 =====================
def tab_student_detail(df, df_all, chart_template):
    """学生个人详情 + 雷达图 + 群体定位"""
    st.subheader("🔎 学生个人详情查询")

    stu_options = df["姓名"].tolist()
    if not stu_options:
        st.warning("⚠️ 当前筛选条件无学生，请调整筛选条件")
        return

    sel_stu = st.selectbox("选择学生", stu_options)
    stu = df[df["姓名"] == sel_stu].iloc[0]

    # 基本信息
    info_col = st.columns(4)
    info_col[0].metric("姓名", stu["姓名"])
    info_col[1].metric("性别", stu["性别"])
    info_col[2].metric("班级", stu["班级"])
    info_col[3].metric("等级", stu["等级"])

    st.divider()

    # 雷达图 + 各科详情
    radar_col, detail_col = st.columns(2)

    class_mean = df_all[df_all["班级"] == stu["班级"]][SUBJECTS].mean()
    fig_my_radar = go.Figure()
    fig_my_radar.add_trace(go.Scatterpolar(
        r=[stu[s] for s in SUBJECTS] + [stu[SUBJECTS[0]]],
        theta=SUBJECTS + [SUBJECTS[0]],
        fill="toself", name=f"{stu['姓名']}", line=dict(color="#6366f1")
    ))
    fig_my_radar.add_trace(go.Scatterpolar(
        r=class_mean.tolist() + [class_mean.tolist()[0]],
        theta=SUBJECTS + [SUBJECTS[0]],
        fill="toself", name=f"{stu['班级']}平均",
        line=dict(color="#f59e0b"), opacity=0.5
    ))
    fig_my_radar.update_layout(
        height=450, title="个人能力 vs 班级平均", template=chart_template,
        polar=dict(radialaxis=dict(visible=True, range=[0, 100]))
    )
    radar_col.plotly_chart(fig_my_radar, use_container_width=True, theme=None)

    detail_col.markdown("### 📚 各科成绩详情")
    overall_mean = df_all[SUBJECTS].mean()
    for s in SUBJECTS:
        score = stu[s]
        cm = overall_mean[s]
        diff = score - cm
        icon = "⬆️" if diff > 0 else ("⬇️" if diff < 0 else "➡️")
        color = "🟢" if score >= 85 else ("🟡" if score >= 60 else "🔴")
        detail_col.markdown(
            f"{color} **{s}**：`{score}` 分  {icon} 对比全校均值 `{cm:.1f}`（{diff:+.1f}）"
        )
    detail_col.markdown(f"**总分：`{stu['总分']}` | 平均分：`{stu['平均分']}`**")

    # 群体定位直方图
    st.divider()
    st.markdown("### 📍 该生在筛选群体中的位置")
    fig_pos = px.histogram(df, x="平均分", nbins=12,
                           title="平均分分布 + 该生位置", height=350)
    fig_pos.add_vline(x=stu["平均分"], line_dash="dash", line_color="red",
                      annotation_text=f"{stu['姓名']}：{stu['平均分']}")
    fig_pos.update_layout(template=chart_template)
    st.plotly_chart(fig_pos, use_container_width=True, theme=None)

# ===================== Tab4：智能报告 =====================
def tab_report(df, df_all):
    """自动生成文字分析报告"""
    st.subheader("🤖 自动生成数据分析报告")

    total_stu = len(df)
    if total_stu == 0:
        st.warning("⚠️ 请先在侧边栏调整筛选条件")
        return

    avg_total = round(df["平均分"].mean(), 2)
    max_score = int(df["总分"].max())
    min_score = int(df["总分"].min())
    pass_rate = round(len(df[df["平均分"] >= 60]) / total_stu * 100, 2)

    # 1. 整体概况
    st.markdown("#### 📌 一、整体概况")
    st.markdown(f"- 本次筛选共 **{total_stu}** 名学生参与分析。")
    st.markdown(
        f"- 整体平均分 **{avg_total}**，最高 **{max_score}**，最低 **{min_score}**，及格率 **{pass_rate}%**。"
    )
    lv = df["等级"].value_counts()
    for k, v in lv.items():
        st.markdown(f"  - {k}：**{v}** 人（{round(v / total_stu * 100, 1)}%）")

    # 2. 科目洞察
    st.markdown("#### 📚 二、科目表现洞察")
    subject_avg = {s: df[s].mean() for s in SUBJECTS}
    sorted_subj = sorted(subject_avg.items(), key=lambda x: x[1])
    weakest, weakest_val = sorted_subj[0]
    strongest, strongest_val = sorted_subj[-1]
    st.markdown(f"- 🟢 **优势科目**：{strongest}（平均分 **{strongest_val:.1f}**）")
    st.markdown(f"- 🔴 **薄弱科目**：{weakest}（平均分 **{weakest_val:.1f}**）")
    st.markdown(f"- 💡 建议：{weakest} 平均分最低，建议增加课时或开展针对性辅导。")

    # 3. 相关性洞察
    st.markdown("#### 🔗 三、科目相关性分析")
    corr = df[SUBJECTS].corr()
    pairs = []
    for i in range(len(SUBJECTS)):
        for j in range(i + 1, len(SUBJECTS)):
            pairs.append((SUBJECTS[i], SUBJECTS[j], corr.iloc[i, j]))
    pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    for s1, s2, r in pairs[:3]:
        if r > 0.7:
            strength = "强正相关"
        elif r > 0.4:
            strength = "中等正相关"
        elif r > 0:
            strength = "弱正相关"
        else:
            strength = "负相关"
        st.markdown(f"- **{s1} ↔ {s2}**：r = **{r:.2f}**（{strength}）")
    top_pair = pairs[0]
    st.markdown(
        f"- 💡 洞察：{top_pair[0]} 与 {top_pair[1]} 相关性最高，可考虑**联合教学**。"
    )

    # 4. 偏科预警
    st.markdown("#### 🚨 四、偏科与不及格预警")
    fail_df = df[(df[SUBJECTS] < 60).any(axis=1)]
    severe_fail = df[(df[SUBJECTS] < 50).any(axis=1)]
    st.markdown(f"- 存在偏科/不及格的学生：**{len(fail_df)}** 人")
    st.markdown(f"- 严重不及格（<50分）学生：**{len(severe_fail)}** 人")

    if len(fail_df) > 0:
        with st.expander("🔴 点击查看不及格学生明细", expanded=False):
            fail_detail = []
            for _, row in fail_df.iterrows():
                fail_subj = [s for s in SUBJECTS if row[s] < 60]
                fail_detail.append({"姓名": row["姓名"], "班级": row["班级"],
                                    "不及格科目": "、".join(fail_subj)})
            st.dataframe(pd.DataFrame(fail_detail), use_container_width=True, hide_index=True)

    # 5. 班级对比
    if len(df["班级"].unique()) > 1:
        st.markdown("#### 🏫 五、班级横向对比")
        cls = df.groupby("班级").agg(
            人数=("姓名", "count"),
            平均分=("平均分", "mean"),
            及格率=("平均分", lambda x: round((x >= 60).sum() / len(x) * 100, 1)),
            最高总分=("总分", "max")
        ).round(2)
        st.dataframe(cls, use_container_width=True)
        best_class = cls["平均分"].idxmax()
        st.markdown(f"- 💡 **{best_class}** 平均分最高，可分享其教学经验。")

    # 6. 综合结论
    st.divider()
    st.markdown("#### ✅ 综合结论")
    conclusions = [
        f"整体成绩处于 **{avg_total:.0f} 分** 水平，及格率 **{pass_rate}%**。",
        f"表现最好的科目是 **{strongest}**，最弱的科目是 **{weakest}**，建议重点加强。",
        f"共发现 **{len(fail_df)}** 名学生存在偏科问题，可建立一对一辅导机制。",
    ]
    if pass_rate < 90:
        conclusions.append("⚠️ 及格率未达 90%，建议关注中低分段学生。")
    else:
        conclusions.append("✅ 及格率表现优秀，继续保持！")

    for i, c in enumerate(conclusions, 1):
        st.markdown(f"{i}. {c}")