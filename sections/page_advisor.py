import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import urlparse

CTR_AT_TOP3 = 10.0  # benchmark CTR at position 3


def _short_url(url: str) -> str:
    try:
        p = urlparse(str(url))
        path = p.path.rstrip("/") or "/"
        return path[:70] if path else str(url)[:70]
    except Exception:
        return str(url)[:70]


def _build_page_opportunities(qp_df: pd.DataFrame) -> pd.DataFrame:
    """
    For each page: find queries at positions 8-20, compute traffic potential,
    collect the phrases to add.
    """
    df = qp_df.copy()

    # Normalise column names from GSC export variants
    df.columns = df.columns.str.strip()
    for alias, canonical in [
        ("Top queries", "Query"), ("Top pages", "Page"),
        ("top queries", "Query"), ("top pages", "Page"),
    ]:
        if alias in df.columns and canonical not in df.columns:
            df.rename(columns={alias: canonical}, inplace=True)

    required = {"Query", "Page", "Position", "Impressions", "Clicks"}
    if not required.issubset(df.columns):
        return pd.DataFrame()

    for col in ("Position", "Impressions", "Clicks"):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    if "CTR" not in df.columns:
        df["CTR"] = (df["Clicks"] / df["Impressions"].replace(0, 1) * 100).round(2)

    # Only striking-distance rows
    striking = df[
        (df["Position"] >= 8) &
        (df["Position"] <= 20) &
        (df["Impressions"] >= 20)
    ].copy()

    if striking.empty:
        return pd.DataFrame()

    striking["Traffic_Gain"] = (
        (striking["Impressions"] * CTR_AT_TOP3 / 100) - striking["Clicks"]
    ).clip(lower=0).round(0)

    # Aggregate per page
    agg = (
        striking.groupby("Page")
        .agg(
            Queries_Count=("Query", "count"),
            Total_Gain=("Traffic_Gain", "sum"),
            Top_Phrases=("Query", lambda x: list(
                x.loc[striking.loc[x.index, "Traffic_Gain"].nlargest(6).index]
            )),
            Avg_Position=("Position", "mean"),
            Total_Impressions=("Impressions", "sum"),
        )
        .reset_index()
    )

    agg["Avg_Position"] = agg["Avg_Position"].round(1)
    agg["Total_Gain"] = agg["Total_Gain"].astype(int)
    agg["Short_URL"] = agg["Page"].apply(_short_url)
    agg["Effort"] = agg["Avg_Position"].apply(
        lambda p: "Low" if p <= 12 else ("Medium" if p <= 16 else "High")
    )

    return agg.sort_values("Total_Gain", ascending=False).reset_index(drop=True)


def render(cannibal_df, _) -> None:
    st.markdown(
        f'<div class="section-header">{_("📋 Page Advisor — What to Add Where")}</div>',
        unsafe_allow_html=True,
    )

    if cannibal_df is None or cannibal_df.empty:
        st.info(_(
            "Upload **Query+Page CSV** in Setup to unlock this section. "
            "In GSC: Performance → Queries tab → click any query → Pages tab → Export CSV."
        ))
        _show_howto(_)
        return

    pages_opp = _build_page_opportunities(cannibal_df)

    if pages_opp.empty:
        st.info(_("No striking-distance query-page pairs found (need positions 8–20, 20+ impressions)."))
        return

    # ── Summary metrics ───────────────────────────────────────────────────────
    total_pages  = len(pages_opp)
    total_gain   = int(pages_opp["Total_Gain"].sum())
    total_queries = int(pages_opp["Queries_Count"].sum())
    low_effort   = pages_opp[pages_opp["Effort"] == "Low"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(_("Pages with opportunity"), total_pages)
    col2.metric(_("Queries to optimise"), total_queries)
    col3.metric(_("Total traffic upside"), f"+{total_gain:,}")
    col4.metric(_("Low-effort pages"), len(low_effort), delta=f"+{int(low_effort['Total_Gain'].sum()):,} clicks")

    st.markdown(
        f'<div class="alert-green">'
        f'<b>How to use this:</b> each row below is a page on your site. '
        f'The phrases listed are queries Google already associates with that page — '
        f'they just need a nudge. Add them to your H2s, intro paragraph, or FAQ. '
        f'That\'s it.'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Bar chart — top pages by upside ───────────────────────────────────────
    top15 = pages_opp.head(15)
    EFFORT_COLORS = {"Low": "#4ade80", "Medium": "#facc15", "High": "#f87171"}

    fig = px.bar(
        top15,
        x="Total_Gain",
        y="Short_URL",
        orientation="h",
        color="Effort",
        color_discrete_map=EFFORT_COLORS,
        text="Total_Gain",
        hover_data={"Queries_Count": True, "Avg_Position": ":.1f", "Total_Impressions": ":,"},
        height=max(380, len(top15) * 36),
        labels={"Total_Gain": "Est. additional clicks/period", "Short_URL": ""},
        title=_("Top pages by traffic upside — fix these first"),
    )
    fig.update_traces(texttemplate="+%{text:,}", textposition="outside")
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=45, b=10, l=10, r=90),
        legend_title_text="Effort",
    )
    fig.update_xaxes(gridcolor="#1e1e24")
    st.plotly_chart(fig, use_container_width=True)

    # ── Per-page action cards ─────────────────────────────────────────────────
    st.markdown(f"### {_('🎯 Action list — page by page')}")
    st.caption(_("Expand each page to see exactly which phrases to add."))

    effort_filter = st.selectbox(
        _("Show effort level"),
        ["All", "Low", "Medium", "High"],
        key="pa_effort",
    )

    filtered = pages_opp if effort_filter == "All" else pages_opp[pages_opp["Effort"] == effort_filter]
    filtered = filtered.reset_index(drop=True)

    for i, row in filtered.iterrows():
        effort_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(row["Effort"], "⚪")
        label = f"{effort_emoji} **{row['Short_URL']}** — +{row['Total_Gain']:,} clicks · {row['Queries_Count']} queries · avg pos {row['Avg_Position']:.0f}"

        with st.expander(label, expanded=(i < 3)):
            phrases = row["Top_Phrases"]

            # Phrase chips
            chips_html = " ".join(
                f'<span style="display:inline-block;background:rgba(37,99,235,0.15);'
                f'border:1px solid rgba(37,99,235,0.3);border-radius:20px;'
                f'padding:3px 12px;margin:3px;font-size:0.83rem;color:#93c5fd;">'
                f'{p}</span>'
                for p in phrases
            )
            st.markdown(
                f'<div style="margin-bottom:0.75rem">'
                f'<div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:0.8px;color:#444;margin-bottom:0.5rem">Phrases to add</div>'
                f'{chips_html}'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Recommendation text
            phrase_list = '", "'.join(phrases[:3])
            st.markdown(
                f'<div class="alert-blue">'
                f'<b>Recommended action:</b> Add "{phrase_list}" to the H2 headings and first 200 words of this page. '
                f'These queries already get <b>{int(row["Total_Impressions"]):,} impressions</b> — '
                f'Google knows this page is relevant, it just needs stronger signal.'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Detail table for this page
            page_queries = cannibal_df[
                cannibal_df["Page"].str.strip() == row["Page"].strip()
            ].copy() if "Page" in cannibal_df.columns else pd.DataFrame()

            if not page_queries.empty:
                pq = page_queries[
                    (pd.to_numeric(page_queries["Position"], errors="coerce").fillna(99) >= 8) &
                    (pd.to_numeric(page_queries["Position"], errors="coerce").fillna(99) <= 20)
                ].sort_values("Impressions", ascending=False).head(10)

                if not pq.empty:
                    pq = pq.reset_index(drop=True)
                    pq.index += 1
                    st.dataframe(
                        pq[["Query", "Position", "Impressions", "Clicks", "CTR"]]
                        .style
                        .background_gradient(subset=["Impressions"], cmap="Blues")
                        .format({
                            "Position": "{:.1f}",
                            "CTR": "{:.2f}%",
                            "Impressions": "{:,}",
                        }),
                        use_container_width=True,
                        height=min(380, 50 + len(pq) * 38),
                    )

        if i >= 29:
            st.caption(_("Showing top 30 pages. Upload more data or filter by effort to see others."))
            break


def _show_howto(_) -> None:
    with st.expander(_("📖 How to export Query+Page CSV from GSC")):
        st.markdown(_("""
1. Open [Google Search Console](https://search.google.com/search-console)
2. Go to **Performance → Search results**
3. Make sure **Queries** tab is selected
4. Click any query in the table
5. In the panel that opens, click the **Pages** tab
6. Click **Export → Download CSV**

The exported file has columns: `Query`, `Page`, `Clicks`, `Impressions`, `CTR`, `Position`

Upload it in **⬆️ Setup & Upload → Cannibalization: Query+Page CSV**
        """))
