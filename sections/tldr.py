import streamlit as st


def render(stats, snippet_opps, cannibal_issues):
    problems = []
    actions  = []

    if stats.zero_click_imp > 0:
        n = int((stats.queries_ranked["Clicks"] == 0).sum()) if "Clicks" in stats.queries_ranked.columns else "?"
        problems.append(
            f"**{stats.zero_click_imp:,} impressions** go to waste — site ranks but users don't click "
            f"(0 clicks on {n} queries)"
        )
        actions.append(
            f"Rewrite title tags for top {min(10, n)} zero-click queries "
            f"→ est. **+{int(stats.total_opportunity * 0.3):,} clicks/period** at zero cost"
        )

    if stats.blog_pct > 50:
        problems.append(
            f"**{stats.blog_pct:.0f}% of clicks** land on blog/informational pages with no purchase path"
        )
        actions.append("Add product CTAs to every blog post → convert existing traffic without new content")

    if stats.mobile_pos is not None and stats.desktop_pos is not None \
            and (stats.desktop_pos - stats.mobile_pos) > 1.5:
        problems.append(
            f"Desktop ranks at **position {stats.desktop_pos:.1f}** vs mobile **{stats.mobile_pos:.1f}** "
            "— B2B buyers can't find the site"
        )
        actions.append("Run desktop technical SEO audit (Core Web Vitals, structured data)")

    if len(snippet_opps) > 0:
        actions.append(
            f"**{len(snippet_opps)} featured snippet opportunities** (pos 2–5, informational) "
            "→ format as Q&A / bullet lists to capture answer boxes"
        )

    if cannibal_issues is not None and len(cannibal_issues) > 0:
        problems.append(
            f"**{len(cannibal_issues)} cannibalizing queries** — multiple pages competing, splitting authority"
        )

    with st.expander("📋 TL;DR — Executive Summary", expanded=True):
        col_p, col_a = st.columns(2)
        with col_p:
            st.markdown("**🔴 Top Problems**")
            for i, p in enumerate(problems[:3], 1):
                st.markdown(f"{i}. {p}")
            if not problems:
                st.markdown("No critical issues found.")
        with col_a:
            st.markdown("**✅ Priority Actions**")
            for i, a in enumerate(actions[:3], 1):
                st.markdown(f"{i}. {a}")

        if stats.total_opportunity > 0:
            st.caption(
                f"Total estimated missed clicks: **~{int(stats.total_opportunity):,}**. "
                f"Quick wins alone could recover "
                f"**{int(stats.total_opportunity * 0.3):,}–{int(stats.total_opportunity * 0.6):,} clicks** "
                "without new content or backlinks."
            )
