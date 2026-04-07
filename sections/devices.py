import streamlit as st
import plotly.express as px


def render(devices, mobile_pos, desktop_pos):
    st.markdown('<div class="section-header">📱 Device Performance</div>', unsafe_allow_html=True)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        fig_dev = px.bar(
            devices, x="Device", y=["Clicks", "Impressions"],
            barmode="group",
            color_discrete_sequence=["#1565c0", "#ff6b35"],
            title="Clicks vs Impressions by device",
        )
        fig_dev.update_layout(height=320, margin=dict(t=40, b=10), plot_bgcolor="white")
        st.plotly_chart(fig_dev, use_container_width=True)

    with col_d2:
        fig_pos = px.bar(
            devices, x="Device", y="Position",
            color="Device",
            color_discrete_sequence=["#1565c0", "#388e3c", "#f9a825"],
            title="Avg. ranking position by device (lower = better)",
            text="Position",
        )
        fig_pos.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_pos.update_layout(
            height=320, margin=dict(t=40, b=10),
            showlegend=False, plot_bgcolor="white",
        )
        fig_pos.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_pos, use_container_width=True)

    if mobile_pos is not None and desktop_pos is not None:
        gap = desktop_pos - mobile_pos
        if gap > 2:
            st.markdown(
                f'<div class="alert-red">Desktop position {desktop_pos:.1f} vs mobile {mobile_pos:.1f} '
                f'— gap of {gap:.1f} positions. Run a dedicated desktop technical audit: '
                "Core Web Vitals, structured data, PageSpeed.</div>",
                unsafe_allow_html=True,
            )
        elif gap > 0.5:
            st.markdown(
                f'<div class="alert-amber">Desktop ({desktop_pos:.1f}) slightly weaker than '
                f"mobile ({mobile_pos:.1f}). Monitor for widening.</div>",
                unsafe_allow_html=True,
            )
