from dataclasses import dataclass
from typing import Optional
import pandas as pd
from config import CTR_BENCH_INFO, CTR_BENCH_COMM, CTR_BENCH_BRAND, COMMERCIAL_SIGNALS


# ── Intent classification ─────────────────────────────────────────────────────

def classify_intent(q: str, brand_terms: list, info_terms: list) -> str:
    q = str(q).lower()
    if any(c in q for c in COMMERCIAL_SIGNALS):
        return "Commercial / Product"
    if brand_terms and any(b in q for b in brand_terms):
        return "Brand"
    if any(i in q for i in info_terms):
        return "Informational"
    return "Commercial / Product"


def tag_page(url: str, blog_kws: list) -> str:
    u = str(url).lower()
    if blog_kws and any(k in u for k in blog_kws):
        return "Informational / Blog"
    return "Product / Category"


# ── CTR benchmark ─────────────────────────────────────────────────────────────

def expected_ctr(pos, intent: str = "") -> float:
    try:
        p = max(1, int(round(float(pos))))
    except (ValueError, TypeError):
        return 0.3
        
    if intent == "Brand":
        bench = CTR_BENCH_BRAND
    elif intent == "Commercial / Product":
        bench = CTR_BENCH_COMM
    else:
        bench = CTR_BENCH_INFO

    if p <= 10:
        return bench[p]
    if p <= 20:
        return 1.5 if intent == "Brand" else (0.8 if intent == "Commercial / Product" else 1.0)
    return 0.5 if intent == "Brand" else (0.2 if intent == "Commercial / Product" else 0.3)


# ── Opportunity scoring ───────────────────────────────────────────────────────

def compute_opportunity(queries: pd.DataFrame) -> pd.DataFrame:
    queries = queries.copy()
    queries["Expected CTR"] = queries.apply(
        lambda r: expected_ctr(r["Position"], r["Intent"]), axis=1
    )
    queries["CTR Gap"] = (queries["Expected CTR"] - queries["CTR"]).round(2)
    queries["Opportunity Score"] = (
        (queries["Impressions"] * queries["CTR Gap"]) / 100
    ).clip(lower=0).round(1)
    return queries


# ── Stats dataclass ───────────────────────────────────────────────────────────

@dataclass
class Stats:
    total_clicks: int
    total_impressions: int
    weighted_ctr: float
    weighted_pos: float
    imp_total: float
    imp_total_s: float
    zero_click_imp: int
    total_opportunity: float
    blog_pct: float
    brand_pct: float
    comm_pct: float
    comm_imp_pct: float
    mobile_pos: Optional[float]
    desktop_pos: Optional[float]
    date_range: str
    top_country: Optional[object]
    anonymized_clicks: int
    anonymized_pct: float
    intent_summary: pd.DataFrame
    queries_ranked: pd.DataFrame
    top_opps: pd.DataFrame


def compute_stats(queries, pages, chart, devices, countries) -> Stats:
    imp_total   = queries["Impressions"].sum()
    imp_total_s = imp_total if imp_total > 0 else 1

    weighted_ctr = (queries["CTR"] * queries["Impressions"]).sum() / imp_total_s
    weighted_pos = (queries["Position"] * queries["Impressions"]).sum() / imp_total_s

    zero_click_imp    = int(queries[queries["Clicks"] == 0]["Impressions"].sum())
    total_opportunity = queries["Opportunity Score"].sum()

    blog_clicks    = int(pages[pages["Type"] == "Informational / Blog"]["Clicks"].sum())
    product_clicks = int(pages[pages["Type"] == "Product / Category"]["Clicks"].sum())
    all_page_clicks = blog_clicks + product_clicks
    blog_pct = 100 * blog_clicks / all_page_clicks if all_page_clicks > 0 else 0.0

    intent_summary = (
        queries
        .groupby("Intent")
        .agg(Queries=("Query","count"), Clicks=("Clicks","sum"), Impressions=("Impressions","sum"))
        .reset_index()
    )

    clicks_total = queries["Clicks"].sum() or 1
    brand_clicks = intent_summary.loc[intent_summary["Intent"] == "Brand", "Clicks"].sum()
    comm_clicks  = intent_summary.loc[intent_summary["Intent"] == "Commercial / Product", "Clicks"].sum()
    brand_pct    = 100 * brand_clicks / clicks_total
    comm_pct     = 100 * comm_clicks  / clicks_total
    comm_imp_pct = 100 * intent_summary.loc[
        intent_summary["Intent"] == "Commercial / Product", "Impressions"
    ].sum() / imp_total_s

    def device_stat(name, col):
        mask = devices["Device"].str.lower() == name.lower()
        vals = devices.loc[mask, col].values
        return float(vals[0]) if len(vals) else None

    mobile_pos  = device_stat("mobile",  "Position")
    desktop_pos = device_stat("desktop", "Position")

    queries_ranked = queries[queries["Position"] > 0].copy()

    top_opps = (
        queries[queries["Opportunity Score"] > 0]
        .sort_values("Opportunity Score", ascending=False)
        .head(25)
        [["Query","Impressions","Clicks","CTR","Position","Expected CTR","CTR Gap","Opportunity Score","Intent"]]
        .reset_index(drop=True)
    )
    top_opps.index += 1

    date_range = (
        f"{chart['Date'].min().strftime('%b %d')} – {chart['Date'].max().strftime('%b %d, %Y')}"
        if not chart["Date"].isna().all() else "N/A"
    )

    top_country = countries.nlargest(1, "Clicks").iloc[0] if len(countries) > 0 else None
    
    anonymized_clicks = 0
    anonymized_pct = 0.0
    if pages is not None and "Clicks" in pages.columns and "Clicks" in queries.columns:
        pages_clicks = int(pages["Clicks"].sum())
        q_clicks = int(queries["Clicks"].sum())
        diff = pages_clicks - q_clicks
        if diff > 0:
            anonymized_clicks = diff
            anonymized_pct = min(100.0, 100 * diff / max(1, pages_clicks))

    return Stats(
        total_clicks=int(chart["Clicks"].sum()),
        total_impressions=int(chart["Impressions"].sum()),
        weighted_ctr=weighted_ctr,
        weighted_pos=weighted_pos,
        imp_total=imp_total,
        imp_total_s=imp_total_s,
        zero_click_imp=zero_click_imp,
        total_opportunity=total_opportunity,
        blog_pct=blog_pct,
        brand_pct=brand_pct,
        comm_pct=comm_pct,
        comm_imp_pct=comm_imp_pct,
        mobile_pos=mobile_pos,
        desktop_pos=desktop_pos,
        date_range=date_range,
        top_country=top_country,
        anonymized_clicks=anonymized_clicks,
        anonymized_pct=anonymized_pct,
        intent_summary=intent_summary,
        queries_ranked=queries_ranked,
        top_opps=top_opps,
    )


# ── Query length & snippet opportunities ─────────────────────────────────────

def compute_length(queries: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    queries = queries.copy()
    queries["Word Count"] = queries["Query"].str.split().str.len()
    queries["Length Group"] = pd.cut(
        queries["Word Count"],
        bins=[0, 1, 2, 3, 4, 99],
        labels=["1 word", "2 words", "3 words", "4 words", "5+ words"],
    )
    length_summary = (
        queries.groupby("Length Group", observed=True)
        .agg(
            Queries=("Query",       "count"),
            Impressions=("Impressions", "sum"),
            Clicks=("Clicks",      "sum"),
            Avg_Position=("Position",   "mean"),
            Avg_CTR=("CTR",        "mean"),
        )
        .reset_index()
    )
    length_summary["CTR"]      = length_summary["Avg_CTR"].round(2)
    length_summary["Position"] = length_summary["Avg_Position"].round(1)

    snippet_opps = (
        queries[
            (queries["Position"] >= 2) &
            (queries["Position"] <= 5) &
            (queries["Intent"] == "Informational") &
            (queries["Impressions"] >= 10)
        ]
        .sort_values("Impressions", ascending=False)
        .head(20)
        [["Query","Position","Impressions","Clicks","CTR","Expected CTR"]]
        .reset_index(drop=True)
    )
    snippet_opps.index += 1

    return length_summary, snippet_opps


# ── Period deltas ─────────────────────────────────────────────────────────────

@dataclass
class Deltas:
    clicks_str:  Optional[str]
    clicks_val:  Optional[float]
    imps_str:    Optional[str]
    imps_val:    Optional[float]
    ctr_str:     Optional[str]
    ctr_val:     Optional[float]
    pos_str:     Optional[str]
    pos_val:     Optional[float]
    has_prev:    bool = False


def _pct_delta(curr, prev):
    if prev is None or prev == 0:
        return None, None
    val = (curr - prev) / abs(prev) * 100
    return f"{val:+.1f}%", val


def compute_deltas(stats: Stats, prev_queries, prev_chart) -> Deltas:
    if prev_chart is None and prev_queries is None:
        return Deltas(None, None, None, None, None, None, None, None, has_prev=False)

    prev_clicks = int(prev_chart["Clicks"].sum())       if prev_chart   is not None else None
    prev_imps   = int(prev_chart["Impressions"].sum())   if prev_chart   is not None else None

    prev_imp_total = prev_queries["Impressions"].sum()  if prev_queries is not None else None
    prev_wctr = (
        (prev_queries["CTR"] * prev_queries["Impressions"]).sum() / prev_imp_total
        if prev_queries is not None and prev_imp_total and prev_imp_total > 0 else None
    )
    prev_wpos = (
        (prev_queries["Position"] * prev_queries["Impressions"]).sum() / prev_imp_total
        if prev_queries is not None and prev_imp_total and prev_imp_total > 0 else None
    )

    cs, cv = _pct_delta(stats.total_clicks,      prev_clicks)
    is_, iv = _pct_delta(stats.total_impressions, prev_imps)
    ctrs, ctrv = _pct_delta(stats.weighted_ctr,  prev_wctr)
    ps, pv     = _pct_delta(stats.weighted_pos,   prev_wpos)

    return Deltas(cs, cv, is_, iv, ctrs, ctrv, ps, pv, has_prev=True)


# ── Period movers ─────────────────────────────────────────────────────────────

def compute_movers(queries, prev_queries, pages, prev_pages):
    query_movers = page_movers = None

    if prev_queries is not None and "Query" in prev_queries.columns:
        query_movers = queries[["Query","Clicks","Impressions","Position","Intent"]].merge(
            prev_queries[["Query","Clicks","Impressions","Position"]].rename(columns={
                "Clicks": "Clicks_prev", "Impressions": "Impressions_prev", "Position": "Position_prev"
            }),
            on="Query", how="outer",
        ).fillna(0)
        query_movers["Clicks_delta"] = query_movers["Clicks"]      - query_movers["Clicks_prev"]
        query_movers["Imps_delta"]   = query_movers["Impressions"]  - query_movers["Impressions_prev"]
        query_movers["Pos_delta"]    = query_movers["Position_prev"] - query_movers["Position"]

    if prev_pages is not None and "Page" in prev_pages.columns:
        page_movers = pages[["Page","Clicks","Impressions","CTR","Type"]].merge(
            prev_pages[["Page","Clicks","Impressions","CTR"]].rename(columns={
                "Clicks": "Clicks_prev", "Impressions": "Impressions_prev", "CTR": "CTR_prev"
            }),
            on="Page", how="outer",
        ).fillna(0)
        page_movers["Clicks_delta"] = page_movers["Clicks"] - page_movers["Clicks_prev"]

    return query_movers, page_movers


# ── Cannibalization ───────────────────────────────────────────────────────────

def compute_cannibalization(cannibal_df) -> Optional[pd.DataFrame]:
    if cannibal_df is None:
        return None
    if "Query" not in cannibal_df.columns or "Page" not in cannibal_df.columns:
        return None

    # Group by query and get sum
    grp = (
        cannibal_df.groupby("Query")
        .agg(
            Pages=("Page", "nunique"),
            Page_list=("Page", lambda x: list(x.unique())),
            Impressions=("Impressions", "sum"),
            Clicks=("Clicks", "sum"),
        )
        .reset_index()
    )
    
    # Filter for true cannibalization (competing page must have >15% of top page impressions)
    real_cannibals = []
    
    for _, row in grp[grp["Pages"] >= 2].iterrows():
        q = row["Query"]
        # get all pages for this query
        q_pages = cannibal_df[cannibal_df["Query"] == q].sort_values("Impressions", ascending=False)
        
        if len(q_pages) >= 2:
            top_imps = q_pages.iloc[0]["Impressions"]
            # Check how many pages have at least 15% of the leader's impressions
            competitors = q_pages[q_pages["Impressions"] > (0.15 * top_imps)]
            
            if len(competitors) >= 2:
                # Real cannibalization found
                row_copy = row.copy()
                row_copy["Pages"] = len(competitors)
                row_copy["Page_list"] = list(competitors["Page"].unique())
                real_cannibals.append(row_copy)

    if not real_cannibals:
        return pd.DataFrame()
        
    result = pd.DataFrame(real_cannibals).sort_values("Impressions", ascending=False).reset_index(drop=True)
    result.index += 1

    def fmt_pages(lst):
        clean  = [str(p).replace("https://","").replace("http://","")[:60] for p in lst[:3]]
        suffix = f" +{len(lst)-3} more" if len(lst) > 3 else ""
        return " | ".join(clean) + suffix

    result["Competing Pages"] = result["Page_list"].apply(fmt_pages)
    return result
