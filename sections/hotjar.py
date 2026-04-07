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
                
                # Общая конверсия (от начала)
                display["Total CR"] = (hj_df["Users"] / first_val * 100).round(1).astype(str) + "%"
                
                # Профессиональный анализ: Step-to-Step конверсия (отвал на каждом шаге)
                step_cr_num = (hj_df["Users"] / hj_df["Users"].shift(1) * 100).round(1)
                display["Step CR (от пред. шага)"] = step_cr_num.fillna(100).astype(str) + "%"
                display["Step Drop-off (потеря)"] = (100 - step_cr_num).fillna(0).astype(str) + "%"
                
                # Переставляем колонки для красивого вывода
                display = display[["Step", "Users", "Total CR", "Step CR (от пред. шага)", "Step Drop-off (потеря)"]]
                st.dataframe(display, use_container_width=True, hide_index=True)

                if len(hj_df) > 1:
                    # Находим шаг с самым большим ПРОЦЕНТНЫМ отвалом
                    step_dropoffs = (1 - hj_df["Users"] / hj_df["Users"].shift(1)) * 100
                    # shift(1) даёт NaN для первого шага — idxmax() его игнорирует, но страхуемся
                    valid = step_dropoffs.dropna()
                    if valid.empty:
                        st.info("Недостаточно данных для анализа bottleneck.")
                    else:
                        worst_idx = valid.idxmax()
                        worst_drop_pct = valid[worst_idx]

                        worst_step_name = hj_df.loc[worst_idx, 'Step']
                        prev_idx = hj_df.index[hj_df.index.get_loc(worst_idx) - 1]
                        prev_step_name = hj_df.loc[prev_idx, 'Step']

                        st.markdown(
                            f'<div class="alert-red"><strong>Критическое "Бутылочное Горлышко":</strong> '
                            f'Самый большой отвал происходит при переходе от <strong>{prev_step_name}</strong> '
                            f'к <strong>{worst_step_name}</strong>. Здесь уходит '
                            f'<strong>{worst_drop_pct:.1f}%</strong> потенциальных покупателей.</div>',
                            unsafe_allow_html=True,
                        )

                        # E-commerce гипотезы для брошенной корзины/чекаута
                        worst_step_lower = str(worst_step_name).lower()
                        prev_step_lower  = str(prev_step_name).lower()
                        if any(k in worst_step_lower or k in prev_step_lower
                               for k in ["cart", "checkout"]):
                            st.markdown(
                                '<div class="alert-amber"><strong>💡 E-commerce инсайты (Cart / Checkout Abandonment):</strong><ul>'
                                '<li><strong>Freight Shipping Shock:</strong> Доставка тяжелого оборудования стоит дорого. '
                                'Если B2B клиент видит стоимость доставки впервые только на чекауте — он уходит. '
                                'Добавь калькулятор доставки на страницу продукта.</li>'
                                '<li><strong>B2B Financing / Invoice Payment:</strong> В B2B редко платят кредиткой сразу '
                                '(Net 30, Purchase Orders, Request a Quote). '
                                'Если на чекауте нет этих опций — это прямая причина отвала.</li>'
                                '<li><strong>Fit Anxiety:</strong> Клиент дошёл до корзины, но засомневался — '
                                'подойдёт ли attachment к его экскаватору. '
                                'Критически важен значок "Guaranteed Fit" и возможность связаться с экспертом прямо в корзине.</li>'
                                '</ul></div>',
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
