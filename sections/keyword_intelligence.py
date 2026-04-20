import re
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

STOPWORDS = set("""
a an the is are was were be been being have has had do does did will would could should
may might shall to of in for on with at by from as into through during before after above
below between out off over and or but if not no so yet both either neither each few more
most other some such only same than too very just your my our their its this that these
those i you he she we they what which who whom how when where why all any both each every
no nor not only own same so than too very can will just should now
""".split())


def _clean(text: str) -> list[str]:
    words = re.sub(r"[^a-z0-9\s]", "", text.lower()).split()
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def _bigrams(words: list[str]) -> list[str]:
    return [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]


# ── Topic Clusters ─────────────────────────────────────────────────────────────

def _build_clusters(queries_df: pd.DataFrame) -> pd.DataFrame:
    bigram_imps: dict[str, float] = {}
    for _, row in queries_df.iterrows():
        words = _clean(str(row["Query"]))
        imps = float(row.get("Impressions", 1))
        for bg in _bigrams(words):
            bigram_imps[bg] = bigram_imps.get(bg, 0) + imps

    top_bigrams = [bg for bg, _ in sorted(bigram_imps.items(), key=lambda x: -x[1])[:35]]

    df = queries_df.copy()
    df["Cluster"] = None

    for bg in top_bigrams:
        mask = df["Cluster"].isna() & df["Query"].str.lower().str.contains(bg, regex=False)
        df.loc[mask, "Cluster"] = bg

    def _fallback(q):
        words = _clean(str(q))
        return words[0] if words else "other"

    df.loc[df["Cluster"].isna(), "Cluster"] = (
        df.loc[df["Cluster"].isna(), "Query"].apply(_fallback)
    )

    agg = (
        df.groupby("Cluster")
        .agg(
            Queries=("Query", "count"),
            Impressions=("Impressions", "sum"),
            Clicks=("Clicks", "sum"),
            Avg_Position=("Position", "mean"),
        )
        .reset_index()
    )
    agg["CTR"] = (agg["Clicks"] / agg["Impressions"].replace(0, 1) * 100).round(2)
    agg["Avg_Position"] = agg["Avg_Position"].round(1)

    df["is_longtail"] = df["Query"].str.split().str.len() >= 3
    depth = df.groupby("Cluster")["is_longtail"].mean().reset_index()
    depth.columns = ["Cluster", "Depth_Score"]
    depth["Depth_Score"] = (depth["Depth_Score"] * 100).round(0)

    agg = agg.merge(depth, on="Cluster")

    median_imps = agg["Impressions"].median()
    median_ctr  = agg["CTR"].median()

    def _status(row):
        if row["Avg_Position"] > 20 and row["Impressions"] > median_imps:
            return "🔴 Opportunity"
        if row["Avg_Position"] <= 5 and row["CTR"] > median_ctr:
            return "🟢 Strong"
        if 5 < row["Avg_Position"] <= 15:
            return "🟡 Growing"
        return "⚪"

    agg["Status"] = agg.apply(_status, axis=1)
    return agg.sort_values("Impressions", ascending=False).reset_index(drop=True)


def _render_clusters(queries_df: pd.DataFrame, _) -> None:
    cluster_df = _build_clusters(queries_df)
    top30 = cluster_df.head(30)

    fig = px.treemap(
        top30,
        path=["Cluster"],
        values="Impressions",
        color="Avg_Position",
        color_continuous_scale=["#388e3c", "#f9a825", "#d32f2f"],
        color_continuous_midpoint=15,
        custom_data=["Queries", "Clicks", "CTR", "Avg_Position", "Depth_Score", "Status"],
        height=500,
        title=_("Topic Clusters — size = impressions, color = avg position (green = ranking well)"),
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Impressions: %{value:,}<br>"
            "Queries: %{customdata[0]}<br>"
            "Clicks: %{customdata[1]:,}<br>"
            "CTR: %{customdata[2]:.2f}%<br>"
            "Avg Position: %{customdata[3]:.1f}<br>"
            "Long-tail depth: %{customdata[4]:.0f}%<br>"
            "Status: %{customdata[5]}<extra></extra>"
        )
    )
    fig.update_layout(
        paper_bgcolor="white",
        margin=dict(t=50, b=10, l=10, r=10),
        coloraxis_colorbar=dict(title="Avg Pos"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Opportunities callout
    opps = cluster_df[cluster_df["Status"] == "🔴 Opportunity"]
    if not opps.empty:
        top_opp = opps.iloc[0]
        st.markdown(
            f'<div class="alert-amber">'
            f'<b>🔴 Top opportunity:</b> cluster <b>"{top_opp["Cluster"]}"</b> — '
            f'{int(top_opp["Impressions"]):,} impressions but avg position {top_opp["Avg_Position"]:.0f}. '
            f'This topic has real demand — improve your content here.'
            f'</div>',
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown(f"#### {_('📐 Depth vs Breadth')}")
        st.caption(_("X = % long-tail queries. Y = unique query count. Bubble = impressions."))
        fig2 = px.scatter(
            cluster_df.head(25),
            x="Depth_Score",
            y="Queries",
            size="Impressions",
            color="CTR",
            color_continuous_scale="RdYlGn",
            text="Cluster",
            hover_data={"Avg_Position": ":.1f", "Impressions": ":,"},
            height=380,
            labels={
                "Depth_Score": "Depth — % long-tail queries",
                "Queries":     "Breadth — unique query count",
            },
        )
        fig2.update_traces(textposition="top center", textfont_size=8)
        fig2.update_layout(paper_bgcolor="white", plot_bgcolor="white")
        fig2.update_xaxes(gridcolor="#f0f0f0", range=[-5, 105])
        fig2.update_yaxes(gridcolor="#f0f0f0")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown(f"#### {_('📋 Cluster table')}")
        display = cluster_df[
            ["Status", "Cluster", "Queries", "Impressions", "Clicks", "CTR", "Avg_Position", "Depth_Score"]
        ].copy()
        display.index = display.index + 1
        st.dataframe(
            display.style
            .background_gradient(subset=["Impressions"], cmap="Blues")
            .background_gradient(subset=["Avg_Position"], cmap="RdYlGn_r")
            .format({
                "Impressions":  "{:,}",
                "Clicks":       "{:,}",
                "CTR":          "{:.2f}%",
                "Avg_Position": "{:.1f}",
                "Depth_Score":  "{:.0f}%",
            }),
            use_container_width=True,
            height=380,
        )


# ── Striking Distance ──────────────────────────────────────────────────────────

EFFORT_COLORS = {"Low": "#388e3c", "Medium": "#f9a825", "High": "#d32f2f"}


def _build_striking(queries_df: pd.DataFrame, min_imps: int) -> pd.DataFrame:
    df = queries_df[
        (queries_df["Position"] >= 8) &
        (queries_df["Position"] <= 20) &
        (queries_df["Impressions"] >= min_imps)
    ].copy()

    if df.empty:
        return df

    # Use custom CTR curve if available (Expected CTR column from compute_opportunity)
    if "Expected CTR" in df.columns:
        ctr_top3 = df["Expected CTR"].clip(upper=30)
    else:
        ctr_top3 = pd.Series(10.0, index=df.index)

    df["Potential_Clicks"] = (df["Impressions"] * ctr_top3 / 100).round(0)
    df["Traffic_Gain"]     = (df["Potential_Clicks"] - df["Clicks"]).clip(lower=0).round(0)
    df["Effort"]           = df["Position"].apply(
        lambda p: "Low" if p <= 12 else ("Medium" if p <= 16 else "High")
    )

    return (
        df[df["Traffic_Gain"] > 0]
        .sort_values("Traffic_Gain", ascending=False)
        .reset_index(drop=True)
    )


def _render_striking(queries_df: pd.DataFrame, _) -> None:
    min_imps = st.slider(_("Min impressions"), 20, 500, 50, step=10, key="sd_min_imps")
    df = _build_striking(queries_df, min_imps)

    if df.empty:
        st.info(_("No striking distance queries found. Try lowering the impressions threshold."))
        return

    total_gain  = int(df["Traffic_Gain"].sum())
    low_effort  = df[df["Effort"] == "Low"]
    quick_wins  = int(low_effort["Traffic_Gain"].sum())

    col1, col2, col3 = st.columns(3)
    col1.metric(_("Queries within reach"), len(df))
    col2.metric(_("Total traffic upside"), f"+{total_gain:,} clicks")
    col3.metric(_("Quick wins (low effort)"), f"+{quick_wins:,} clicks", delta=f"{len(low_effort)} queries")

    st.markdown(
        f'<div class="alert-green">'
        f'<b>{len(low_effort)} low-effort queries</b> at positions 8–12 — '
        f'these are the ones to tackle first. One focused content update each = <b>+{quick_wins:,} estimated clicks</b>.'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Main bar chart
    top20 = df.head(20)
    fig = px.bar(
        top20,
        x="Traffic_Gain",
        y="Query",
        orientation="h",
        color="Effort",
        color_discrete_map=EFFORT_COLORS,
        text="Traffic_Gain",
        hover_data={"Position": ":.1f", "Impressions": ":,", "CTR": ":.2f"},
        height=max(400, len(top20) * 32),
        labels={"Traffic_Gain": "Est. additional clicks/period", "Query": ""},
        title=_("Top striking distance queries — potential traffic gain at position 3"),
    )
    fig.update_traces(texttemplate="+%{text:.0f}", textposition="outside")
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(t=45, b=10, l=10, r=80),
        legend_title_text="Effort",
    )
    fig.update_xaxes(gridcolor="#f0f0f0")
    st.plotly_chart(fig, use_container_width=True)

    # Priority matrix
    st.markdown(f"#### {_('⚡ Priority Matrix — Impact vs Effort')}")
    st.caption(_("Top-left = highest ROI: close to page 1 + biggest traffic upside."))

    fig2 = px.scatter(
        df.head(50),
        x="Position",
        y="Traffic_Gain",
        size="Impressions",
        color="Effort",
        color_discrete_map=EFFORT_COLORS,
        text="Query",
        hover_data={"Impressions": True, "CTR": ":.2f", "Intent": True},
        height=450,
        labels={
            "Position":     "Current Position (lower = closer to page 1)",
            "Traffic_Gain": "Est. Traffic Gain (clicks)",
        },
    )
    fig2.update_traces(textposition="top center", textfont_size=8)
    fig2.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(range=[21, 7], gridcolor="#f0f0f0"),
        yaxis=dict(gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Full table
    with st.expander(_("📋 Full list ({n} queries)".format(n=len(df)))):
        c1, c2 = st.columns(2)
        intent_opts = ["All"] + sorted(df["Intent"].dropna().unique().tolist())
        effort_opts = ["All", "Low", "Medium", "High"]
        intent_f = c1.selectbox(_("Intent"), intent_opts, key="sd_intent")
        effort_f = c2.selectbox(_("Effort"), effort_opts, key="sd_effort")

        tbl = df.copy()
        if intent_f != "All":
            tbl = tbl[tbl["Intent"] == intent_f]
        if effort_f != "All":
            tbl = tbl[tbl["Effort"] == effort_f]

        tbl = tbl.reset_index(drop=True)
        tbl.index += 1

        st.dataframe(
            tbl[["Query", "Position", "Impressions", "Clicks", "CTR", "Intent", "Traffic_Gain", "Effort"]]
            .style
            .background_gradient(subset=["Traffic_Gain"], cmap="Greens")
            .background_gradient(subset=["Impressions"],  cmap="Blues")
            .applymap(
                lambda v: f"color: {EFFORT_COLORS.get(v, '#333')}; font-weight: bold",
                subset=["Effort"],
            )
            .format({
                "Position":     "{:.1f}",
                "CTR":          "{:.2f}%",
                "Traffic_Gain": "+{:.0f}",
                "Impressions":  "{:,}",
            }),
            use_container_width=True,
            height=min(600, 60 + len(tbl) * 38),
        )


# ── Main render ───────────────────────────────────────────────────────────────

def render(queries_df: pd.DataFrame, _) -> None:
    st.markdown(
        f'<div class="section-header">{_("🎯 Keyword Intelligence")}</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs([
        _("🗺️ Topic Clusters"),
        _("🎯 Striking Distance"),
    ])

    with tab1:
        _render_clusters(queries_df, _)

    with tab2:
        _render_striking(queries_df, _)
