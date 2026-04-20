CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&display=swap');

/* ── Base ────────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Sora', system-ui, sans-serif !important;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1280px;
}

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #0a0a0d !important;
    border-right: 1px solid #1e1e24 !important;
}
.sidebar-logo {
    font-size: 1rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
    margin-bottom: 0;
}
.sidebar-tagline {
    font-size: 0.7rem;
    color: #444;
    margin-top: 2px;
    letter-spacing: 0.3px;
}
.sidebar-user {
    font-size: 0.78rem;
    color: #666;
    padding: 4px 0;
}

/* ── Sidebar nav ─────────────────────────────────────────────────────────── */
.nav-label {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #333;
    margin: 1rem 0 0.4rem 0.2rem;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
    gap: 2px !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
    padding: 0.5rem 0.8rem !important;
    border-radius: 6px !important;
    border-left: 2px solid transparent !important;
    cursor: pointer !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: #888 !important;
    transition: all 0.1s !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
    background: rgba(37,99,235,0.08) !important;
    color: #ccc !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"],
section[data-testid="stSidebar"] div[data-testid="stRadio"] label[aria-checked="true"] {
    background: rgba(37,99,235,0.12) !important;
    border-left-color: #2563eb !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] input[type="radio"] {
    display: none !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
    margin: 0 !important;
}

/* ── Page header ─────────────────────────────────────────────────────────── */
.page-header {
    padding-bottom: 1.25rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid #1e1e24;
}
.page-header h2 {
    margin: 0 0 0.3rem 0;
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.8px;
    line-height: 1.15;
}
.page-header h2 span.accent {
    color: #2563eb;
}
.page-header .meta {
    font-size: 0.8rem;
    color: #444;
    margin-top: 0.25rem;
    letter-spacing: 0.2px;
}

/* ── Section header ──────────────────────────────────────────────────────── */
.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: -0.3px;
    margin-top: 2.5rem;
    margin-bottom: 0.75rem;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-header::after {
    content: "";
    display: block;
    height: 2px;
    flex: 1;
    background: linear-gradient(90deg, #2563eb 0%, transparent 100%);
    border-radius: 2px;
    margin-left: 0.75rem;
}

/* ── Upload cards ────────────────────────────────────────────────────────── */
.upload-card {
    border: 1px solid #1e1e24;
    border-radius: 12px;
    padding: 1.2rem 1.4rem 1rem;
    background: #111116;
    margin-bottom: 0.75rem;
}
.upload-card-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.2rem;
    letter-spacing: -0.2px;
}
.upload-card-hint {
    font-size: 0.74rem;
    color: #444;
    margin-bottom: 0.75rem;
    line-height: 1.5;
}

/* ── Alert boxes ──────────────────────────────────────────────────────────── */
.alert-red {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.75rem;
    font-size: 0.88rem;
    color: #fca5a5;
    line-height: 1.5;
}
.alert-amber {
    background: rgba(245,158,11,0.08);
    border: 1px solid rgba(245,158,11,0.25);
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.75rem;
    font-size: 0.88rem;
    color: #fcd34d;
    line-height: 1.5;
}
.alert-green {
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.2);
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.75rem;
    font-size: 0.88rem;
    color: #86efac;
    line-height: 1.5;
}
.alert-blue {
    background: rgba(37,99,235,0.08);
    border: 1px solid rgba(37,99,235,0.25);
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.75rem;
    font-size: 0.88rem;
    color: #93c5fd;
    line-height: 1.5;
}

/* ── Stat card — for big numbers ─────────────────────────────────────────── */
.stat-card {
    background: #111116;
    border: 1px solid #1e1e24;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.5rem;
}
.stat-card .stat-value {
    font-size: 2.2rem;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: -1.5px;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.stat-card .stat-value.accent { color: #2563eb; }
.stat-card .stat-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #444;
}
.stat-card .stat-delta {
    font-size: 0.82rem;
    font-weight: 500;
    margin-top: 0.4rem;
}
.stat-card .stat-delta.up   { color: #4ade80; }
.stat-card .stat-delta.down { color: #f87171; }

/* ── Hotjar placeholder ───────────────────────────────────────────────────── */
.hotjar-placeholder {
    border: 1px dashed #222;
    border-radius: 10px;
    padding: 2rem;
    text-align: center;
    margin-top: 0.5rem;
    color: #444;
}

/* ── Tabs ────────────────────────────────────────────────────────────────── */
button[data-baseweb="tab"] {
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.1px !important;
}

/* ── Dataframe tweaks ────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}
</style>
"""

# CTR benchmarks by position and intent
CTR_BENCH_INFO = {
    1: 35.0, 2: 20.0, 3: 14.0, 4: 10.0, 5: 8.0,
    6: 6.0,  7: 4.5,  8: 3.5,  9: 3.0, 10: 2.5,
}
CTR_BENCH_COMM = {
    1: 15.0, 2: 10.0, 3: 8.0, 4: 6.0, 5: 5.0,
    6: 4.0,  7: 3.5,  8: 3.0,  9: 2.5, 10: 2.0,
}
CTR_BENCH_BRAND = {
    1: 42.0, 2: 28.0, 3: 18.0, 4: 12.0, 5: 9.0,
    6: 6.5,  7: 5.0,  8: 4.0,  9: 3.5, 10: 3.0,
}

COMMERCIAL_SIGNALS = [
    "buy", "price", "cost", "for sale", "shop", "order", "purchase",
    "quote", "dealer", "supplier", "wholesale", "oem", "cheap", "best",
    "top", "review", "vs", "compare", "compatible", "attachment",
    "kit", "part", "replace", "install", "near me", "shipping",
]

INTENT_COLORS = {
    "Brand":                "#1565c0",
    "Informational":        "#f9a825",
    "Commercial / Product": "#388e3c",
}

PRIORITY_COLOR = {
    "URGENT": "alert-red",
    "HIGH":   "alert-amber",
    "MEDIUM": "alert-amber",
    "LOW":    "alert-green",
}
