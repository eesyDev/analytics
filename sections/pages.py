import streamlit as st
import plotly.express as px

def render(pages, _):
    st.markdown(f'<div class="section-header">{_("📄 Top Pages — Performance & Type")}</div>', unsafe_allow_html=True)

    pages_top = pages.nlargest(20, "Clicks").copy()
    pages_top["Label"] = (
        pages_top["Page"]
        .str.replace(r"https?://[^/]+", "", regex=True)
        .str[:70]
    )

    col_p1, col_p2 = st.columns([3, 2])
    with col_p1:
        fig = px.bar(
            pages_top, x="Clicks", y="Label", orientation="h",
            color="Type",
            color_discrete_map={
                "Informational / Blog": "#d32f2f",
                "Product / Category":   "#388e3c",
            },
            title=_("Top 20 pages — red = informational/blog"),
            text="Clicks", height=560,
        )
        fig.update_layout(
            margin=dict(t=40, b=10, l=10),
            yaxis=dict(autorange="reversed"),
            legend=dict(orientation="h", y=1.08),
            plot_bgcolor="white",
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col_p2:
        st.markdown(_("**CTR & Position for top pages**"))
        
        display_cols = ["Label", "Clicks", "CTR", "Position"]
        formats = {"CTR": "{:.2f}%", "Position": "{:.1f}"}
        
        if "Sessions" in pages.columns and "Revenue" in pages.columns:
            display_cols.extend(["Sessions", "Revenue"])
            formats["Revenue"] = "${:,.2f}"
            formats["Sessions"] = "{:,.0f}"

        st.dataframe(
            pages_top[display_cols]
            .sort_values("Clicks", ascending=False)
            .style
            .format(formats)
            .background_gradient(subset=["CTR"], cmap="RdYlGn"),
            height=560, use_container_width=True,
        )
