import streamlit as st

def render(stats, deltas, _):
    st.markdown(f'<div class="section-header">{_("📌 KPIs")}</div>', unsafe_allow_html=True)

    def delta_color(val, inverse=False):
        if val is None:
            return "off"
        good = val >= 0
        if inverse:
            good = not good
        return "normal" if good else "inverse"

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric(_("Total Clicks"),           f"{stats.total_clicks:,}",
              delta=deltas.clicks_str,
              delta_color=delta_color(deltas.clicks_val))
    k2.metric(_("Total Impressions"),      f"{stats.total_impressions:,}",
              delta=deltas.imps_str,
              delta_color=delta_color(deltas.imps_val))
    k3.metric(_("Weighted CTR"),           f"{stats.weighted_ctr:.2f}%",
              delta=deltas.ctr_str,
              delta_color=delta_color(deltas.ctr_val),
              help=_("Impressions-weighted CTR — more accurate than simple average"))
    k4.metric(_("Weighted Avg Position"),  f"{stats.weighted_pos:.1f}",
              delta=deltas.pos_str,
              delta_color=delta_color(deltas.pos_val, inverse=True),
              help=_("Lower = better. Green delta = position improved."))
    k5.metric(_("Estimated Missed Clicks"), f"~{int(stats.total_opportunity):,}",
              help=_("Additional clicks if all queries reached benchmark CTR for their position"))
    st.divider()
