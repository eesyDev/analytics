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
from i18n import get_text
import i18n
import db

st.set_page_config(page_title="SEO Performance Audit", page_icon="📊", layout="wide")
st.markdown(config.CSS, unsafe_allow_html=True)

import auth
auth.check_auth()  # Блокируем доступ неавторизованным пользователям

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.write(f"👤 Аналитик: **{st.session_state['email']}**")
    if st.button("🚪 Выйти", use_container_width=True):
        auth.logout()
        st.rerun()

    # lang_choice = st.radio("🌐 Language / Язык", ["EN", "RU"])
    lang_choice = "EN"
    _ = lambda key, *args, **kwargs: i18n.get_text(lang_choice, key, *args, **kwargs)

    st.header(_("⚙️ Settings"))
    
    with st.expander(_("Intent Classification")):
        brand_raw   = st.text_area(_("Brand terms (one per line)"), "")
        info_raw    = st.text_area(_("Informational terms (one per line)"),
                        _("how to\nwhat is\nmake money\ndepreciation\nfinancing\nhow long\nhow much\ncan you\nis a\nstarting a\nclearing land\nhourly rate\nguide\ntips\nvs\nreviews"))
        blog_kw_raw = st.text_area(_("URL keywords → Blog page (one per line)"),
                        _("how-to\nwhat-is\nguide\ntips\nblog\narticle"))

    st.divider()
    st.subheader(_("Проекты (Cloud Saved)"))
    projects = db.list_projects(st.session_state['user_id'])
    selected_proj = st.selectbox("Выберите сайт", ["🆕 Новый проект..."] + projects)
    
    if selected_proj == "🆕 Новый проект...":
        client_name = st.text_input("Название для нового проекта:", value="My Site")
    else:
        client_name = selected_proj

    with st.expander("⬆️ Загрузка CSV файлов (в облако)"):
        f_queries   = st.file_uploader(_("Queries.csv"), type="csv", key="q")
        f_pages     = st.file_uploader(_("Pages.csv"), type="csv", key="p")
        f_devices   = st.file_uploader(_("Devices.csv"), type="csv", key="d")
        f_countries = st.file_uploader(_("Countries.csv"), type="csv", key="c")
        f_chart     = st.file_uploader(_("Chart.csv (time series)"), type="csv", key="ch")
        st.divider()
        f_prev_queries = st.file_uploader(_("Queries.csv (prev)"), type="csv", key="pq")
        f_prev_pages   = st.file_uploader(_("Pages.csv (prev)"), type="csv", key="pp")
        f_prev_chart   = st.file_uploader(_("Chart.csv (prev)"), type="csv", key="pch")
        st.divider()
        f_query_page = st.file_uploader(_("Query+Page export CSV"), type="csv", key="qp")
        st.divider()
        f_hotjar     = st.file_uploader(_("Funnel export CSV"), type="csv", key="hj")
        f_hm_home    = st.file_uploader(_("Homepage heatmap"), type=["png","jpg","jpeg"], key="hm1")
        f_hm_product = st.file_uploader(_("Product page heatmap"), type=["png","jpg","jpeg"], key="hm2")
        f_hm_cart    = st.file_uploader(_("Cart page heatmap"), type=["png","jpg","jpeg"], key="hm3")

        if st.button("💾 Сохранить файлы в облако", type="primary", use_container_width=True):
            if not client_name or client_name == "🆕 Новый проект...":
                st.error("Укажите имя проекта!")
            else:
                uid = st.session_state['user_id']
                if f_queries: db.upload_file(f"{uid}/{client_name}/queries.csv", f_queries.getvalue())
                if f_pages: db.upload_file(f"{uid}/{client_name}/pages.csv", f_pages.getvalue())
                if f_devices: db.upload_file(f"{uid}/{client_name}/devices.csv", f_devices.getvalue())
                if f_countries: db.upload_file(f"{uid}/{client_name}/countries.csv", f_countries.getvalue())
                if f_chart: db.upload_file(f"{uid}/{client_name}/chart.csv", f_chart.getvalue())
                
                if f_prev_queries: db.upload_file(f"{uid}/{client_name}/prev_queries.csv", f_prev_queries.getvalue())
                if f_prev_pages: db.upload_file(f"{uid}/{client_name}/prev_pages.csv", f_prev_pages.getvalue())
                if f_prev_chart: db.upload_file(f"{uid}/{client_name}/prev_chart.csv", f_prev_chart.getvalue())
                
                if f_query_page: db.upload_file(f"{uid}/{client_name}/query_page.csv", f_query_page.getvalue())
                
                if f_hotjar: db.upload_file(f"{uid}/{client_name}/funnel.csv", f_hotjar.getvalue())
                if f_hm_home: db.upload_file(f"{uid}/{client_name}/hm_home", f_hm_home.getvalue(), f_hm_home.type)
                if f_hm_product: db.upload_file(f"{uid}/{client_name}/hm_product", f_hm_product.getvalue(), f_hm_product.type)
                if f_hm_cart: db.upload_file(f"{uid}/{client_name}/hm_cart", f_hm_cart.getvalue(), f_hm_cart.type)
                
                st.cache_data.clear()
                st.success("Все файлы сохранены в базу Supabase!")
                import time; time.sleep(1)
                st.rerun()

    st.divider()
    st.caption(_("Universal SEO Audit Tool · Built with Streamlit + Plotly"))


# ── Load data ─────────────────────────────────────────────────────────────────
import io
uid = st.session_state["user_id"]

@st.cache_data(show_spinner=False)
def get_b(uid, project_name, fname):
    b = db.download_file(f"{uid}/{project_name}/{fname}")
    return b  # return raw bytes, convert to BytesIO below

def load_b(fname):
    b = get_b(uid, client_name, fname)
    return io.BytesIO(b) if b else None

try:
    if selected_proj == "🆕 Новый проект...":
        raise FileNotFoundError

    queries, pages_df, devices_df, countries_df, chart = load_current({
        "queries": load_b("queries.csv"), "pages": load_b("pages.csv"),
        "devices": load_b("devices.csv"), "countries": load_b("countries.csv"),
        "chart": load_b("chart.csv"),
    })
except FileNotFoundError:
    st.warning(_("⬆️  Upload GSC CSV files in the sidebar to get started."))
    st.stop()
except Exception as e:
    st.error(f"Не удалось распарсить базу облака: {e}")
    st.stop()

prev_queries, prev_pages, prev_chart = load_previous({
    "queries": load_b("prev_queries.csv"), "pages": load_b("prev_pages.csv"),
    "chart": load_b("prev_chart.csv"),
})
cannibal_df  = load_cannibal(load_b("query_page.csv"))
f_hotjar     = load_b("funnel.csv")
f_hm_home    = load_b("hm_home")
f_hm_product = load_b("hm_product")
f_hm_cart    = load_b("hm_cart")
has_prev     = any([prev_queries is not None, prev_pages is not None, prev_chart is not None])


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



# ── Layout ────────────────────────────────────────────────────────────────────
st.markdown(_("## 📊 {client_name} — SEO Performance Audit", client_name=client_name))
st.markdown(
    _("**Period:** {date_range} &nbsp;|&nbsp; **Source:** Google Search Console &nbsp;|&nbsp; **Queries analyzed:** {q_count:,}", 
      date_range=stats.date_range, q_count=len(queries)),
    unsafe_allow_html=True,
)

tldr.render(stats, snippet_opps, cannibal_issues, _)
st.divider()

kpis.render(stats, deltas, _)
trend.render(chart, prev_chart if has_prev else None,
             query_movers if has_prev else None,
             page_movers  if has_prev else None, _)
findings.render(stats, queries, _)
opportunities.render(queries, stats, _)
cannibalization.render(cannibal_df, cannibal_issues, _)
intent.render(stats.intent_summary, stats.comm_imp_pct, _)
pages.render(pages_df, _)
positions.render(stats.queries_ranked, queries, length_summary, snippet_opps, _)
devices.render(devices_df, stats.mobile_pos, stats.desktop_pos, _)
geo.render(countries_df, stats.top_country, _)
hotjar.render(f_hotjar, f_hm_home, f_hm_product, f_hm_cart, _)

recs = recommendations.render(stats, cannibal_issues, countries_df, _)
export.render(stats.top_opps, recs, queries, _)

st.divider()
st.markdown(
    _("<small style='color:#888'>Audit generated · {date_range} · Source: Google Search Console · Built with Streamlit + Plotly</small>", date_range=stats.date_range),
    unsafe_allow_html=True,
)
