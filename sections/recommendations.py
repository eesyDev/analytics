import streamlit as st
from config import PRIORITY_COLOR


def render(stats, cannibal_issues, countries):
    st.markdown('<div class="section-header">✅ Prioritized Recommendations</div>',
                unsafe_allow_html=True)

    recs = []

    if stats.zero_click_imp > 0:
        recs.append(("🔴", "URGENT", "Rewrite title tags & meta descriptions for zero-click queries",
            f"{stats.zero_click_imp:,} impressions, 0 clicks. Start with Quick Wins table top 10 — "
            "these already rank, fixing CTR costs nothing."))

    if stats.blog_pct > 50:
        recs.append(("🔴", "URGENT", "Add product CTAs to all informational / blog pages",
            f"{stats.blog_pct:.0f}% of clicks land on blog pages with no path to purchase. "
            "Add contextually relevant product banners and internal links to every article."))

    if stats.mobile_pos is not None and stats.desktop_pos is not None \
            and (stats.desktop_pos - stats.mobile_pos) > 2:
        recs.append(("🟠", "HIGH", "Desktop SEO technical audit",
            f"Desktop ranks at {stats.desktop_pos:.1f} vs mobile {stats.mobile_pos:.1f}. "
            "Audit Core Web Vitals, structured data, and PageSpeed for desktop."))

    recs.append(("🟠", "HIGH", "Set up Hotjar conversion funnel tracking",
        "Install: Product → Add to Cart → Checkout → Order confirmation. "
        "This identifies the single biggest conversion bottleneck."))

    if stats.comm_imp_pct < 30:
        recs.append(("🟠", "HIGH", "Create dedicated commercial landing pages",
            f"Only {stats.comm_imp_pct:.0f}% of impressions are commercial (buyer) queries. "
            'Build pages targeting product + intent keywords ("X for sale", "X price", etc.).'))

    if cannibal_issues is not None and len(cannibal_issues) > 0:
        recs.append(("🟠", "HIGH", "Fix keyword cannibalization",
            f"{len(cannibal_issues)} queries have 2+ competing pages. "
            "Consolidate to one canonical per topic, redirect the rest."))

    if stats.top_country is not None and len(countries) > 1:
        countries_top = countries.nlargest(10, "Clicks")
        high_ctr_intl = countries_top[
            (countries_top["Country"] != stats.top_country["Country"]) &
            (countries_top["CTR"] > countries_top["CTR"].mean())
        ]
        if len(high_ctr_intl) > 0:
            names = ", ".join(high_ctr_intl["Country"].tolist())
            recs.append(("🟢", "LOW", "Expand into high-CTR international markets",
                f"{names} show above-average CTR. "
                "Geo-targeted content or hreflang could yield disproportionate growth."))

    for emoji, priority, title, desc in recs:
        cls = PRIORITY_COLOR.get(priority, "alert-blue")
        st.markdown(
            f'<div class="{cls}"><strong>{emoji} {priority} — {title}</strong><br>{desc}</div>',
            unsafe_allow_html=True,
        )

    return recs
