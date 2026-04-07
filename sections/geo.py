import streamlit as st
import plotly.express as px

def render(countries, top_country, _):
    st.markdown(f'<div class="section-header">{_("🌍 Geographic Performance")}</div>', unsafe_allow_html=True)

    countries_top = countries.nlargest(10, "Clicks").copy()

    col_geo1, col_geo2 = st.columns([2, 1])
    with col_geo1:
        fig = px.bar(
            countries_top, x="Country", y="Clicks",
            color="CTR", color_continuous_scale="RdYlGn",
            title=_("Top 10 countries — color = CTR%"), text="Clicks",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(height=360, margin=dict(t=40, b=10), plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col_geo2:
        st.markdown(_("**Country CTR breakdown**"))
        st.dataframe(
            countries_top[["Country", "Clicks", "Impressions", "CTR", "Position"]]
            .style
            .format({"CTR": "{:.2f}%", "Position": "{:.1f}"})
            .background_gradient(subset=["CTR"], cmap="RdYlGn"),
            height=360, use_container_width=True,
        )

    if top_country is not None and len(countries_top) > 1:
        top_pct = 100 * top_country["Clicks"] / countries_top["Clicks"].sum()
        others  = countries_top[countries_top["Country"] != top_country["Country"]]
        high_ctr = others[others["CTR"] > others["CTR"].mean()]
        if top_pct > 75 and len(high_ctr) > 0:
            names = ", ".join(high_ctr["Country"].tolist())
            st.markdown(
                f'<div class="alert-amber">' +
                _("**{c} drives {pct:.0f}% of clicks.** Markets with above-average CTR: **{names}** — geo-targeted content may unlock disproportionate growth here.", c=top_country["Country"], pct=top_pct, names=names) +
                '</div>',
                unsafe_allow_html=True,
            )
