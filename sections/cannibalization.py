import streamlit as st

def render(cannibal_df, cannibal_issues, _):
    st.markdown(f'<div class="section-header">{_("⚠️ Keyword Cannibalization")}</div>', unsafe_allow_html=True)

    if cannibal_df is None:
        st.markdown(
            f'<div class="alert-blue">{_("**To detect cannibalization:** In GSC → Performance, click the *Pages* tab, add the *Queries* dimension, and export. Upload the result in the sidebar.")}</div>',
            unsafe_allow_html=True,
        )
        return

    st.caption(_("Queries where 2+ pages compete for the same keyword — Google picks one, others dilute authority."))

    if cannibal_issues is None or len(cannibal_issues) == 0:
        st.markdown(f'<div class="alert-green">{_("No cannibalization detected.")}</div>', unsafe_allow_html=True)
        return

    c1, c2, c3 = st.columns(3)
    c1.metric(_("Cannibalizing queries"),  len(cannibal_issues))
    c2.metric(_("Impressions at risk"),    f"{int(cannibal_issues['Impressions'].sum()):,}")
    c3.metric(_("Clicks at risk"),         f"{int(cannibal_issues['Clicks'].sum()):,}")

    st.markdown(_("**Top cannibalizing queries (by impressions)**"))
    st.dataframe(
        cannibal_issues.head(20)[["Query", "Pages", "Impressions", "Clicks", "Competing Pages"]]
        .style.background_gradient(subset=["Impressions"], cmap="YlOrRd"),
        use_container_width=True, height=420,
    )
    st.markdown(
        f'<div class="alert-amber">{_("**How to fix:** For each group, pick one canonical page and consolidate content there. 301-redirect or noindex the weaker pages.")}</div>',
        unsafe_allow_html=True,
    )
