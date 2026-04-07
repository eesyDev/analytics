import pandas as pd
import streamlit as st


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    if "CTR" in df.columns:
        df["CTR"] = (
            df["CTR"].astype(str)
            .str.replace("%", "", regex=False)
            .str.strip()
            .pipe(pd.to_numeric, errors="coerce")
            .fillna(0.0)
        )
    for col in ("Position", "Clicks", "Impressions"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def _read(upload, fallback: str) -> pd.DataFrame:
    return clean_df(pd.read_csv(upload if upload else fallback))


def load_current(uploads: dict) -> tuple:
    """Load current-period GSC data. Returns (queries, pages, devices, countries, chart)."""
    queries   = _read(uploads["queries"],   "data/Queries.csv")
    pages     = _read(uploads["pages"],     "data/Pages.csv")
    devices   = _read(uploads["devices"],   "data/Devices.csv")
    countries = _read(uploads["countries"], "data/Countries.csv")
    chart     = _read(uploads["chart"],     "data/Chart.csv")

    queries.rename(columns={"Top queries": "Query"}, inplace=True, errors="ignore")
    pages.rename(columns={"Top pages":    "Page"},   inplace=True, errors="ignore")
    chart["Date"] = pd.to_datetime(chart["Date"], errors="coerce")

    return queries, pages, devices, countries, chart


def load_previous(uploads: dict) -> tuple:
    """Load previous-period GSC data. Returns (prev_queries, prev_pages, prev_chart)."""
    prev_queries = prev_pages = prev_chart = None

    try:
        if uploads.get("queries"):
            prev_queries = clean_df(pd.read_csv(uploads["queries"]))
            prev_queries.rename(columns={"Top queries": "Query"}, inplace=True, errors="ignore")
        if uploads.get("pages"):
            prev_pages = clean_df(pd.read_csv(uploads["pages"]))
            prev_pages.rename(columns={"Top pages": "Page"}, inplace=True, errors="ignore")
        if uploads.get("chart"):
            prev_chart = clean_df(pd.read_csv(uploads["chart"]))
            prev_chart["Date"] = pd.to_datetime(prev_chart["Date"], errors="coerce")
    except Exception as e:
        st.sidebar.warning(f"Previous period load error: {e}")

    return prev_queries, prev_pages, prev_chart


def load_cannibal(upload) -> pd.DataFrame | None:
    """Load Query+Page combined export for cannibalization analysis."""
    if not upload:
        return None
    try:
        df = clean_df(pd.read_csv(upload))
        df.rename(columns={"Top queries": "Query", "Top pages": "Page"},
                  inplace=True, errors="ignore")
        return df
    except Exception as e:
        st.sidebar.warning(f"Query+Page load error: {e}")
        return None
