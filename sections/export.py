import streamlit as st
import pandas as pd

def render(top_opps, recs, queries, _):
    st.markdown(f'<div class="section-header">{_("⬇️ Export")}</div>', unsafe_allow_html=True)

    col_e1, col_e2, col_e3 = st.columns(3)

    with col_e1:
        st.download_button(
            _("📥 Quick Wins (CSV)"),
            top_opps.to_csv(index=False).encode("utf-8"),
            "quick_wins.csv", "text/csv",
        )

    with col_e2:
        recs_df = pd.DataFrame(recs, columns=["Emoji", "Priority", "Title", "Description"])
        st.download_button(
            _("📥 Recommendations (CSV)"),
            recs_df.to_csv(index=False).encode("utf-8"),
            "recommendations.csv", "text/csv",
        )

    with col_e3:
        export_cols = [c for c in [
            "Query", "Clicks", "Impressions", "CTR", "Position",
            "Expected CTR", "CTR Gap", "Opportunity Score", "Intent",
        ] if c in queries.columns]
        full_q = queries[export_cols].sort_values("Opportunity Score", ascending=False)
        st.download_button(
            _("📥 All Queries Scored (CSV)"),
            full_q.to_csv(index=False).encode("utf-8"),
            "all_queries_scored.csv", "text/csv",
        )
