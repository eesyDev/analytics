import streamlit as st
import pandas as pd
import plotly.express as px


# ── Page Opportunity Table ────────────────────────────────────────────────────

def render_page_opportunity(page_opp: pd.DataFrame, stats, _):
    st.markdown(
        f'<div class="section-header">{_("💸 Click Opportunity by Page")}</div>',
        unsafe_allow_html=True,
    )
    st.caption(_(
        "Estimated clicks gained if each page reached top-3 position. "
        "Commercial CTR benchmarks used. Treat as directional — actual gains depend on competition."
    ))

    if page_opp is None or page_opp.empty:
        st.info(_("No page opportunity data — all pages already rank in top 3, or Position data missing."))
        return

    has_revenue = "Rev_Gain_top3" in page_opp.columns and page_opp["Rev_Gain_top3"].notna().any()

    total_gain_top3 = int(page_opp["Gain_top3"].sum())
    total_gain_top1 = int(page_opp["Gain_top1"].sum())

    col1, col2, col3 = st.columns(3)
    col1.metric(_("Current clicks (period)"), f"{int(stats.total_clicks):,}")
    col2.metric(_("+ Clicks if top 3"), f"+{total_gain_top3:,}", delta=f"+{100*total_gain_top3/max(1,stats.total_clicks):.0f}%")
    col3.metric(_("+ Clicks if top 1"), f"+{total_gain_top1:,}", delta=f"+{100*total_gain_top1/max(1,stats.total_clicks):.0f}%")

    if has_revenue:
        total_rev = page_opp["Rev_Gain_top3"].sum()
        st.metric(_("Estimated revenue gain (top 3)"), f"${total_rev:,.0f}")

    # Chart — top 15 pages
    top15 = page_opp.head(15).copy()
    top15["Label"] = top15["Page"].str.replace(r"https?://[^/]+", "", regex=True).str[:60]

    fig = px.bar(
        top15,
        x="Gain_top3",
        y="Label",
        orientation="h",
        color="Gain_top3",
        color_continuous_scale="Blues",
        title=_("Top 15 pages by missed clicks (if they hit top 3)"),
        height=480,
        labels={"Gain_top3": _("Estimated missed clicks"), "Label": ""},
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        coloraxis_showscale=False,
        margin=dict(t=40, b=10, l=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Table
    display_cols = ["Label", "Clicks", "Position", "Impressions", "CTR", "Gain_top3", "Gain_top1"]
    formats = {
        "CTR": "{:.2f}%",
        "Position": "{:.1f}",
        "Gain_top3": "{:,.0f}",
        "Gain_top1": "{:,.0f}",
        "Clicks": "{:,.0f}",
        "Impressions": "{:,.0f}",
    }
    col_rename = {
        "Gain_top3": _("+ Clicks → top 3"),
        "Gain_top1": _("+ Clicks → top 1"),
    }
    if has_revenue:
        display_cols.append("Rev_Gain_top3")
        formats["Rev_Gain_top3"] = "${:,.0f}"
        col_rename["Rev_Gain_top3"] = _("+ Revenue → top 3")

    top15_display = top15[display_cols].rename(columns=col_rename)
    st.dataframe(
        top15_display.style
        .background_gradient(subset=[col_rename["Gain_top3"]], cmap="Blues")
        .format(formats),
        use_container_width=True,
        hide_index=True,
    )


# ── AI Executive Briefing ─────────────────────────────────────────────────────

def _build_prompt(stats, page_opp, cannibal_issues, queries, _) -> str:
    top_opps_text = ""
    if len(stats.top_opps) > 0:
        for _, row in stats.top_opps.head(10).iterrows():
            top_opps_text += (
                f'  - "{row["Query"]}" | pos {row["Position"]:.1f} | '
                f'{row["Impressions"]:,} imps | {row["Clicks"]:,} clicks | '
                f'missed ~{row["Opportunity Score"]:.0f} clicks\n'
            )

    page_opp_text = ""
    if page_opp is not None and not page_opp.empty:
        for _, row in page_opp.head(8).iterrows():
            label = str(row["Page"]).replace("https://", "").replace("http://", "")[:80]
            page_opp_text += (
                f'  - {label} | pos {row["Position"]:.1f} | '
                f'{int(row["Clicks"]):,} clicks now | '
                f'could gain +{int(row["Gain_top3"]):,} clicks at top 3\n'
            )

    intent_mix = ""
    for _, row in stats.intent_summary.iterrows():
        intent_mix += f'{row["Intent"]}: {row["Clicks"]:,} clicks ({row["Impressions"]:,} imps) | '

    cannibal_n = len(cannibal_issues) if cannibal_issues is not None and len(cannibal_issues) > 0 else 0

    return f"""You are a senior SEO analyst. Write a concise executive briefing based on this data.

SITE DATA ({stats.date_range}):
- Total clicks: {stats.total_clicks:,}
- Total impressions: {stats.total_impressions:,}
- Weighted CTR: {stats.weighted_ctr:.2f}%
- Weighted position: {stats.weighted_pos:.1f}
- Zero-click impressions (ranks but nobody clicks): {stats.zero_click_imp:,}
- Estimated total missed clicks: {int(stats.total_opportunity):,}
- Blog/info pages % of clicks: {stats.blog_pct:.0f}%
- Intent mix: {intent_mix}
- Cannibalization issues: {cannibal_n} queries

TOP UNDERPERFORMING QUERIES (highest missed click potential):
{top_opps_text or '  No data'}

TOP PAGES WITH CLICK OPPORTUNITY:
{page_opp_text or '  No data'}

Write the following (use markdown formatting):
## Executive Summary
2–3 sentences. Include the total missed clicks number. State the single biggest revenue lever.

## Top 5 Action Items
For each: state the exact page URL or query, what specifically to change (title tag text, content format, etc.), and the estimated click impact. Be specific — no generic advice.

Keep it tight. The reader is a business owner, not an SEO nerd."""


def render_ai_briefing(stats, page_opp, cannibal_issues, queries, _):
    st.markdown(
        f'<div class="section-header">{_("🤖 AI Executive Briefing")}</div>',
        unsafe_allow_html=True,
    )
    st.caption(_("Generates a plain-language summary and specific action items based on your data. Uses Claude AI."))

    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.warning(_(
            "Add `ANTHROPIC_API_KEY` to `.streamlit/secrets.toml` to enable AI briefings."
        ))
        return

    if st.button(_("🤖 Generate AI Briefing"), type="primary"):
        try:
            import anthropic
        except ImportError:
            st.error(_("Run `pip install anthropic` to enable this feature."))
            return

        prompt = _build_prompt(stats, page_opp, cannibal_issues, queries, _)
        client = anthropic.Anthropic(api_key=api_key)

        with st.spinner(_("Generating briefing…")):
            output = st.empty()
            full_text = ""
            with client.messages.stream(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for text in stream.text_stream:
                    full_text += text
                    output.markdown(full_text)


# ── Combined render ───────────────────────────────────────────────────────────

def render(stats, page_opp, cannibal_issues, queries, _):
    render_page_opportunity(page_opp, stats, _)
    st.divider()
    render_ai_briefing(stats, page_opp, cannibal_issues, queries, _)
