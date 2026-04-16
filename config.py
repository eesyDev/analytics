CSS = """
<style>
/* ── Layout ─────────────────────────────────────────────────────────────── */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* ── Sidebar branding ────────────────────────────────────────────────────── */
.sidebar-logo {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1565c0;
    letter-spacing: -0.3px;
    margin-bottom: 0;
}
.sidebar-tagline {
    font-size: 0.72rem;
    color: #888;
    margin-top: 0;
}
.sidebar-user {
    font-size: 0.82rem;
    color: #555;
    padding: 6px 0;
}

/* ── Sidebar nav radio → looks like a menu ──────────────────────────────── */
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
    gap: 1px !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
    padding: 0.48rem 0.9rem !important;
    border-radius: 7px !important;
    border-left: 3px solid transparent !important;
    cursor: pointer !important;
    font-size: 0.88rem !important;
    transition: background 0.12s, border-color 0.12s !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
    background: rgba(21,101,192,0.07) !important;
    border-left-color: #90caf9 !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"],
section[data-testid="stSidebar"] div[data-testid="stRadio"] label[aria-checked="true"] {
    background: rgba(21,101,192,0.12) !important;
    border-left-color: #1565c0 !important;
    font-weight: 600 !important;
    color: #1565c0 !important;
}
/* Hide radio dots */
section[data-testid="stSidebar"] div[data-testid="stRadio"] input[type="radio"] {
    display: none !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
    margin: 0 !important;
}
/* Sidebar section label */
.nav-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: #aaa;
    margin: 0.75rem 0 0.3rem 0.5rem;
}

/* ── Upload cards ────────────────────────────────────────────────────────── */
.upload-card {
    border: 1.5px solid #e8eaf0;
    border-radius: 10px;
    padding: 1.1rem 1.3rem 0.8rem;
    background: #f8f9fc;
    margin-bottom: 0.5rem;
}
.upload-card-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #1565c0;
    margin-bottom: 0.25rem;
}
.upload-card-hint {
    font-size: 0.78rem;
    color: #888;
    margin-bottom: 0.6rem;
}

/* ── Page header ─────────────────────────────────────────────────────────── */
.page-header {
    border-bottom: 2px solid #e8eaf0;
    padding-bottom: 0.75rem;
    margin-bottom: 1.25rem;
}
.page-header h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a1a2e;
}
.page-header .meta {
    font-size: 0.83rem;
    color: #888;
    margin-top: 0.2rem;
}

/* ── Section header ──────────────────────────────────────────────────────── */
.section-header {
    font-size: 1.05rem;
    font-weight: 600;
    margin-top: 1.75rem;
    margin-bottom: 0.6rem;
    border-bottom: 2px solid #1565c0;
    padding-bottom: 0.35rem;
    color: #1a1a2e;
}

/* ── Alert boxes — light mode ────────────────────────────────────────────── */
.alert-red {
    background: #fdecea; border-left: 4px solid #d32f2f;
    border-radius: 6px; padding: 0.8rem 1rem;
    margin-bottom: 0.6rem; font-size: 0.92rem; color: #7f1d1d;
}
.alert-amber {
    background: #fff8e1; border-left: 4px solid #f9a825;
    border-radius: 6px; padding: 0.8rem 1rem;
    margin-bottom: 0.6rem; font-size: 0.92rem; color: #78350f;
}
.alert-green {
    background: #e8f5e9; border-left: 4px solid #388e3c;
    border-radius: 6px; padding: 0.8rem 1rem;
    margin-bottom: 0.6rem; font-size: 0.92rem; color: #14532d;
}
.alert-blue {
    background: #e3f2fd; border-left: 4px solid #1565c0;
    border-radius: 6px; padding: 0.8rem 1rem;
    margin-bottom: 0.6rem; font-size: 0.92rem; color: #1e3a8a;
}

/* ── Alert boxes — dark mode ─────────────────────────────────────────────── */
@media (prefers-color-scheme: dark) {
    .upload-card  { background: #1e2433; border-color: #2e3450; }
    .upload-card-title { color: #90caf9; }
    .page-header h2 { color: #e0e0e0; }
    .page-header .meta { color: #888; }
    .section-header { color: #e0e0e0; }
    .alert-red   { background: rgba(211,47,47,0.15);  color: #fca5a5; }
    .alert-amber { background: rgba(249,168,37,0.15); color: #fcd34d; }
    .alert-green { background: rgba(56,142,60,0.15);  color: #86efac; }
    .alert-blue  { background: rgba(21,101,192,0.15); color: #93c5fd; }
}

.hotjar-placeholder {
    border: 2px dashed #bbb;
    border-radius: 10px; padding: 2rem;
    text-align: center; margin-top: 0.5rem;
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
