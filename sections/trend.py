import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render(chart, prev_chart, query_movers, page_movers, _):
    st.markdown(f'<div class="section-header">{_("📈 Traffic Trend")}</div>', unsafe_allow_html=True)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=chart["Date"], y=chart["Clicks"], name=_("Clicks"),
               marker_color="#1565c0", opacity=0.8),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=chart["Date"], y=chart["Impressions"], name=_("Impressions"),
                   line=dict(color="#ff6b35", width=2), mode="lines+markers"),
        secondary_y=True,
    )
    fig.update_layout(
        height=300, margin=dict(t=10, b=10),
        legend=dict(orientation="h", y=1.15),
        hovermode="x unified",
        plot_bgcolor="white", paper_bgcolor="white",
    )
    fig.update_yaxes(title_text=_("Clicks"),      secondary_y=False, gridcolor="#f0f0f0")
    fig.update_yaxes(title_text=_("Impressions"), secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    if prev_chart is None and query_movers is None and page_movers is None:
        return

    st.markdown(f'<div class="section-header">{_("📊 Period-over-Period Comparison")}</div>', unsafe_allow_html=True)

    if prev_chart is not None:
        fig_cmp = go.Figure()
        fig_cmp.add_trace(go.Scatter(
            x=list(range(len(chart))), y=chart["Clicks"],
            name=_("Current period"), line=dict(color="#1565c0", width=2),
            mode="lines+markers",
        ))
        fig_cmp.add_trace(go.Scatter(
            x=list(range(len(prev_chart))), y=prev_chart["Clicks"],
            name=_("Previous period"), line=dict(color="#bdbdbd", width=2, dash="dash"),
            mode="lines+markers",
        ))
        fig_cmp.update_layout(
            height=280, margin=dict(t=10, b=10),
            hovermode="x unified", plot_bgcolor="white",
            xaxis_title=_("Day"), yaxis_title=_("Clicks"),
            legend=dict(orientation="h", y=1.15),
        )
        fig_cmp.update_xaxes(gridcolor="#f0f0f0")
        fig_cmp.update_yaxes(gridcolor="#f0f0f0")
        st.plotly_chart(fig_cmp, use_container_width=True)

    if query_movers is not None:
        col_gain, col_lose = st.columns(2)
        with col_gain:
            st.markdown(_("**Top growing queries**"))
            gainers = (
                query_movers[query_movers["Clicks_delta"] > 0]
                .nlargest(10, "Clicks_delta")
                [["Query", "Clicks", "Clicks_prev", "Clicks_delta", "Intent"]]
                .reset_index(drop=True)
            )
            gainers.index += 1
            st.dataframe(
                gainers.style
                .background_gradient(subset=["Clicks_delta"], cmap="Greens")
                .format({"Clicks_delta": "+{:.0f}"}),
                use_container_width=True, height=340,
            )
        with col_lose:
            st.markdown(_("**Top declining queries**"))
            losers = (
                query_movers[query_movers["Clicks_delta"] < 0]
                .nsmallest(10, "Clicks_delta")
                [["Query", "Clicks", "Clicks_prev", "Clicks_delta", "Intent"]]
                .reset_index(drop=True)
            )
            losers.index += 1
            st.dataframe(
                losers.style
                .background_gradient(subset=["Clicks_delta"], cmap="Reds_r")
                .format({"Clicks_delta": "{:.0f}"}),
                use_container_width=True, height=340,
            )

    if page_movers is not None:
        st.markdown(_("**Page movers**"))
        pm = (
            page_movers.assign(
                Label=page_movers["Page"]
                .str.replace(r"https?://[^/]+", "", regex=True)
                .str[:70]
            )
            .sort_values("Clicks_delta", key=abs, ascending=False)
            .head(15)[["Label", "Clicks", "Clicks_prev", "Clicks_delta", "Type"]]
            .reset_index(drop=True)
        )
        pm.index += 1
        fig_pm = px.bar(
            pm, x="Clicks_delta", y="Label", orientation="h",
            color="Clicks_delta",
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=0,
            title=_("Click change vs previous period"),
            height=440,
        )
        fig_pm.update_layout(
            margin=dict(t=40, b=10, l=10),
            yaxis=dict(autorange="reversed"),
            plot_bgcolor="white",
        )
        st.plotly_chart(fig_pm, use_container_width=True)

    if query_movers is not None:
        new_q  = query_movers[(query_movers["Clicks_prev"] == 0) & (query_movers["Clicks"] > 0)]\
                     .nlargest(5, "Clicks")[["Query", "Clicks", "Impressions", "Intent"]]
        lost_q = query_movers[(query_movers["Clicks"] == 0) & (query_movers["Clicks_prev"] > 0)]\
                     .nlargest(5, "Clicks_prev")[["Query", "Clicks_prev", "Intent"]]

        col_new, col_lost = st.columns(2)
        with col_new:
            if len(new_q) > 0:
                st.markdown(_("**New queries this period**"))
                st.dataframe(new_q.reset_index(drop=True),
                             use_container_width=True, hide_index=True)
        with col_lost:
            if len(lost_q) > 0:
                st.markdown(_("**Queries that dropped out**"))
                st.dataframe(lost_q.reset_index(drop=True),
                             use_container_width=True, hide_index=True)
