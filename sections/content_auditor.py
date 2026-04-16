import re
import streamlit as st
import plotly.graph_objects as go
from scraper import scrape_content_deep


# ── Helpers ───────────────────────────────────────────────────────────────────

def _headings_tree(headings: list) -> str:
    """Format headings as an indented tree string."""
    indent = {"H1": "", "H2": "  ", "H3": "    ", "H4": "      "}
    lines = []
    for level, text in headings:
        pad = indent.get(level, "")
        lines.append(f"{pad}{level}: {text}")
    return "\n".join(lines) if lines else "(no headings found)"


def _depth_gauge(score: int) -> go.Figure:
    """Plotly gauge chart for content depth score."""
    if score >= 75:
        color = "#388e3c"
    elif score >= 50:
        color = "#f9a825"
    else:
        color = "#d32f2f"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Content Depth Score", "font": {"size": 16}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#888"},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "white",
            "borderwidth": 1,
            "bordercolor": "#ddd",
            "steps": [
                {"range": [0,  40], "color": "#fdecea"},
                {"range": [40, 70], "color": "#fff8e1"},
                {"range": [70, 100], "color": "#e8f5e9"},
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        height=260,
        margin=dict(t=40, b=10, l=20, r=20),
        paper_bgcolor="white",
        font={"color": "#333"},
    )
    return fig


def _build_prompt(my: dict, comps: list, topic: str) -> str:
    """Build the Claude prompt for content analysis."""

    def _page_block(data: dict, label: str) -> str:
        tree = _headings_tree(data["headings"])
        text_preview = data["body_text"][:3500].strip()
        return (
            f"--- {label} ---\n"
            f"URL: {data['url']}\n"
            f"Title: {data['title']}\n"
            f"Word count: {data['word_count']:,}\n"
            f"Paragraphs: {data['paragraph_count']}\n"
            f"Heading structure:\n{tree}\n\n"
            f"Content (first ~3500 words):\n{text_preview}\n"
        )

    my_block = _page_block(my, "YOUR PAGE")

    comp_blocks = ""
    valid_comps = [c for c in comps if not c["error"]]
    for i, c in enumerate(valid_comps, 1):
        comp_blocks += "\n" + _page_block(c, f"COMPETITOR {i}")

    topic_line = f"Main keyword / topic: {topic}" if topic else ""

    return f"""You are an expert SEO content strategist. Analyze the page below and give specific, actionable recommendations.
{topic_line}

{my_block}
{"COMPETITOR PAGES:" + comp_blocks if comp_blocks else "No competitor pages provided — base analysis on SEO best practices and content quality."}

Respond with EXACTLY these sections in order. Use markdown. Be specific — no generic advice.

## Content Depth Score: [0-100]/100
One paragraph explaining the score. Mention: topical coverage, content structure, expertise signals, and what specifically earns or loses points. Be direct.

## What This Page Covers Well ✅
3–5 bullet points. Each must reference something specific from the actual content.

## Missing Sections to Add 📝
6–8 sections the page is missing. For each: the section title, one sentence on what to include, and why it matters for ranking. Be concrete — invent real section names.

## FAQ to Add ❓
10 specific questions real users search for that this page doesn't answer. Write them as actual question headings (H3 style). Make them feel like Google autocomplete suggestions.

## Semantic Keywords to Weave In 🔑
15 LSI / semantic keywords grouped into 3 clusters. Format: **Cluster name**: term1, term2, term3, term4, term5.

{"## Competitor Content Gap 🏆" + chr(10) + "3–5 topics or sections that competitors cover that YOUR PAGE completely misses. For each: topic name, which competitor(s) cover it, and one sentence on how to address it." if valid_comps else ""}

## Priority Action Plan 🚀
Top 3 actions ranked by impact. Format: **Action**: what exactly to do. **Impact**: why this matters. **Effort**: Low / Medium / High."""


# ── Main render ───────────────────────────────────────────────────────────────

def render(_):
    st.markdown(
        f'<div class="section-header">{_("🧠 AI Content Auditor")}</div>',
        unsafe_allow_html=True,
    )
    st.caption(_(
        "Paste any URL — AI reads the actual content, scores depth, "
        "finds missing sections, and gives you a competitor gap analysis."
    ))

    # ── Inputs ────────────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        my_url = st.text_input(
            _("Your page URL"),
            placeholder="https://yoursite.com/your-page",
            key="ca_my_url",
        )
        topic = st.text_input(
            _("Main keyword / topic (optional)"),
            placeholder="e.g. solar panel installation cost",
            key="ca_topic",
        )

    with col_right:
        comp_raw = st.text_area(
            _("Competitor URLs (optional — up to 3, one per line)"),
            placeholder="https://competitor1.com/page\nhttps://competitor2.com/page",
            height=108,
            key="ca_comps",
        )

    go_btn = st.button(_("🔍 Analyze Content"), type="primary", use_container_width=True, key="ca_go")

    if not go_btn:
        st.info(_("Enter your page URL above and click Analyze — no GSC data required."))
        return

    if not my_url.strip().startswith("http"):
        st.warning(_("Please enter a valid URL starting with http:// or https://"))
        return

    comp_urls = [u.strip() for u in comp_raw.strip().splitlines() if u.strip().startswith("http")][:3]
    all_urls = [my_url.strip()] + comp_urls

    # ── Scraping ──────────────────────────────────────────────────────────────
    scraped = []
    with st.spinner(_("Crawling pages…")):
        prog = st.progress(0)
        for i, url in enumerate(all_urls):
            scraped.append(scrape_content_deep(url))
            prog.progress((i + 1) / len(all_urls))
        prog.empty()

    my_data = scraped[0]
    comp_data = scraped[1:]

    if my_data["error"]:
        st.error(f"Couldn't crawl your page: {my_data['error']}")
        return

    crawl_errors = [c for c in comp_data if c["error"]]
    if crawl_errors:
        st.warning(
            _("Couldn't crawl {n} competitor page(s): {urls}",
              n=len(crawl_errors),
              urls=", ".join(c["url"][:60] for c in crawl_errors))
        )

    valid_comps = [c for c in comp_data if not c["error"]]

    # ── Page Snapshot ─────────────────────────────────────────────────────────
    st.markdown(f"### {_('📊 Page Snapshot')}")

    comp_avg_wc = (
        sum(c["word_count"] for c in valid_comps) / len(valid_comps)
        if valid_comps else 0
    )
    comp_avg_h2 = (
        sum(sum(1 for h in c["headings"] if h[0] == "H2") for c in valid_comps) / len(valid_comps)
        if valid_comps else 0
    )

    my_h2 = sum(1 for h in my_data["headings"] if h[0] == "H2")
    my_h3 = sum(1 for h in my_data["headings"] if h[0] == "H3")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(
        _("Word Count"),
        f"{my_data['word_count']:,}",
        delta=f"comp avg: {int(comp_avg_wc):,}" if comp_avg_wc else None,
        delta_color="normal",
    )
    c2.metric(_("Paragraphs"), my_data["paragraph_count"])
    c3.metric(_("H2 sections"), my_h2,
              delta=f"comp avg: {comp_avg_h2:.1f}" if comp_avg_h2 else None,
              delta_color="normal")
    c4.metric(_("H3 subsections"), my_h3)
    c5.metric(_("Total headings"), len(my_data["headings"]))

    # ── Heading Structure Tree ─────────────────────────────────────────────────
    if my_data["headings"]:
        with st.expander(_("📑 Heading Structure"), expanded=True):
            st.code(_headings_tree(my_data["headings"]), language=None)
    else:
        st.warning(_("No headings found on this page — that's an issue to fix."))

    # ── Competitor word count bar ──────────────────────────────────────────────
    if valid_comps:
        st.markdown(f"#### {_('Word count comparison')}")
        import plotly.express as px
        import pandas as pd

        from urllib.parse import urlparse
        def _short(url):
            return urlparse(url).netloc.replace("www.", "") or url[:40]

        wc_data = [{"Site": _short(my_data["url"]) + " (you)", "Words": my_data["word_count"], "mine": True}]
        for c in valid_comps:
            wc_data.append({"Site": _short(c["url"]), "Words": c["word_count"], "mine": False})

        wc_df = pd.DataFrame(wc_data)
        colors = ["#1565c0" if r else "#90a4ae" for r in wc_df["mine"]]

        fig_wc = px.bar(
            wc_df, x="Site", y="Words",
            text="Words",
            height=280,
            labels={"Words": "Word count", "Site": ""},
        )
        fig_wc.update_traces(
            marker_color=colors,
            texttemplate="%{text:,}",
            textposition="outside",
        )
        fig_wc.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=10, b=10),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        )
        st.plotly_chart(fig_wc, use_container_width=True)

    st.divider()

    # ── AI Analysis ───────────────────────────────────────────────────────────
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.warning(_("Add `ANTHROPIC_API_KEY` to `.streamlit/secrets.toml` to enable AI analysis."))
        return

    st.markdown(f"### {_('🤖 AI Content Analysis')}")
    st.caption(_("Claude reads the actual content and gives you specific, actionable recommendations."))

    try:
        import anthropic
    except ImportError:
        st.error(_("Run `pip install anthropic` to enable this feature."))
        return

    prompt = _build_prompt(my_data, comp_data, topic.strip())
    client = anthropic.Anthropic(api_key=api_key)

    output_box = st.empty()
    full_text = ""

    with st.spinner(_("Analyzing content — this takes ~15 seconds…")):
        try:
            with client.messages.stream(
                model="claude-haiku-4-5-20251001",
                max_tokens=2500,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for chunk in stream.text_stream:
                    full_text += chunk
                    output_box.markdown(full_text + "▌")
            output_box.markdown(full_text)
        except Exception as e:
            st.error(f"AI analysis failed: {e}")
            return

    # ── Depth Score Gauge ─────────────────────────────────────────────────────
    match = re.search(r"Content Depth Score[:\s]*(\d+)/100", full_text, re.IGNORECASE)
    if match:
        score = int(match.group(1))
        col_gauge, col_tip = st.columns([1, 2])
        with col_gauge:
            st.plotly_chart(_depth_gauge(score), use_container_width=True)
        with col_tip:
            st.markdown(" ")
            if score >= 75:
                st.markdown(
                    '<div class="alert-green">Strong content — focus on filling the gaps identified above to reach topical authority.</div>',
                    unsafe_allow_html=True,
                )
            elif score >= 50:
                st.markdown(
                    '<div class="alert-amber">Average depth — significant opportunities to outrank competitors by expanding coverage.</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="alert-red">Thin content — major risk of being outranked. Prioritize the Missing Sections above immediately.</div>',
                    unsafe_allow_html=True,
                )
