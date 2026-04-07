import streamlit as st
import plotly.express as px


def render(pages):
    st.markdown('<div class="section-header">📄 Top Pages — Performance & Type</div>',
                unsafe_allow_html=True)

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
            title="Top 20 pages — red = informational/blog",
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
        st.markdown("**CTR & Position for top pages**")
        st.dataframe(
            pages_top[["Label", "Clicks", "CTR", "Position"]]
            .sort_values("Clicks", ascending=False)
            .style
            .format({"CTR": "{:.2f}%", "Position": "{:.1f}"})
            .background_gradient(subset=["CTR"], cmap="RdYlGn"),
            height=560, use_container_width=True,
        )
