import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from analysis import expected_ctr
from config import INTENT_COLORS


def render(queries, stats):
    # Opportunity Matrix
    st.markdown('<div class="section-header">🎯 Opportunity Matrix — CTR vs Position</div>',
                unsafe_allow_html=True)
    st.caption("Queries below the red benchmark line are underperforming. Size = Impressions.")

    opp_df = queries[queries["Impressions"] >= 5].copy()
    fig = px.scatter(
        opp_df, x="Position", y="CTR",
        size="Impressions", color="Intent",
        hover_name="Query",
        hover_data={"Impressions": True, "Clicks": True, "CTR": ":.2f", "Position": ":.1f"},
        color_discrete_map=INTENT_COLORS,
        title="Each bubble = one query (≥5 impressions)",
        height=480,
    )
    bench_x = list(range(1, 31))
    bench_y = [expected_ctr(p) for p in bench_x]
    fig.add_trace(go.Scatter(
        x=bench_x, y=bench_y, mode="lines",
        name="Industry benchmark CTR",
        line=dict(color="#d32f2f", width=1.5, dash="dash"),
    ))
    fig.update_layout(
        xaxis_title="Avg. Position (lower = better)", yaxis_title="CTR %",
        xaxis=dict(range=[0, 31]),
        plot_bgcolor="white", paper_bgcolor="white",
    )
    fig.update_xaxes(gridcolor="#f0f0f0")
    fig.update_yaxes(gridcolor="#f0f0f0")
    st.plotly_chart(fig, use_container_width=True)

    # Quick Wins Table
    st.markdown('<div class="section-header">💡 Prioritized Quick Wins</div>',
                unsafe_allow_html=True)
    st.markdown("**Opportunity Score** = estimated additional clicks if CTR reaches benchmark for current position.")

    if len(stats.top_opps) > 0:
        st.dataframe(
            stats.top_opps.style
            .background_gradient(subset=["Opportunity Score"], cmap="YlOrRd")
            .background_gradient(subset=["Impressions"],       cmap="Blues")
            .format({
                "CTR":               "{:.2f}%",
                "Expected CTR":      "{:.1f}%",
                "CTR Gap":           "{:.1f}pp",
                "Opportunity Score": "{:.1f}",
                "Position":          "{:.1f}",
            }),
            use_container_width=True, height=500,
        )
        st.markdown(
            f'<div class="alert-green">Total estimated missed clicks: '
            f'<strong>~{int(stats.total_opportunity):,}</strong>. '
            f'Fixing title tags for the top 10 queries can recover a significant share at zero cost.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("No opportunity data — check that Queries.csv has Position and CTR columns.")
