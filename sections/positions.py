import streamlit as st
import plotly.express as px
from config import INTENT_COLORS

def render(queries_ranked, queries, length_summary, snippet_opps, _):
    st.markdown(f'<div class="section-header">{_("📊 Ranking Position Distribution")}</div>', unsafe_allow_html=True)

    col_hist, col_tier = st.columns([2, 1])
    with col_hist:
        fig_hist = px.histogram(
            queries_ranked[queries_ranked["Position"] <= 100],
            x="Position", nbins=20,
            color="Intent", color_discrete_map=INTENT_COLORS,
            title=_("Distribution of ranking positions"),
            barmode="stack",
        )
        fig_hist.update_layout(height=340, plot_bgcolor="white")
        fig_hist.add_vline(x=10, line_dash="dash", line_color="red",
                           annotation_text=_("Page 2 boundary"))
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
        st.markdown(_("**Queries by position tier**"))
        st.dataframe(tier_df, use_container_width=True, hide_index=True)

        p4_10  = tier_df[tier_df["Tier"] == "Pos 4–10"]["Queries"].values
        p11_20 = tier_df[tier_df["Tier"] == "Pos 11–20"]["Queries"].values
        if len(p4_10) and len(p11_20) and p11_20[0] > p4_10[0]:
            st.markdown(
                f'<div class="alert-amber">' + 
                _("**{p11}** queries on page 2 vs **{p4}** on page 1. Content updates could push many to page 1.", p11=p11_20[0], p4=p4_10[0]) + 
                '</div>',
                unsafe_allow_html=True,
            )

    st.markdown(f'<div class="section-header">{_("🔤 Query Length Analysis (Head vs Long-Tail)")}</div>', unsafe_allow_html=True)
    st.caption(_("Longer queries = lower volume but higher purchase intent and easier to rank for."))

    col_ql1, col_ql2 = st.columns(2)
    with col_ql1:
        fig_imp = px.bar(
            length_summary, x="Length Group", y="Impressions",
            color="Length Group",
            color_discrete_sequence=["#d32f2f","#f9a825","#1565c0","#388e3c","#7b1fa2"],
            title=_("Impressions by query length"), text="Impressions",
        )
        fig_imp.update_traces(textposition="outside", showlegend=False)
        fig_imp.update_layout(height=320, plot_bgcolor="white", margin=dict(t=40, b=10))
        st.plotly_chart(fig_imp, use_container_width=True)

    with col_ql2:
        fig_ctr = px.bar(
            length_summary, x="Length Group", y=["CTR", "Position"],
            barmode="group",
            color_discrete_sequence=["#1565c0", "#ff6b35"],
            title=_("Avg CTR % and Position by query length"),
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
            f'<div class="alert-green">' +
            _("Long-tail queries (3+ words) make up **{pct:.0f}%** of impressions but convert at **{ctr:.2f}% CTR** vs **{ht:.2f}%** for head terms. Targeting long-tail keywords is a high-ROI strategy.", pct=lt_pct, ctr=lt_ctr, ht=ht_ctr) +
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="alert-blue">' +
            _("Long-tail queries (3+ words) account for **{pct:.0f}%** of impressions.", pct=lt_pct) +
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown(f'<div class="section-header">{_("⭐ Featured Snippet Opportunities")}</div>', unsafe_allow_html=True)
    st.caption(_("Queries ranking **position 2–5** with informational intent — prime candidates for answer boxes."))

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
            st.markdown(_("**How to capture the snippet:**"))
            st.markdown(_("1. Add a direct 40–60 word answer at the top of the page\n2. Use the exact query phrase as an H2 header\n3. For list queries: use `<ul>` / `<ol>` with concise items\n4. For definition queries: bolded term + 1-sentence definition\n5. Add FAQ schema markup\n6. Internal links with anchor text = the query"))
            st.markdown(
                f'<div class="alert-green">' + 
                _("**{n}** opportunities. Top: *\"{q}\"* — pos {pos:.1f}, {imp:,} impressions.", n=len(snippet_opps), q=snippet_opps.iloc[0]["Query"], pos=snippet_opps.iloc[0]["Position"], imp=int(snippet_opps.iloc[0]["Impressions"])) +
                '</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f'<div class="alert-blue">{_("No snippet opportunities found (need queries at position 2–5, informational intent, 10+ impressions).")}</div>',
            unsafe_allow_html=True,
        )
