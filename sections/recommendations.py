import streamlit as st
from config import PRIORITY_COLOR

def render(stats, cannibal_issues, countries, _):
    st.markdown(f'<div class="section-header">{_("✅ Prioritized Recommendations")}</div>', unsafe_allow_html=True)

    recs = []

    if stats.zero_click_imp > 0:
        recs.append(("🔴", _("URGENT"), _("Rewrite title tags & meta descriptions for zero-click queries"),
            _("{imp:,} impressions, 0 clicks. Start with Quick Wins table top 10 — these already rank, fixing CTR costs nothing.", imp=stats.zero_click_imp)))

    if stats.blog_pct > 50:
        recs.append(("🔴", _("URGENT"), _("Add product CTAs to all informational / blog pages"),
            _("{pct:.0f}% of clicks land on blog pages with no path to purchase. Add contextually relevant product banners and internal links to every article.", pct=stats.blog_pct)))

    if stats.mobile_pos is not None and stats.desktop_pos is not None \
            and (stats.desktop_pos - stats.mobile_pos) > 2:
        recs.append(("🟠", _("HIGH"), _("Desktop SEO technical audit"),
            _("Desktop ranks at {dt:.1f} vs mobile {mob:.1f}. Audit Core Web Vitals, structured data, and PageSpeed for desktop.", dt=stats.desktop_pos, mob=stats.mobile_pos)))

    recs.append(("🟠", _("HIGH"), _("Set up Hotjar conversion funnel tracking"),
        _("Install: Product → Add to Cart → Checkout → Order confirmation. This identifies the single biggest conversion bottleneck.")))

    if stats.comm_imp_pct < 30:
        recs.append(("🟠", _("HIGH"), _("Create dedicated commercial landing pages"),
            _('Only {pct:.0f}% of impressions are commercial (buyer) queries. Build pages targeting product + intent keywords ("X for sale", "X price", etc.).', pct=stats.comm_imp_pct)))

    if cannibal_issues is not None and len(cannibal_issues) > 0:
        recs.append(("🟠", _("HIGH"), _("Fix keyword cannibalization"),
            _("{n} queries have 2+ competing pages. Consolidate to one canonical per topic, redirect the rest.", n=len(cannibal_issues))))

    if stats.top_country is not None and len(countries) > 1:
        countries_top = countries.nlargest(10, "Clicks")
        high_ctr_intl = countries_top[
            (countries_top["Country"] != stats.top_country["Country"]) &
            (countries_top["CTR"] > countries_top["CTR"].mean())
        ]
        if len(high_ctr_intl) > 0:
            names = ", ".join(high_ctr_intl["Country"].tolist())
            recs.append(("🟢", _("LOW"), _("Expand into high-CTR international markets"),
                _("{names} show above-average CTR. Geo-targeted content or hreflang could yield disproportionate growth.", names=names)))

    # Display dynamically
    color_map = {
        _("URGENT"): "alert-red",
        _("HIGH"): "alert-amber",
        _("LOW"): "alert-green"
    }

    for emoji, priority, title, desc in recs:
        cls = color_map.get(priority, "alert-blue")
        st.markdown(
            f'<div class="{cls}"><strong>{emoji} {priority} — {title}</strong><br>{desc}</div>',
            unsafe_allow_html=True,
        )

    return recs
