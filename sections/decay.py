import streamlit as st
import plotly.express as px

def render(page_movers, _):
    st.markdown(f'<div class="section-header">{_("📉 Content Decay: Pages Losing Traffic")}</div>', unsafe_allow_html=True)
    st.caption(_("Identify pages that have lost the most traffic compared to the previous period. These pages likely need content updates, new links, or re-optimization."))

    if page_movers is None or len(page_movers) == 0:
        st.info(_("No previous period data available to compute content decay."))
        return

    # Filter for pages that actually lost clicks
    decaying_pages = (
        page_movers[page_movers["Clicks_delta"] < 0]
        .copy()
    )

    if len(decaying_pages) == 0:
        st.success(_("Great news! No pages lost traffic compared to the previous period."))
        return

    # Sort by the sheer volume of lost traffic
    decaying_pages = decaying_pages.sort_values("Clicks_delta", ascending=True)

    decaying_pages["Label"] = (
        decaying_pages["Page"]
        .str.replace(r"https?://[^/]+", "", regex=True)
        .str[:70]
    )

    top_losers = decaying_pages.head(20).reset_index(drop=True)
    top_losers.index += 1

    col1, col2 = st.columns([3, 2])

    with col1:
        fig = px.bar(
            top_losers,
            x="Clicks_delta",
            y="Label",
            orientation="h",
            color="Clicks_delta",
            color_continuous_scale="Reds_r",
            title=_("Top 20 most degraded pages"),
            height=500
        )
        fig.update_layout(
            margin=dict(t=40, b=10, l=10),
            yaxis=dict(autorange="reversed"),
            plot_bgcolor="white"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(_("**Priority Rewrite List**"))
        st.dataframe(
            top_losers[["Label", "Clicks_prev", "Clicks_delta", "Type"]]
            .style
            .format({"Clicks_delta": "{:.0f}", "Clicks_prev": "{:.0f}"})
            .background_gradient(subset=["Clicks_delta"], cmap="Reds_r"),
            height=500, use_container_width=True
        )
