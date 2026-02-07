# ============================================================
# GLOBAL STYLESHEET — injected once via inject_css()
# ============================================================

import streamlit as st
from ui.theme import (
    CHARCOAL, CHARCOAL_LIGHT, SLATE, WHITE, OFF_WHITE, WARM_GRAY,
    BORDER_LIGHT, ACCENT_PRIMARY, ACCENT_SECONDARY, ACCENT_MUTED,
    ACCENT_PALE, POSITIVE, NEGATIVE,
    FONT_HEADING, FONT_BODY, CARD_RADIUS,
)

_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@300;400;500;600&display=swap');

    .stApp {{ background: {OFF_WHITE}; }}
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
        border-bottom: 2px solid {ACCENT_PRIMARY};
    }}

    /* ---- Sidebar (light, warm) ---- */
    section[data-testid="stSidebar"] {{
        background: {WARM_GRAY};
        border-right: 1px solid {BORDER_LIGHT};
    }}
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown div {{
        color: {CHARCOAL};
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
        font-size: 0.9rem !important; background-color: {WARM_GRAY} !important;
        border-radius: 8px !important;
    }}

    /* ---- Charts container ---- */
    .stPlotlyChart {{
        background: {WHITE}; border-radius: {CARD_RADIUS};
        padding: 1rem; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        border: 1px solid {BORDER_LIGHT};
    }}

    /* ---- Custom HTML table (driving breakdown, etc.) ---- */
    .premium-table {{
        width: 100%; border-collapse: separate; border-spacing: 0;
        font-family: {FONT_BODY}; background: {WHITE};
        border-radius: {CARD_RADIUS}; overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
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
        border-bottom: 1px solid {BORDER_LIGHT}; font-size: 0.9rem;
        color: {CHARCOAL};
    }}
    .premium-table td:first-child {{ text-align: left; padding-left: 1.25rem; font-weight: 500; }}
    .premium-table tr:last-child td {{ border-bottom: none; }}
    .premium-table .row-primary {{ background: {WARM_GRAY}; }}
    .premium-table .row-primary td {{ font-weight: 600; font-size: 1rem; padding: 1rem 0.75rem; }}
    .premium-table .row-header {{ background: {ACCENT_PALE}; }}
    .premium-table .row-header td {{
        color: {SLATE}; font-weight: 600; font-size: 0.7rem;
        text-transform: uppercase; letter-spacing: 0.05em; padding: 0.6rem 0.75rem;
    }}
    .premium-table .row-highlight {{
        background: {ACCENT_PALE};
    }}
    .premium-table .row-highlight td {{ font-weight: 700; color: {ACCENT_PRIMARY}; padding: 0.875rem 0.75rem; }}
    .premium-table .row-danger {{
        background: {NEGATIVE_BG};
    }}
    .premium-table .row-danger td {{ font-weight: 700; color: {NEGATIVE}; padding: 0.875rem 0.75rem; }}
    .premium-table .indent {{ padding-left: 2rem !important; }}

    /* ---- Tabs ---- */
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px; background-color: {WARM_GRAY}; border-radius: 8px 8px 0 0;
        padding: 0 24px; font-family: {FONT_BODY}; font-weight: 500;
        color: {CHARCOAL} !important; border: 1px solid {BORDER_LIGHT};
        border-bottom: none;
    }}
    .stTabs [data-baseweb="tab"]:hover {{ background-color: {ACCENT_PALE}; }}
    .stTabs [aria-selected="true"] {{
        background-color: {WHITE} !important;
        color: {ACCENT_PRIMARY} !important; font-weight: 600 !important;
        border-bottom: 2px solid {ACCENT_PRIMARY} !important;
    }}
</style>
"""

# Need NEGATIVE_BG from theme — import it
from ui.theme import NEGATIVE_BG


def inject_css():
    """Call once at app start to inject the global stylesheet."""
    st.markdown(_CSS, unsafe_allow_html=True)
