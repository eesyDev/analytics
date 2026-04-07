import streamlit as st
import config
from data_loader import load_current, load_previous, load_cannibal
from analysis import (
    classify_intent, tag_page, compute_opportunity,
    compute_stats, compute_length, compute_deltas, compute_movers,
    compute_cannibalization,
)
from sections import tldr, kpis, trend, findings, opportunities
from sections import cannibalization, intent, pages, positions, devices, geo, hotjar
from sections import recommendations, export

st.set_page_config(page_title="SEO Performance Audit", page_icon="📊", layout="wide")
st.markdown(config.CSS, unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    client_name = st.text_input("Client / Site Name", value="My Site")

    with st.expander("Intent Classification"):
        brand_raw   = st.text_area("Brand terms (one per line)", "")
        info_raw    = st.text_area("Informational terms (one per line)",
                        "how to\nwhat is\nmake money\ndepreciation\nfinancing\n"
                        "how long\nhow much\ncan you\nis a\nstarting a\n"
                        "clearing land\nhourly rate\nguide\ntips\nvs\nreviews")
        blog_kw_raw = st.text_area("URL keywords → Blog page (one per line)",
                        "how-to\nwhat-is\nguide\ntips\nblog\narticle")

    st.divider()
    st.subheader("📁 Current Period — GSC")
    st.caption("Google Search Console → Performance → Export CSV")
    f_queries   = st.file_uploader("Queries.csv",             type="csv", key="q")
    f_pages     = st.file_uploader("Pages.csv",               type="csv", key="p")
    f_devices   = st.file_uploader("Devices.csv",             type="csv", key="d")
    f_countries = st.file_uploader("Countries.csv",           type="csv", key="c")
    f_chart     = st.file_uploader("Chart.csv (time series)", type="csv", key="ch")

    st.divider()
    st.subheader("📁 Previous Period — GSC")
    st.caption("Same exports for the prior period (WoW / MoM)")
    f_prev_queries = st.file_uploader("Queries.csv (prev)",  type="csv", key="pq")
    f_prev_pages   = st.file_uploader("Pages.csv (prev)",    type="csv", key="pp")
    f_prev_chart   = st.file_uploader("Chart.csv (prev)",    type="csv", key="pch")

    st.divider()
    st.subheader("🔍 Cannibalization")
    st.caption("GSC → Performance → add Pages + Queries dimensions → export")
    f_query_page = st.file_uploader("Query+Page export CSV", type="csv", key="qp")

    st.divider()
    st.subheader("🎥 Hotjar (optional)")
    f_hotjar     = st.file_uploader("Funnel export CSV",     type="csv",                key="hj")
    f_hm_home    = st.file_uploader("Homepage heatmap",      type=["png","jpg","jpeg"], key="hm1")
    f_hm_product = st.file_uploader("Product page heatmap",  type=["png","jpg","jpeg"], key="hm2")
    f_hm_cart    = st.file_uploader("Cart page heatmap",     type=["png","jpg","jpeg"], key="hm3")

    st.divider()
    st.caption("Universal SEO Audit Tool · Built with Streamlit + Plotly")


# ── Load data ─────────────────────────────────────────────────────────────────
try:
    queries, pages_df, devices_df, countries_df, chart = load_current({
        "queries": f_queries, "pages": f_pages, "devices": f_devices,
        "countries": f_countries, "chart": f_chart,
    })
except FileNotFoundError:
    st.warning("⬆️  Upload GSC CSV files in the sidebar to get started.")
    st.info("Or place CSV files in the `data/` directory next to app.py.")
    st.stop()

prev_queries, prev_pages, prev_chart = load_previous({
    "queries": f_prev_queries, "pages": f_prev_pages, "chart": f_prev_chart,
})
cannibal_df = load_cannibal(f_query_page)


# ── Analysis ──────────────────────────────────────────────────────────────────
brand_terms = [t.strip().lower() for t in brand_raw.split("\n")   if t.strip()]
info_terms  = [t.strip().lower() for t in info_raw.split("\n")    if t.strip()]
blog_kws    = [t.strip().lower() for t in blog_kw_raw.split("\n") if t.strip()]

queries["Intent"] = queries["Query"].apply(lambda q: classify_intent(q, brand_terms, info_terms))
pages_df["Type"]  = pages_df["Page"].apply(lambda u: tag_page(u, blog_kws))

queries        = compute_opportunity(queries)
stats          = compute_stats(queries, pages_df, chart, devices_df, countries_df)
length_summary, snippet_opps = compute_length(queries)
deltas         = compute_deltas(stats, prev_queries, prev_chart)
query_movers, page_movers = compute_movers(queries, prev_queries, pages_df, prev_pages)
cannibal_issues = compute_cannibalization(cannibal_df)

has_prev = any([f_prev_queries, f_prev_pages, f_prev_chart])


# ── Layout ────────────────────────────────────────────────────────────────────
st.markdown(f"## 📊 {client_name} — SEO Performance Audit")
st.markdown(
    f"**Period:** {stats.date_range} &nbsp;|&nbsp; **Source:** Google Search Console"
    f" &nbsp;|&nbsp; **Queries analyzed:** {len(queries):,}",
    unsafe_allow_html=True,
)

tldr.render(stats, snippet_opps, cannibal_issues)
st.divider()

kpis.render(stats, deltas)
trend.render(chart, prev_chart if has_prev else None,
             query_movers if has_prev else None,
             page_movers  if has_prev else None)
findings.render(stats, queries)
opportunities.render(queries, stats)
cannibalization.render(cannibal_df, cannibal_issues)
intent.render(stats.intent_summary, stats.comm_imp_pct)
pages.render(pages_df)
positions.render(stats.queries_ranked, queries, length_summary, snippet_opps)
devices.render(devices_df, stats.mobile_pos, stats.desktop_pos)
geo.render(countries_df, stats.top_country)
hotjar.render(f_hotjar, f_hm_home, f_hm_product, f_hm_cart)

recs = recommendations.render(stats, cannibal_issues, countries_df)
export.render(stats.top_opps, recs, queries)

st.divider()
st.markdown(
    f"<small style='color:#888'>Audit generated · {stats.date_range} · "
    "Source: Google Search Console · Built with Streamlit + Plotly</small>",
    unsafe_allow_html=True,
)
