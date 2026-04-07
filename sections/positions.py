import streamlit as st
import plotly.express as px
from config import INTENT_COLORS


def render(queries_ranked, queries, length_summary, snippet_opps):
    # Position distribution
    st.markdown('<div class="section-header">📊 Ranking Position Distribution</div>',
                unsafe_allow_html=True)

    col_hist, col_tier = st.columns([2, 1])
    with col_hist:
        fig_hist = px.histogram(
            queries_ranked[queries_ranked["Position"] <= 100],
            x="Position", nbins=20,
            color="Intent", color_discrete_map=INTENT_COLORS,
            title="Distribution of ranking positions",
            barmode="stack",
        )
        fig_hist.update_layout(height=340, plot_bgcolor="white")
        fig_hist.add_vline(x=10, line_dash="dash", line_color="red",
                           annotation_text="Page 2 boundary")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_tier:
        tier_data = [
            {"Tier": "Top 3",      "min": 0,   "max": 3},
            {"Tier": "Pos 4–10",   "min": 3,   "max": 10},
            {"Tier": "Pos 11–20",  "min": 10,  "max": 20},
            {"Tier": "Pos 21–100", "min": 20,  "max": 100},
            {"Tier": "Pos 100+",   "min": 100, "max": 9999},
        ]
        rows = []
        for t in tier_data:
            subset = queries_ranked[
                (queries_ranked["Position"] > t["min"]) &
                (queries_ranked["Position"] <= t["max"])
            ]
            rows.append({
                "Tier":        t["Tier"],
                "Queries":     len(subset),
                "Impressions": int(subset["Impressions"].sum()),
                "Clicks":      int(subset["Clicks"].sum()),
            })
        import pandas as pd
        tier_df = pd.DataFrame(rows)
        st.markdown("**Queries by position tier**")
        st.dataframe(tier_df, use_container_width=True, hide_index=True)

        p4_10  = tier_df[tier_df["Tier"] == "Pos 4–10"]["Queries"].values
        p11_20 = tier_df[tier_df["Tier"] == "Pos 11–20"]["Queries"].values
        if len(p4_10) and len(p11_20) and p11_20[0] > p4_10[0]:
            st.markdown(
                f'<div class="alert-amber"><strong>{p11_20[0]}</strong> queries on page 2 vs '
                f'<strong>{p4_10[0]}</strong> on page 1. '
                "Content updates could push many to page 1.</div>",
                unsafe_allow_html=True,
            )

    # Query length analysis
    st.markdown('<div class="section-header">🔤 Query Length Analysis (Head vs Long-Tail)</div>',
                unsafe_allow_html=True)
    st.caption("Longer queries = lower volume but higher purchase intent and easier to rank for.")

    col_ql1, col_ql2 = st.columns(2)
    with col_ql1:
        fig_imp = px.bar(
            length_summary, x="Length Group", y="Impressions",
            color="Length Group",
            color_discrete_sequence=["#d32f2f","#f9a825","#1565c0","#388e3c","#7b1fa2"],
            title="Impressions by query length", text="Impressions",
        )
        fig_imp.update_traces(textposition="outside", showlegend=False)
        fig_imp.update_layout(height=320, plot_bgcolor="white", margin=dict(t=40, b=10))
        st.plotly_chart(fig_imp, use_container_width=True)

    with col_ql2:
        fig_ctr = px.bar(
            length_summary, x="Length Group", y=["CTR", "Position"],
            barmode="group",
            color_discrete_sequence=["#1565c0", "#ff6b35"],
            title="Avg CTR % and Position by query length",
        )
        fig_ctr.update_layout(height=320, plot_bgcolor="white", margin=dict(t=40, b=10))
        st.plotly_chart(fig_ctr, use_container_width=True)

    longtail     = queries[queries["Word Count"] >= 3]
    imp_total_s  = queries["Impressions"].sum() or 1
    lt_pct       = 100 * longtail["Impressions"].sum() / imp_total_s
    lt_ctr       = longtail["CTR"].mean() if len(longtail) > 0 else 0
    ht_ctr       = queries[queries["Word Count"] <= 2]["CTR"].mean() if len(queries[queries["Word Count"] <= 2]) > 0 else 0

    if lt_ctr > ht_ctr:
        st.markdown(
            f'<div class="alert-green">Long-tail queries (3+ words) make up '
            f'<strong>{lt_pct:.0f}%</strong> of impressions but convert at '
            f'<strong>{lt_ctr:.2f}% CTR</strong> vs <strong>{ht_ctr:.2f}%</strong> for head terms. '
            "Targeting long-tail keywords is a high-ROI strategy.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="alert-blue">Long-tail queries (3+ words) account for '
            f'<strong>{lt_pct:.0f}%</strong> of impressions.</div>',
            unsafe_allow_html=True,
        )

    # Featured snippet opportunities
    st.markdown('<div class="section-header">⭐ Featured Snippet Opportunities</div>',
                unsafe_allow_html=True)
    st.caption(
        "Queries ranking **position 2–5** with informational intent — prime candidates for "
        "answer boxes. Structured content (H2 headers, bullet lists, FAQ schema) can jump "
        "above position 1."
    )

    if len(snippet_opps) > 0:
        col_sn1, col_sn2 = st.columns([2, 1])
        with col_sn1:
            st.dataframe(
                snippet_opps.style
                .background_gradient(subset=["Impressions"], cmap="Blues")
                .format({"Position": "{:.1f}", "CTR": "{:.2f}%", "Expected CTR": "{:.1f}%"}),
                use_container_width=True, height=420,
            )
        with col_sn2:
            st.markdown("**How to capture the snippet:**")
            st.markdown("""
1. Add a direct 40–60 word answer at the top of the page
2. Use the exact query phrase as an H2 header
3. For list queries: use `<ul>` / `<ol>` with concise items
4. For definition queries: bolded term + 1-sentence definition
5. Add FAQ schema markup
6. Internal links with anchor text = the query
            """)
            st.markdown(
                f'<div class="alert-green"><strong>{len(snippet_opps)}</strong> opportunities. '
                f'Top: <em>"{snippet_opps.iloc[0]["Query"]}"</em> — '
                f'pos {snippet_opps.iloc[0]["Position"]:.1f}, '
                f'{int(snippet_opps.iloc[0]["Impressions"]):,} impressions.</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="alert-blue">No snippet opportunities found '
            '(need queries at position 2–5, informational intent, 10+ impressions).</div>',
            unsafe_allow_html=True,
        )
