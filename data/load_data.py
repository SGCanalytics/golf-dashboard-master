import pandas as pd
import streamlit as st

# ============================================================
# CONFIG
# ============================================================

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZZ8-dHrvrfl8YQnRSLpCYS6GjTHpXQm2uVuqS0X5t3yOxhciFnvxlLSSMX_gplveVmlP5Uz8nOmJF/pub?gid=0&single=true&output=csv"


# ============================================================
# HELPER FUNCTIONS (LOCAL TO DATA LOADING)
# ============================================================

def determine_par(distance):
    """Assign par based on starting distance of tee shot."""
    if distance <= 245:
        return 3
    elif distance <= 475:
        return 4
    return 5


def determine_shot_type(start_location, start_distance, par):
    """Unified shot type logic."""
    if start_distance is None:
        return 'Other'
    if start_location == 'Green':
        return 'Putt'
    if start_location == 'Tee':
        return 'Approach' if par == 3 else 'Driving'
    if start_location == 'Recovery':
        return 'Recovery'
    if start_distance < 50:
        return 'Short Game'
    if start_location in ['Fairway', 'Rough', 'Sand'] and 50 <= start_distance <= 245:
        return 'Approach'
    return 'Other'


# ============================================================
# MAIN DATA LOADER
# ============================================================

@st.cache_data(ttl=300)
def load_data():
    """
    Load, clean, and enrich the dataset.
    This function is shared across all colleges.
    """
    df = pd.read_csv(SHEET_URL)

    # Clean strings
    df['Player'] = df['Player'].str.strip().str.title()
    df['Course'] = df['Course'].str.strip().str.title()
    df['Tournament'] = df['Tournament'].str.strip().str.title()

    # Compute par from first shot
    first_shots = df[df['Shot'] == 1].copy()
    first_shots['Par'] = first_shots['Starting Distance'].apply(determine_par)

    df = df.merge(
        first_shots[['Round ID', 'Hole', 'Par']],
        on=['Round ID', 'Hole'],
        how='left'
    )

    # Shot type
    df['Shot Type'] = df.apply(
        lambda row: determine_shot_type(
            row['Starting Location'],
            row['Starting Distance'],
            row['Par']
        ),
        axis=1
    )

    # Unique shot ID
    df['Shot ID'] = (
        df['Round ID'] +
        '-H' + df['Hole'].astype(str) +
        '-S' + df['Shot'].astype(str)
    )

    # Date conversion
    df['Date'] = pd.to_datetime(df['Date'])

    return df
