import io
import time
import streamlit as st
import config
from data_loader import load_current, load_previous, load_cannibal, load_ga4
from analysis import (
    classify_intent, tag_page, compute_opportunity,
    compute_stats, compute_length, compute_deltas, compute_movers,
    compute_cannibalization, compute_page_opportunity,
)
from sections import tldr, kpis, trend, findings, opportunities
from sections import cannibalization, intent, pages, positions, devices, geo, hotjar, decay
from sections import recommendations, export, competitor, ai_summary, content_auditor
from i18n import get_text
import i18n
import db

st.set_page_config(page_title="SEO Audit", page_icon="📊", layout="wide")
st.markdown(config.CSS, unsafe_allow_html=True)

import auth
auth.check_auth()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Branding
    st.markdown('<p class="sidebar-logo">📊 SEO Audit Tool</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-tagline">Powered by GSC · GA4 · Claude AI</p>', unsafe_allow_html=True)

    st.divider()

    # User + sign out
    col_u, col_b = st.columns([3, 1])
    with col_u:
        st.markdown(f'<p class="sidebar-user">👤 {st.session_state["email"]}</p>', unsafe_allow_html=True)
    with col_b:
        if st.button("↩", help="Sign Out", use_container_width=True):
            auth.logout()
            st.rerun()

    # Language (hidden for now, kept for future)
    lang_choice = "EN"
    _ = lambda key, *args, **kwargs: i18n.get_text(lang_choice, key, *args, **kwargs)

    st.divider()

    # Project selector
    st.markdown('<p class="nav-label">Project</p>', unsafe_allow_html=True)
    projects = db.list_projects(st.session_state["user_id"])
    proj_options = ["🆕 New project..."] + projects
    default_index = 1 if projects else 0
    selected_proj = st.selectbox("", proj_options, index=default_index, label_visibility="collapsed", key="proj_select")
    if selected_proj == "🆕 New project...":
        client_name = st.text_input("", value="My Site", placeholder="Project name", label_visibility="collapsed", key="proj_name")
    else:
        client_name = selected_proj

    st.divider()

    # Navigation
    st.markdown('<p class="nav-label">Navigation</p>', unsafe_allow_html=True)
    page = st.radio(
        "",
        [
            "⬆️  Setup & Upload",
            "📈  Overview",
            "🔍  Traffic",
            "📄  Pages & Keywords",
            "👥  Audience",
            "🖱️  Behavioral",
            "⚔️  Competitors",
            "🧠  Content Audit",
            "📋  Report",
        ],
        label_visibility="collapsed",
        key="nav",
    )

    st.divider()

    # Settings
    with st.expander("⚙️ Settings"):
        brand_raw   = st.text_area(_("Brand terms (one per line)"), "", key="brand")
        info_raw    = st.text_area(
            _("Informational terms (one per line)"),
            _("how to\nwhat is\nmake money\ndepreciation\nfinancing\nhow long\nhow much\ncan you\nis a\nstarting a\nclearing land\nhourly rate\nguide\ntips\nvs\nreviews"),
            key="info",
        )
        blog_kw_raw = st.text_area(
            _("URL keywords → Blog page (one per line)"),
            _("how-to\nwhat-is\nguide\ntips\nblog\narticle"),
            key="blog",
        )

    st.markdown('<p class="sidebar-tagline" style="margin-top:1rem">Built with Streamlit + Plotly</p>', unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
uid = st.session_state["user_id"]

@st.cache_data(show_spinner=False)
def get_b(uid, project_name, fname):
    return db.download_file(f"{uid}/{project_name}/{fname}")

def load_b(fname):
    b = get_b(uid, client_name, fname)
    return io.BytesIO(b) if b else None


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: Setup & Upload
# ═══════════════════════════════════════════════════════════════════════════════
if page == "⬆️  Setup & Upload":
    st.markdown(
        '<div class="page-header"><h2>⬆️ Setup & Upload</h2>'
        '<p class="meta">Upload your data exports to start the audit. Files are saved to the cloud per project.</p></div>',
        unsafe_allow_html=True,
    )

    if selected_proj == "🆕 New project..." and (not client_name or client_name.strip() == ""):
        st.warning("Enter a project name in the sidebar first.")
        st.stop()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="upload-card"><p class="upload-card-title">📊 Current Period — Google Search Console</p><p class="upload-card-hint">GSC → Performance → Queries / Pages / Devices / Countries / Date chart → Export CSV</p>', unsafe_allow_html=True)
        f_queries   = st.file_uploader("Queries.csv",   type="csv", key="q")
        f_pages     = st.file_uploader("Pages.csv",     type="csv", key="p")
        f_devices   = st.file_uploader("Devices.csv",   type="csv", key="d")
        f_countries = st.file_uploader("Countries.csv", type="csv", key="c")
        f_chart     = st.file_uploader("Chart.csv (date trend)", type="csv", key="ch")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="upload-card"><p class="upload-card-title">📅 Previous Period (optional)</p><p class="upload-card-hint">Same GSC exports from the prior period — enables WoW / MoM comparison.</p>', unsafe_allow_html=True)
        f_prev_queries = st.file_uploader("Queries.csv", type="csv", key="pq")
        f_prev_pages   = st.file_uploader("Pages.csv",   type="csv", key="pp")
        f_prev_chart   = st.file_uploader("Chart.csv",   type="csv", key="pch")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="upload-card"><p class="upload-card-title">🔬 Extra Data (optional)</p><p class="upload-card-hint">Cannibalization report, Google Analytics 4, Hotjar funnels and heatmaps.</p>', unsafe_allow_html=True)
        f_query_page = st.file_uploader("Cannibalization: Query+Page CSV", type="csv", key="qp")
        f_ga4        = st.file_uploader("GA4: Landing Pages CSV (Sessions, Revenue)", type="csv", key="ga4")
        st.caption("Hotjar")
        f_hotjar_up     = st.file_uploader("Funnel CSV",           type="csv",                key="hj")
        f_hm_home_up    = st.file_uploader("Homepage heatmap",     type=["png","jpg","jpeg"], key="hm1")
        f_hm_product_up = st.file_uploader("Product page heatmap", type=["png","jpg","jpeg"], key="hm2")
        f_hm_cart_up    = st.file_uploader("Cart page heatmap",    type=["png","jpg","jpeg"], key="hm3")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="upload-card"><p class="upload-card-title">⚔️ Competitors (optional)</p><p class="upload-card-hint">Used in the Competitors tab — paste URLs to compare on-page SEO signals.</p>', unsafe_allow_html=True)
        competitor_urls_raw = st.text_area(
            "URLs to analyze (your site first)",
            placeholder="https://yoursite.com/page\nhttps://competitor1.com/page\nhttps://competitor2.com/page",
            height=120,
            key="competitor_urls",
            label_visibility="collapsed",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("💾 Save all files to cloud", type="primary", use_container_width=True):
        if not client_name or client_name.strip() in ("", "🆕 New project..."):
            st.error("Please enter a project name in the sidebar.")
        else:
            with st.spinner("Uploading to Supabase…"):
                _uid = st.session_state["user_id"]
                if f_queries:     db.upload_file(f"{_uid}/{client_name}/queries.csv",      f_queries.getvalue())
                if f_pages:       db.upload_file(f"{_uid}/{client_name}/pages.csv",        f_pages.getvalue())
                if f_devices:     db.upload_file(f"{_uid}/{client_name}/devices.csv",      f_devices.getvalue())
                if f_countries:   db.upload_file(f"{_uid}/{client_name}/countries.csv",    f_countries.getvalue())
                if f_chart:       db.upload_file(f"{_uid}/{client_name}/chart.csv",        f_chart.getvalue())
                if f_prev_queries:db.upload_file(f"{_uid}/{client_name}/prev_queries.csv", f_prev_queries.getvalue())
                if f_prev_pages:  db.upload_file(f"{_uid}/{client_name}/prev_pages.csv",   f_prev_pages.getvalue())
                if f_prev_chart:  db.upload_file(f"{_uid}/{client_name}/prev_chart.csv",   f_prev_chart.getvalue())
                if f_query_page:  db.upload_file(f"{_uid}/{client_name}/query_page.csv",   f_query_page.getvalue())
                if f_ga4:         db.upload_file(f"{_uid}/{client_name}/ga4.csv",          f_ga4.getvalue())
                if f_hotjar_up:   db.upload_file(f"{_uid}/{client_name}/funnel.csv",       f_hotjar_up.getvalue())
                if f_hm_home_up:  db.upload_file(f"{_uid}/{client_name}/hm_home",          f_hm_home_up.getvalue(), f_hm_home_up.type)
                if f_hm_product_up: db.upload_file(f"{_uid}/{client_name}/hm_product",    f_hm_product_up.getvalue(), f_hm_product_up.type)
                if f_hm_cart_up:  db.upload_file(f"{_uid}/{client_name}/hm_cart",          f_hm_cart_up.getvalue(), f_hm_cart_up.type)
                st.cache_data.clear()
            st.success("Files saved! Navigate to Overview to see your audit.")
            time.sleep(1)
            st.rerun()
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: Content Audit  (no GSC data needed)
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🧠  Content Audit":
    content_auditor.render(_)
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# All other pages need GSC data — load it now
# ═══════════════════════════════════════════════════════════════════════════════
_data_loaded = False
try:
    if selected_proj == "🆕 New project...":
        raise FileNotFoundError
    with st.spinner("Loading project data…"):
        queries, pages_df, devices_df, countries_df, chart = load_current({
            "queries":   load_b("queries.csv"),
            "pages":     load_b("pages.csv"),
            "devices":   load_b("devices.csv"),
            "countries": load_b("countries.csv"),
            "chart":     load_b("chart.csv"),
        })
    _data_loaded = True
except FileNotFoundError:
    st.info("No data loaded yet. Go to **⬆️ Setup & Upload** in the sidebar to get started.")
    st.stop()
except Exception as e:
    st.error(f"Failed to load project: {e}")
    st.stop()

with st.spinner("Loading additional data…"):
    prev_queries, prev_pages, prev_chart = load_previous({
        "queries": load_b("prev_queries.csv"),
        "pages":   load_b("prev_pages.csv"),
        "chart":   load_b("prev_chart.csv"),
    })
    cannibal_df = load_cannibal(load_b("query_page.csv"))
    ga4_df      = load_ga4(load_b("ga4.csv"))
    f_hotjar    = load_b("funnel.csv")
    f_hm_home   = load_b("hm_home")
    f_hm_product= load_b("hm_product")
    f_hm_cart   = load_b("hm_cart")
    has_prev    = any([prev_queries is not None, prev_pages is not None, prev_chart is not None])

# Analysis
brand_terms = [t.strip().lower() for t in brand_raw.split("\n")   if t.strip()]
info_terms  = [t.strip().lower() for t in info_raw.split("\n")    if t.strip()]
blog_kws    = [t.strip().lower() for t in blog_kw_raw.split("\n") if t.strip()]

queries["Word Count"] = queries["Query"].str.split().str.len()
queries["Intent"]     = queries["Query"].apply(lambda q: classify_intent(q, brand_terms, info_terms))

if ga4_df is not None:
    def _norm(url):
        return str(url).split("?")[0].rstrip("/").lower()
    pages_df["_key"] = pages_df["Page"].apply(_norm)
    ga4_df["_key"]   = ga4_df["Page"].apply(_norm)
    ga4_num_cols = [c for c in ga4_df.columns if c not in ("Page", "_key")]
    pages_df = pages_df.merge(ga4_df.drop(columns="Page"), on="_key", how="left")
    pages_df[ga4_num_cols] = pages_df[ga4_num_cols].fillna(0)
    pages_df.drop(columns="_key", inplace=True)

pages_df["Type"] = pages_df["Page"].apply(lambda u: tag_page(u, blog_kws))

queries         = compute_opportunity(queries)
stats           = compute_stats(queries, pages_df, chart, devices_df, countries_df)
length_summary, snippet_opps = compute_length(queries)
deltas          = compute_deltas(stats, prev_queries, prev_chart)
query_movers, page_movers = compute_movers(queries, prev_queries, pages_df, prev_pages)
cannibal_issues = compute_cannibalization(cannibal_df)
page_opp        = compute_page_opportunity(pages_df)

# Shared page header
st.markdown(
    f'<div class="page-header"><h2>📊 {client_name} — SEO Performance Audit</h2>'
    f'<p class="meta">Period: {stats.date_range} &nbsp;·&nbsp; Source: Google Search Console &nbsp;·&nbsp; {len(queries):,} queries analyzed</p></div>',
    unsafe_allow_html=True,
)

# Competitor URLs (persisted via session state from Setup page)
competitor_urls_raw = st.session_state.get("competitor_urls", "")


# ═══════════════════════════════════════════════════════════════════════════════
# Route to selected page
# ═══════════════════════════════════════════════════════════════════════════════

if page == "📈  Overview":
    tldr.render(stats, snippet_opps, cannibal_issues, _)
    st.divider()
    kpis.render(stats, deltas, _)
    trend.render(
        chart,
        prev_chart if has_prev else None,
        query_movers if has_prev else None,
        page_movers  if has_prev else None,
        _,
    )
    if has_prev:
        decay.render(page_movers, _)

elif page == "🔍  Traffic":
    findings.render(stats, queries, _)
    opportunities.render(queries, stats, _)
    intent.render(stats.intent_summary, stats.comm_imp_pct, _)

elif page == "📄  Pages & Keywords":
    pages.render(pages_df, _)
    positions.render(stats.queries_ranked, queries, length_summary, snippet_opps, _)
    cannibalization.render(cannibal_df, cannibal_issues, _)

elif page == "👥  Audience":
    devices.render(devices_df, stats.mobile_pos, stats.desktop_pos, _)
    geo.render(countries_df, stats.top_country, _)

elif page == "🖱️  Behavioral":
    hotjar.render(f_hotjar, f_hm_home, f_hm_product, f_hm_cart, _)

elif page == "⚔️  Competitors":
    st.markdown(
        '<div class="alert-blue">Enter your page URL and competitor URLs below, then click Analyze.</div>',
        unsafe_allow_html=True,
    )
    comp_urls_input = st.text_area(
        "URLs to analyze (your site first, then competitors — one per line)",
        value=competitor_urls_raw,
        placeholder="https://yoursite.com/page\nhttps://competitor1.com/page\nhttps://competitor2.com/page",
        height=140,
        key="comp_urls_inline",
    )
    competitor.render(comp_urls_input, _)

elif page == "📋  Report":
    ai_summary.render(stats, page_opp, cannibal_issues, queries, _)
    st.divider()
    recs = recommendations.render(stats, cannibal_issues, countries_df, _)
    export.render(stats.top_opps, recs, queries, _)

st.divider()
st.markdown(
    f"<small style='color:#aaa'>Audit generated · {stats.date_range} · Source: Google Search Console · Built with Streamlit + Plotly</small>",
    unsafe_allow_html=True,
)
