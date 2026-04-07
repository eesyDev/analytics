import streamlit as st


def render(cannibal_df, cannibal_issues):
    st.markdown('<div class="section-header">⚠️ Keyword Cannibalization</div>',
                unsafe_allow_html=True)

    if cannibal_df is None:
        st.markdown(
            '<div class="alert-blue"><strong>To detect cannibalization:</strong> '
            "In GSC → Performance, click the <em>Pages</em> tab, add the <em>Queries</em> "
            "dimension, and export. Upload the result as \"Query+Page export CSV\" in the sidebar."
            "</div>",
            unsafe_allow_html=True,
        )
        return

    st.caption("Queries where 2+ pages compete for the same keyword — Google picks one, others dilute authority.")

    if cannibal_issues is None or len(cannibal_issues) == 0:
        st.markdown('<div class="alert-green">No cannibalization detected.</div>',
                    unsafe_allow_html=True)
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Cannibalizing queries",  len(cannibal_issues))
    c2.metric("Impressions at risk",    f"{int(cannibal_issues['Impressions'].sum()):,}")
    c3.metric("Clicks at risk",         f"{int(cannibal_issues['Clicks'].sum()):,}")

    st.markdown("**Top cannibalizing queries (by impressions)**")
    st.dataframe(
        cannibal_issues.head(20)[["Query", "Pages", "Impressions", "Clicks", "Competing Pages"]]
        .style.background_gradient(subset=["Impressions"], cmap="YlOrRd"),
        use_container_width=True, height=420,
    )
    st.markdown(
        '<div class="alert-amber"><strong>How to fix:</strong> For each group, pick one '
        "canonical page and consolidate content there. 301-redirect or noindex the weaker "
        "pages, and add internal links pointing to the canonical.</div>",
        unsafe_allow_html=True,
    )
