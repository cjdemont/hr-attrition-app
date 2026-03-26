# =============================================================================
# components/section_header.py
# Reusable section header with title, subtitle, and body text blocks.
# All text comes from text_content.yaml via the cfg dict passed in.
# =============================================================================

import streamlit as st


def section_header(title: str, subtitle: str = "", body: str = "", body_2: str = ""):
    st.markdown(
        f"""
        <div style="
            border-left: 4px solid #E6772E;
            padding: 0.1rem 0 0.1rem 1rem;
            margin-bottom: 0.5rem;
        ">
            <h2 style="margin: 0; color: #3D6B8E;">{title}</h2>
            {'<p style="margin: 0.2rem 0 0; color: #5F5E5A; font-size: 0.95rem;">' + subtitle + '</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if body:
        st.markdown(body)
    if body_2:
        st.markdown(body_2)


def pull_quote(text: str):
    st.markdown(
        f"""
        <blockquote style="
            border-left: 4px solid #3D6B8E;
            background-color: #EAF1F7;
            padding: 1rem 1.25rem;
            border-radius: 0 8px 8px 0;
            color: #2C3E50;
            font-style: italic;
            margin: 1rem 0;
        ">
            {text}
        </blockquote>
        """,
        unsafe_allow_html=True,
    )


def interaction_hint(text: str):
    st.markdown(
        f"""
        <p style="
            font-size: 0.85rem;
            color: #888780;
            font-style: italic;
            margin-bottom: 0.5rem;
        ">
            ↕ {text}
        </p>
        """,
        unsafe_allow_html=True,
    )


def divider():
    st.markdown(
        """<hr style="border: none; border-top: 1px solid #D3D1C7; margin: 2.5rem 0;">""",
        unsafe_allow_html=True,
    )
