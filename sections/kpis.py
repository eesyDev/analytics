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

    cols = st.columns(6 if stats.anonymized_clicks > 0 else 5)
    cols[0].metric(_("Total Clicks"),           f"{stats.total_clicks:,}",
              delta=deltas.clicks_str, delta_color=delta_color(deltas.clicks_val))
    cols[1].metric(_("Total Impressions"),      f"{stats.total_impressions:,}",
              delta=deltas.imps_str, delta_color=delta_color(deltas.imps_val))
    cols[2].metric(_("Weighted CTR"),           f"{stats.weighted_ctr:.2f}%",
              delta=deltas.ctr_str, delta_color=delta_color(deltas.ctr_val),
              help=_("Impressions-weighted CTR — more accurate than simple average"))
    cols[3].metric(_("Weighted Avg Position"),  f"{stats.weighted_pos:.1f}",
              delta=deltas.pos_str, delta_color=delta_color(deltas.pos_val, inverse=True),
              help=_("Lower = better. Green delta = position improved."))
    cols[4].metric(_("Estimated Missed Clicks"), f"~{int(stats.total_opportunity):,}",
              help=_("Additional clicks if all queries reached benchmark CTR for their position"))
              
    if stats.anonymized_clicks > 0:
        cols[5].metric(
            _("Hidden (Anonymized) Clicks"), f"{stats.anonymized_clicks:,} ({stats.anonymized_pct:.0f}%)",
            help=_("Clicks not attributed to any specific search query due to Google privacy limits.")
        )

    st.caption(_(
        "⚠️ GSC sampling: on high-traffic properties Google may show only a fraction of actual data. "
        "Treat all figures as directional — export to BigQuery for exact counts."
    ))
    st.divider()
