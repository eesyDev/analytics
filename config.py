CSS = """
<style>
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

# CTR benchmarks by position (Backlinko / Advanced Web Ranking)
CTR_BENCH = {
    1: 28.5, 2: 15.7, 3: 11.0, 4: 8.0, 5: 7.2,
    6: 5.1,  7: 4.0,  8: 3.2,  9: 2.8, 10: 2.5,
}
CTR_BENCH_BRAND = {
    1: 42.0, 2: 28.0, 3: 18.0, 4: 12.0, 5: 9.0,
    6: 6.5,  7: 5.0,  8: 4.0,  9: 3.5,  10: 3.0,
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
