import streamlit as st


def render(stats, queries):
    st.markdown('<div class="section-header">🔴 Critical Findings</div>', unsafe_allow_html=True)

    findings = []

    if stats.blog_pct > 50:
        findings.append(("red",
            f"Blog / informational pages drive <strong>{stats.blog_pct:.0f}%</strong> of clicks "
            f"but have no direct purchase intent. Only <strong>{100 - stats.blog_pct:.0f}%</strong> "
            "of clicks land on product or category pages."))

    if stats.zero_click_imp > 0:
        zero_count = int((queries["Clicks"] == 0).sum())
        findings.append(("red",
            f"<strong>{stats.zero_click_imp:,} impressions</strong> across "
            f"<strong>{zero_count}</strong> queries received zero clicks. "
            "The site ranks — but users don't click. Title tags and meta descriptions "
            "need immediate attention."))

    if stats.brand_pct > 60:
        findings.append(("red",
            f"<strong>{stats.brand_pct:.0f}%</strong> of clicks are branded queries. "
            "Non-brand organic traffic is critically low — almost all traffic comes "
            "from users who already know the brand."))

    if stats.mobile_pos is not None and stats.desktop_pos is not None \
            and (stats.desktop_pos - stats.mobile_pos) > 1.5:
        findings.append(("amber",
            f"Desktop ranking ({stats.desktop_pos:.1f}) is significantly worse than "
            f"mobile ({stats.mobile_pos:.1f}) — a gap of "
            f"{stats.desktop_pos - stats.mobile_pos:.1f} positions. "
            "B2B buyers who research on desktop see you below competitors."))

    underperformers = queries[
        (queries["Impressions"] >= 20) &
        (queries["CTR"] < queries["Expected CTR"] * 0.5)
    ]
    if len(underperformers) > 0:
        findings.append(("amber",
            f"<strong>{len(underperformers)}</strong> queries with 20+ impressions achieve "
            "less than half the benchmark CTR for their ranking position. "
            "These pages rank well but fail to attract clicks."))

    if not findings:
        findings.append(("green", "No critical issues detected based on current data."))

    for severity, text in findings:
        st.markdown(f'<div class="alert-{severity}">{text}</div>', unsafe_allow_html=True)
