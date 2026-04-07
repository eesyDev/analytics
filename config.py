CSS = """
<style>
/* Move sidebar to the right */
.stApp {
    flex-direction: row-reverse;
}
[data-testid="stSidebarCollapsedControl"] {
    right: 0.5rem;
    left: unset;
}

.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.alert-red {
    background: #fdecea; border-left: 4px solid #d32f2f;
    border-radius: 6px; padding: 0.8rem 1rem;
    margin-bottom: 0.6rem; font-size: 0.92rem;
}
.alert-amber {
    background: #fff8e1; border-left: 4px solid #f9a825;
    border-radius: 6px; padding: 0.8rem 1rem;
    margin-bottom: 0.6rem; font-size: 0.92rem;
}
.alert-green {
    background: #e8f5e9; border-left: 4px solid #388e3c;
    border-radius: 6px; padding: 0.8rem 1rem;
    margin-bottom: 0.6rem; font-size: 0.92rem;
}
.alert-blue {
    background: #e3f2fd; border-left: 4px solid #1565c0;
    border-radius: 6px; padding: 0.8rem 1rem;
    margin-bottom: 0.6rem; font-size: 0.92rem;
}
.section-header {
    font-size: 1.1rem; font-weight: 600; color: #1a1a1a;
    margin-top: 2rem; margin-bottom: 0.5rem;
    border-bottom: 2px solid #1565c0; padding-bottom: 0.3rem;
}
.hotjar-placeholder {
    background: #f5f5f5; border: 2px dashed #bbb;
    border-radius: 10px; padding: 2rem;
    text-align: center; color: #888; margin-top: 0.5rem;
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
