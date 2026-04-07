import streamlit as st
import plotly.express as px
import pandas as pd


def render(f_hotjar, f_hm_home, f_hm_product, f_hm_cart):
    st.markdown('<div class="section-header">🎥 User Behavior Analysis (Hotjar)</div>',
                unsafe_allow_html=True)

    if not f_hotjar and not any([f_hm_home, f_hm_product, f_hm_cart]):
        st.markdown(
            '<div class="alert-amber"><strong>Hotjar data not yet connected.</strong> '
            "GSC shows <em>who finds the site</em> — Hotjar reveals <em>why they don't convert.</em> "
            "Upload a funnel CSV and/or heatmap screenshots in the sidebar.</div>",
            unsafe_allow_html=True,
        )

    if f_hotjar:
        try:
            hj_df = pd.read_csv(f_hotjar)
            if "Step" in hj_df.columns and "Users" in hj_df.columns:
                st.markdown("**Conversion Funnel**")
                fig = px.funnel(hj_df, x="Users", y="Step", title="Conversion Funnel (Hotjar)")
                fig.update_layout(height=380)
                st.plotly_chart(fig, use_container_width=True)

                first_val = hj_df["Users"].iloc[0]
                display = hj_df.copy()
                display["Conversion Rate"] = (hj_df["Users"] / first_val * 100).round(1).astype(str) + "%"
                display["Drop-off %"]      = ((1 - hj_df["Users"] / first_val) * 100).round(1).astype(str) + "%"
                st.dataframe(display, use_container_width=True, hide_index=True)

                if len(hj_df) > 1:
                    diffs     = hj_df["Users"].diff().abs().fillna(0)
                    worst_idx = diffs.idxmax()
                    st.markdown(
                        f'<div class="alert-red"><strong>Biggest drop-off:</strong> '
                        f"{int(diffs[worst_idx]):,} users lost at "
                        f"<strong>{hj_df.loc[worst_idx, 'Step']}</strong>. "
                        "Highest-priority fix in the funnel.</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.warning(
                    "Hotjar CSV missing required columns: **Step** and **Users**. "
                    "Please export the funnel report with these headers."
                )
                st.dataframe(hj_df.head(), use_container_width=True)
        except Exception as e:
            st.error(f"Error reading Hotjar file: {e}")

    heatmaps = [
        ("🔥 Homepage Heatmap",     f_hm_home,    "Focus: hero CTA, navigation, above-the-fold"),
        ("🔥 Product Page Heatmap", f_hm_product, "Focus: add-to-cart, specs, pricing"),
        ("🔥 Cart Page Heatmap",    f_hm_cart,    "Focus: checkout button, trust signals"),
    ]
    loaded      = [(l, f, c) for l, f, c in heatmaps if f]
    placeholder = [(l, c)    for l, f, c in heatmaps if not f]

    if loaded:
        st.markdown("**Heatmaps**")
        for label, f, caption in loaded:
            st.markdown(f"*{label}*")
            st.image(f, use_container_width=True)
            st.caption(caption)

    if placeholder:
        cols = st.columns(len(placeholder))
        for col, (label, caption) in zip(cols, placeholder):
            col.markdown(
                f'<div class="hotjar-placeholder">'
                f'<div style="font-size:2rem">🔥</div>'
                f'<strong>{label}</strong><br><small>{caption}</small>'
                f'</div>',
                unsafe_allow_html=True,
            )
