import streamlit as st

def render(stats, queries, _):
    st.markdown(f'<div class="section-header">{_("🔴 Critical Findings")}</div>', unsafe_allow_html=True)

    findings = []

    if stats.blog_pct > 50:
        findings.append(("red",
            _("Blog / informational pages drive **{pct:.0f}%** of clicks but have no direct purchase intent. Only **{diff:.0f}%** of clicks land on product or category pages.", pct=stats.blog_pct, diff=100-stats.blog_pct)))

    if stats.anonymized_pct > 20:
        findings.append(("red",
            _("Google Search Console is hiding **{pct:.0f}%** of your clicks ({clicks:,}) due to privacy thresholds. This is common in B2B but means your query data is highly incomplete.", pct=stats.anonymized_pct, clicks=stats.anonymized_clicks)))

    if stats.zero_click_imp > 0:
        zero_count = int((queries["Clicks"] == 0).sum())
        findings.append(("red",
            _("**{imp:,} impressions** across **{n}** queries received zero clicks. The site ranks — but users don't click. Title tags and meta descriptions need immediate attention.", imp=stats.zero_click_imp, n=zero_count)))

    if stats.brand_pct > 60:
        findings.append(("red",
            _("**{pct:.0f}%** of clicks are branded queries. Non-brand organic traffic is critically low — almost all traffic comes from users who already know the brand.", pct=stats.brand_pct)))

    if stats.mobile_pos is not None and stats.desktop_pos is not None \
            and (stats.desktop_pos - stats.mobile_pos) > 1.5:
        findings.append(("amber",
            _("Desktop ranking ({dt:.1f}) is significantly worse than mobile ({mob:.1f}) — a gap of {gap:.1f} positions. B2B buyers who research on desktop see you below competitors.", dt=stats.desktop_pos, mob=stats.mobile_pos, gap=(stats.desktop_pos - stats.mobile_pos))))

    underperformers = queries[
        (queries["Impressions"] >= 20) &
        (queries["CTR"] < queries["Expected CTR"] * 0.5)
    ]
    if len(underperformers) > 0:
        findings.append(("amber",
            _("**{n}** queries with 20+ impressions achieve less than half the benchmark CTR for their ranking position. These pages rank well but fail to attract clicks.", n=len(underperformers))))

    if not findings:
        findings.append(("green", _("No critical issues detected based on current data.")))

    for severity, text in findings:
        st.markdown(f'<div class="alert-{severity}">{text}</div>', unsafe_allow_html=True)
