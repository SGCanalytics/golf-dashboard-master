# ============================================================
# GLOBAL STYLESHEET — injected once via inject_css()
# ============================================================

import streamlit as st
from ui.theme import (
    CHARCOAL, CHARCOAL_LIGHT, SLATE, WHITE, OFF_WHITE, WARM_GRAY,
    BORDER_LIGHT, ACCENT_PRIMARY, ACCENT_SECONDARY, ACCENT_MUTED,
    POSITIVE, NEGATIVE, FONT_HEADING, FONT_BODY, CARD_RADIUS,
)

_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@300;400;500;600&display=swap');

    .stApp {{ background: linear-gradient(180deg, {OFF_WHITE} 0%, #f5f5f5 100%); }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    h1, h2, h3 {{ font-family: {FONT_HEADING} !important; letter-spacing: -0.02em; }}
    p, span, div, label, .stMarkdown {{ font-family: {FONT_BODY}; }}

    /* ---- Page titles ---- */
    .main-title {{
        font-family: {FONT_HEADING}; font-size: 2.8rem; font-weight: 700;
        color: {CHARCOAL}; margin-bottom: 0.25rem;
    }}
    .main-subtitle {{
        font-family: {FONT_BODY}; font-size: 1rem; color: {SLATE};
        font-weight: 400; margin-bottom: 2rem; padding-bottom: 1.5rem;
        border-bottom: 3px solid {ACCENT_PRIMARY};
    }}

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%);
    }}

    /* ---- Data tables ---- */
    .stDataFrame th {{
        text-align: center !important; background-color: {WARM_GRAY} !important;
        color: {CHARCOAL} !important; font-family: {FONT_BODY} !important;
        font-weight: 600 !important; font-size: 0.8rem !important;
        border-bottom: 2px solid {ACCENT_PRIMARY} !important;
    }}
    .stDataFrame td {{
        text-align: center !important; font-family: {FONT_BODY} !important;
        font-size: 0.85rem !important;
    }}

    /* ---- Expanders ---- */
    .streamlit-expanderHeader {{
        font-family: {FONT_BODY} !important; font-weight: 500 !important;
        font-size: 0.9rem !important; background-color: #f8f8f8 !important;
        border-radius: 8px !important;
    }}

    /* ---- Charts container ---- */
    .stPlotlyChart {{
        background: {WHITE}; border-radius: {CARD_RADIUS};
        padding: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid {BORDER_LIGHT};
    }}

    /* ---- Custom HTML table (driving breakdown, etc.) ---- */
    .premium-table {{
        width: 100%; border-collapse: separate; border-spacing: 0;
        font-family: {FONT_BODY}; background: {WHITE};
        border-radius: {CARD_RADIUS}; overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    }}
    .premium-table th {{
        background: {WARM_GRAY}; color: {CHARCOAL}; font-weight: 600;
        font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;
        padding: 1rem 0.75rem; text-align: center;
        border-bottom: 2px solid {ACCENT_PRIMARY};
    }}
    .premium-table th:first-child {{ text-align: left; padding-left: 1.25rem; }}
    .premium-table td {{
        padding: 0.75rem; text-align: center;
        border-bottom: 1px solid #f0f0f0; font-size: 0.9rem; color: {CHARCOAL};
    }}
    .premium-table td:first-child {{ text-align: left; padding-left: 1.25rem; font-weight: 500; }}
    .premium-table tr:last-child td {{ border-bottom: none; }}
    .premium-table .row-primary {{ background: #f8f8f8; }}
    .premium-table .row-primary td {{ font-weight: 600; font-size: 1rem; padding: 1rem 0.75rem; }}
    .premium-table .row-header {{ background: #f0ede5; }}
    .premium-table .row-header td {{
        color: {SLATE}; font-weight: 600; font-size: 0.7rem;
        text-transform: uppercase; letter-spacing: 0.05em; padding: 0.6rem 0.75rem;
    }}
    .premium-table .row-highlight {{
        background: linear-gradient(90deg, {ACCENT_PRIMARY} 0%, {ACCENT_SECONDARY} 100%);
    }}
    .premium-table .row-highlight td {{ font-weight: 700; color: {WHITE}; padding: 0.875rem 0.75rem; }}
    .premium-table .row-danger {{
        background: linear-gradient(90deg, {NEGATIVE} 0%, #b91c1c 100%);
    }}
    .premium-table .row-danger td {{ font-weight: 700; color: {WHITE}; padding: 0.875rem 0.75rem; }}
    .premium-table .indent {{ padding-left: 2rem !important; }}

    /* ---- Tabs ---- */
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px; background-color: #f0f0f0; border-radius: 8px 8px 0 0;
        padding: 0 24px; font-family: {FONT_BODY}; font-weight: 500;
        color: {CHARCOAL} !important;
    }}
    .stTabs [data-baseweb="tab"]:hover {{ background-color: #ddd; }}
    .stTabs [aria-selected="true"] {{
        background-color: {ACCENT_PRIMARY} !important;
        color: {WHITE} !important; font-weight: 600 !important;
    }}
</style>
"""


def inject_css():
    """Call once at app start to inject the global stylesheet."""
    st.markdown(_CSS, unsafe_allow_html=True)
