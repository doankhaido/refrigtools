import streamlit as st


def render_handbook_link():
    """
    Adds the Code of Practice handbook link to the sidebar.
    Call this function near the top of every page (home.py and each file in pages/).
    """
    st.sidebar.markdown("---")
    st.sidebar.link_button(
        "📘 Code of Practice handbook",
        "https://refrigtools.app/code-of-practice",
        use_container_width=True,
    )
    st.sidebar.caption("Installable on phone for offline use")