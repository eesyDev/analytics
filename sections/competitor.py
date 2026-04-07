import re
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scraper import scrape_page

STOPWORDS = set("""
a an the is are was were be been being have has had do does did will would could should
may might shall to of in for on with at by from as into through during before after above
below between out off over and or but if not no so yet both either neither each few more
most other some such only same than too very just your my our their its this that these
those i you he she we they what which who whom how when where why all any both each every
no nor not only own same so than too very can will just don't should now
""".split())


def _keywords(text: str) -> set:
    words = re.sub(r"[^a-z0-9\s]", "", text.lower()).split()
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def _score_title(n: int) -> int:
    if 50 <= n <= 60:   return 100
    if 40 <= n <= 70:   return 70
    if n > 0:           return 35
    return 0


def _score_meta(n: int) -> int:
    if 140 <= n <= 160: return 100
    if 100 <= n <= 175: return 70
    if n > 0:           return 35
    return 0


def _score_h1(count: int) -> int:
    if count == 1: return 100
    if count > 1:  return 50
    return 0


def _score_images(total: int, no_alt: int) -> int:
    if total == 0: return 100
    pct_ok = 1 - no_alt / total
    return int(pct_ok * 100)


def _score_schema(has: bool) -> int:
    return 100 if has else 0


def _score_words(wc: int, avg: float) -> int:
    if avg == 0: return 50
    ratio = wc / avg
    if ratio >= 0.9:  return 100
    if ratio >= 0.6:  return 65
    return 35


def _label(url: str) -> str:
    from urllib.parse import urlparse
    netloc = urlparse(url).netloc
    return netloc.replace("www.", "") or url[:40]


def render(_):
    st.markdown(
        f'<div class="section-header">{_("🔍 Competitor Page Analysis")}</div>',
        unsafe_allow_html=True,
    )
    st.caption(_(
        "Paste your page URL first, then competitor URLs — one per line. "
        "The tool crawls each page and compares on-page SEO signals."
    ))

    default_placeholder = "https://yoursite.com/page\nhttps://competitor1.com/page\nhttps://competitor2.com/page"
    raw = st.text_area(_("URLs to analyze (your site first)"), placeholder=default_placeholder, height=130)
    analyze = st.button(_("🔎 Analyze pages"), type="primary")

    if not analyze or not raw.strip():
        return

    urls = [u.strip() for u in raw.strip().splitlines() if u.strip().startswith("http")]
    if not urls:
        st.warning(_("Enter at least one valid URL starting with http:// or https://"))
        return
    if len(urls) > 8:
        st.warning(_("Max 8 URLs per analysis to stay polite to servers."))
        urls = urls[:8]

    my_url = urls[0]
    results = []
    with st.spinner(_("Crawling pages…")):
        progress = st.progress(0)
        for i, url in enumerate(urls):
            results.append(scrape_page(url))
            progress.progress((i + 1) / len(urls))
        progress.empty()

    df = pd.DataFrame(results)

    # ── Error report ──────────────────────────────────────────────────────────
    errors = df[df["Error"].notna()]
    if not errors.empty:
        st.warning(_("Some pages couldn't be crawled (Cloudflare / timeout):"))
        st.dataframe(errors[["URL", "Error"]], use_container_width=True, hide_index=True)
        df = df[df["Error"].isna()].copy()

    if df.empty:
        st.error(_("No pages were successfully crawled."))
        return

    labels = [_label(u) for u in df["URL"]]
    my_label = labels[0]
    avg_words = df["Word Count"].mean()

    # ── Scores ────────────────────────────────────────────────────────────────
    df["Score: Title"]    = df["Title Length"].apply(_score_title)
    df["Score: Meta"]     = df["Meta Desc Length"].apply(_score_meta)
    df["Score: H1"]       = df["H1 Count"].apply(_score_h1)
    df["Score: Images"]   = df.apply(lambda r: _score_images(r["Images Total"], r["Images No Alt"]), axis=1)
    df["Score: Schema"]   = df["Has Schema"].apply(_score_schema)
    df["Score: Content"]  = df["Word Count"].apply(lambda w: _score_words(w, avg_words))

    score_cols = ["Score: Title", "Score: Meta", "Score: H1", "Score: Images", "Score: Schema", "Score: Content"]
    df["Total Score"] = df[score_cols].mean(axis=1).round(1)

    # ── Radar chart ───────────────────────────────────────────────────────────
    st.markdown(f"### {_('📡 SEO Radar — your site vs competitors')}")
    radar_dims = ["Title", "Meta Desc", "H1", "Images", "Schema", "Content"]
    fig_radar = go.Figure()
    palette = px.colors.qualitative.Set2

    for i, (row, label) in enumerate(zip(df.itertuples(), labels)):
        scores = [
            row._asdict()["Score: Title"],
            row._asdict()["Score: Meta"],
            row._asdict()["Score: H1"],
            row._asdict()["Score: Images"],
            row._asdict()["Score: Schema"],
            row._asdict()["Score: Content"],
        ]
        is_mine = (i == 0)
        fig_radar.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],
            theta=radar_dims + [radar_dims[0]],
            fill="toself",
            name=label,
            line=dict(
                color=palette[i % len(palette)],
                width=3 if is_mine else 1.5,
            ),
            opacity=0.85 if is_mine else 0.55,
        ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        height=430,
        margin=dict(t=20, b=20),
        paper_bgcolor="white",
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ── Score table ───────────────────────────────────────────────────────────
    st.markdown(f"### {_('📊 Page-by-page breakdown')}")

    display = df[[
        "URL", "Total Score",
        "Title", "Title Length",
        "Meta Desc Length", "H1",
        "H1 Count", "H2 Count",
        "Word Count", "Images No Alt",
        "Has Schema", "Internal Links",
    ]].copy()
    display.insert(0, "Site", labels)
    display = display.drop(columns=["URL"])

    def color_score(val):
        if val >= 80: return "background-color: #c8e6c9"
        if val >= 55: return "background-color: #fff9c4"
        return "background-color: #ffcdd2"

    st.dataframe(
        display.style
        .applymap(color_score, subset=["Total Score"])
        .format({
            "Total Score": "{:.0f}",
            "Title Length": "{:.0f}",
            "Meta Desc Length": "{:.0f}",
            "Word Count": "{:,}",
        }),
        use_container_width=True,
        hide_index=True,
        height=min(400, 60 + len(df) * 55),
    )

    # ── Issues for MY site ────────────────────────────────────────────────────
    my = df.iloc[0]
    issues = []

    if my["Title Length"] == 0:
        issues.append(("🔴", _("Missing title tag")))
    elif my["Title Length"] > 65:
        issues.append(("🟡", _("Title too long ({n} chars) — Google truncates above ~60", n=my["Title Length"])))
    elif my["Title Length"] < 30:
        issues.append(("🟡", _("Title too short ({n} chars) — aim for 50–60", n=my["Title Length"])))

    if my["Meta Desc Length"] == 0:
        issues.append(("🔴", _("Missing meta description")))
    elif my["Meta Desc Length"] > 165:
        issues.append(("🟡", _("Meta description too long ({n} chars) — truncated in SERPs", n=my["Meta Desc Length"])))
    elif my["Meta Desc Length"] < 80:
        issues.append(("🟡", _("Meta description very short ({n} chars) — aim for 140–160", n=my["Meta Desc Length"])))

    if my["H1 Count"] == 0:
        issues.append(("🔴", _("No H1 tag — critical for on-page SEO")))
    elif my["H1 Count"] > 1:
        issues.append(("🟡", _("{n} H1 tags found — use exactly one H1 per page", n=my["H1 Count"])))

    if my["Images Total"] > 0 and my["Images No Alt"] > 0:
        issues.append(("🟡", _(
            "{n}/{t} images missing alt text — hurts accessibility and image SEO",
            n=my["Images No Alt"], t=my["Images Total"]
        )))

    if not my["Has Schema"]:
        issues.append(("🟡", _("No schema markup — competitors with schema get rich results in SERPs")))

    comp_words_avg = df.iloc[1:]["Word Count"].mean() if len(df) > 1 else 0
    if comp_words_avg > 0 and my["Word Count"] < comp_words_avg * 0.7:
        issues.append(("🟡", _(
            "Content is thin — {mine:,} words vs competitor avg {avg:,}",
            mine=int(my["Word Count"]), avg=int(comp_words_avg)
        )))

    if issues:
        st.markdown(f"### {_('⚠️ Issues on your page')}")
        for icon, msg in issues:
            st.markdown(f"{icon} {msg}")
    else:
        st.success(_("No major on-page issues detected on your site."))

    # ── Keyword gap ───────────────────────────────────────────────────────────
    if len(df) > 1:
        st.markdown(f"### {_('🧩 Keyword Gap — competitor titles & H1s vs yours')}")
        st.caption(_(
            "Words that appear in competitor titles/H1s but NOT on your page. "
            "These may be signals Google uses to understand topic relevance."
        ))

        my_words = _keywords(my["Title"] + " " + my["H1"])
        comp_words: dict[str, int] = {}
        for _, row in df.iloc[1:].iterrows():
            for w in _keywords(row["Title"] + " " + row["H1"]):
                comp_words[w] = comp_words.get(w, 0) + 1

        gap = {w: c for w, c in comp_words.items() if w not in my_words}

        if gap:
            gap_df = (
                pd.DataFrame({"Keyword": list(gap.keys()), "Competitors using it": list(gap.values())})
                .sort_values("Competitors using it", ascending=False)
                .head(20)
                .reset_index(drop=True)
            )
            gap_df.index += 1

            fig_gap = px.bar(
                gap_df, x="Competitors using it", y="Keyword",
                orientation="h",
                color="Competitors using it",
                color_continuous_scale="Reds",
                height=max(300, len(gap_df) * 28),
                title=_("Keywords in competitor titles/H1s missing from your page"),
            )
            fig_gap.update_layout(
                yaxis=dict(autorange="reversed"),
                plot_bgcolor="white", paper_bgcolor="white",
                coloraxis_showscale=False,
                margin=dict(l=10, t=40, b=10),
            )
            fig_gap.update_xaxes(gridcolor="#f0f0f0", dtick=1)
            st.plotly_chart(fig_gap, use_container_width=True)
        else:
            st.info(_("No keyword gaps detected — your title and H1 cover all competitor terms."))
