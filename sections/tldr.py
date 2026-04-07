import streamlit as st

def render(stats, snippet_opps, cannibal_issues, _):
    problems = []
    actions  = []

    if stats.zero_click_imp > 0:
        n = int((stats.queries_ranked["Clicks"] == 0).sum()) if "Clicks" in stats.queries_ranked.columns else "?"
        problems.append(_("**{count:,} impressions** go to waste — site ranks but users don't click (0 clicks on {n} queries)", count=stats.zero_click_imp, n=n))
        actions.append(_("Rewrite title tags for top {n} zero-click queries → est. **+{opp:,} clicks/period** at zero cost", n=min(10, n if isinstance(n, int) else 10), opp=int(stats.total_opportunity * 0.3)))

    if stats.blog_pct > 50:
        problems.append(_("**{pct:.0f}% of clicks** land on blog/informational pages with no purchase path", pct=stats.blog_pct))
        actions.append(_("Add product CTAs to every blog post → convert existing traffic without new content"))

    if stats.mobile_pos is not None and stats.desktop_pos is not None \
            and (stats.desktop_pos - stats.mobile_pos) > 1.5:
        problems.append(_("Desktop ranks at **position {dt:.1f}** vs mobile **{mob:.1f}** — B2B buyers can't find the site", dt=stats.desktop_pos, mob=stats.mobile_pos))
        actions.append(_("Run desktop technical SEO audit (Core Web Vitals, structured data)"))

    if len(snippet_opps) > 0:
        actions.append(_("**{count} featured snippet opportunities** (pos 2–5, informational) → format as Q&A / bullet lists to capture answer boxes", count=len(snippet_opps)))

    if cannibal_issues is not None and len(cannibal_issues) > 0:
        problems.append(_("**{count} cannibalizing queries** — multiple pages competing, splitting authority", count=len(cannibal_issues)))

    with st.expander(_("📋 TL;DR — Executive Summary"), expanded=True):
        col_p, col_a = st.columns(2)
        with col_p:
            st.markdown(_("**🔴 Top Problems**"))
            for i, p in enumerate(problems[:3], 1):
                st.markdown(f"{i}. {p}")
            if not problems:
                st.markdown(_("No critical issues found."))
        with col_a:
            st.markdown(_("**✅ Priority Actions**"))
            for i, a in enumerate(actions[:3], 1):
                st.markdown(f"{i}. {a}")

        if stats.total_opportunity > 0:
            st.caption(_("Total estimated missed clicks: **~{opp:,}**. Quick wins alone could recover **{r1:,}–{r2:,} clicks** without new content or backlinks.", opp=int(stats.total_opportunity), r1=int(stats.total_opportunity * 0.3), r2=int(stats.total_opportunity * 0.6)))
