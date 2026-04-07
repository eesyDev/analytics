import streamlit as st
import plotly.express as px
from config import INTENT_COLORS

def render(intent_summary, comm_imp_pct, _):
    st.markdown(f'<div class="section-header">{_("🎯 Search Intent Distribution")}</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        fig_pie = px.pie(
            intent_summary, values="Impressions", names="Intent",
            color="Intent", color_discrete_map=INTENT_COLORS,
            hole=0.45, title=_("Share of impressions by intent"),
        )
        fig_pie.update_traces(textinfo="percent+label")
        fig_pie.update_layout(height=340, margin=dict(t=40, b=10), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        fig_bar = px.bar(
            intent_summary, x="Intent", y=["Impressions", "Clicks"],
            barmode="group",
            color_discrete_sequence=["#1565c0", "#ff6b35"],
            title=_("Impressions vs Clicks by intent"),
        )
        fig_bar.update_layout(height=340, margin=dict(t=40, b=10), plot_bgcolor="white")
        st.plotly_chart(fig_bar, use_container_width=True)

    if comm_imp_pct < 30:
        st.markdown(
            f'<div class="alert-amber">' +
            _("Commercial / Product queries represent only **{pct:.0f}%** of impressions. The SEO strategy is optimised for awareness, not purchase intent.", pct=comm_imp_pct) +
            '</div>',
            unsafe_allow_html=True,
        )
