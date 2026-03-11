"""
Streamlit app for Project Okavango.
Displays world maps and dataset-specific charts for environmental data.
"""

import os
import sys

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

sys.path.append(os.path.dirname(__file__))
from class_environment_data import EnvironmentData


# ─────────────────────────────────────────────────────────────
# DATASET CONFIG
# Each entry defines:
#   - value_col:    the actual data column to plot on the map/chart
#   - label:        readable label for axes and titles
#   - chart_type:   "gainers_losers" = split top/bottom with colors
#                   "top_bottom"     = top 5 and bottom 5, both shown
#                   "top_only"       = only worst offenders (deforestation)
#   - cmap:         matplotlib colormap for the world map
# ─────────────────────────────────────────────────────────────

DATASET_CONFIG: dict[str, dict] = {
    "Annual Change in Forest Area": {
        "value_col": "Net_Change_Forest_Area",
        "label": "Net Change in Forest Area (ha)",
        "chart_type": "gainers_losers",
        "cmap": "RdYlGn",
    },
    "Annual Deforestation": {
        "value_col": "_1D_Deforestation",
        "label": "Deforested Area (ha)",
        "chart_type": "top_only",
        "cmap": "Reds",
    },
    "Share of Land Protected": {
        "value_col": "Er_Lnd_Ptld_Zs",
        "label": "Protected Land (%)",
        "chart_type": "top_bottom",
        "cmap": "Greens",
    },
    "Share of Land Degraded": {
        "value_col": "_15_2_1__Ag_Lnd_Frstchg",
        "label": "Annual Forest Change Rate (%)",
        "chart_type": "gainers_losers",
        "cmap": "RdYlGn",
    },
    "Forest Area Total Share": {
        "value_col": "Forest_Share",
        "label": "Forest Area (% of land)",
        "chart_type": "top_bottom",
        "cmap": "YlGn",
    },
}


# ─────────────────────────────────────────────────────────────
# LOAD DATA
# st.cache_resource means this only runs once per session —
# data won't re-download every time the user touches a widget
# ─────────────────────────────────────────────────────────────

@st.cache_resource
def load_data() -> EnvironmentData:
    """Load and cache the EnvironmentData instance."""
    return EnvironmentData()


# ─────────────────────────────────────────────────────────────
# CHART FUNCTIONS
# One function per chart type, each tailored to its dataset
# ─────────────────────────────────────────────────────────────

def chart_gainers_losers(gdf, value_col: str, label: str, title: str) -> None:
    """
    Bar chart showing top 5 countries gaining (green)
    and top 5 countries losing (red) for the given column.
    Used for: Annual Change in Forest Area, Share of Land Degraded.
    """
    df = gdf[["NAME", value_col]].dropna()

    top5 = df.nlargest(5, value_col)    # biggest positive values
    bottom5 = df.nsmallest(5, value_col)  # biggest negative values

    import pandas as pd
    combined = pd.concat([top5, bottom5])
    colors = ["#2ecc71"] * 5 + ["#e74c3c"] * 5

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.barh(combined["NAME"], combined[value_col], color=colors)
    ax.axvline(0, color="black", linewidth=0.8)  # zero reference line
    ax.set_xlabel(label)
    ax.set_title(title)
    ax.invert_yaxis()

    # Legend
    gain_patch = mpatches.Patch(color="#2ecc71", label="Top 5 Gaining")
    loss_patch = mpatches.Patch(color="#e74c3c", label="Top 5 Losing")
    ax.legend(handles=[gain_patch, loss_patch])

    st.pyplot(fig)


def chart_top_only(gdf, value_col: str, label: str, title: str) -> None:
    """
    Bar chart showing the top 10 countries with the highest values.
    Used for: Annual Deforestation (worst deforesters).
    """
    df = gdf[["NAME", value_col]].dropna()
    top10 = df.nlargest(10, value_col)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.barh(top10["NAME"], top10[value_col], color="#e74c3c")
    ax.set_xlabel(label)
    ax.set_title(title)
    ax.invert_yaxis()

    st.pyplot(fig)


def chart_top_bottom(gdf, value_col: str, label: str, title: str) -> None:
    """
    Bar chart showing top 5 (green) and bottom 5 (orange) countries.
    Used for: Share of Land Protected, Forest Area Total Share.
    """
    df = gdf[["NAME", value_col]].dropna()
    top5 = df.nlargest(5, value_col)
    bottom5 = df.nsmallest(5, value_col)

    import pandas as pd
    combined = pd.concat([top5, bottom5])
    colors = ["#2ecc71"] * 5 + ["#e67e22"] * 5

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.barh(combined["NAME"], combined[value_col], color=colors)
    ax.set_xlabel(label)
    ax.set_title(title)
    ax.invert_yaxis()

    # Legend
    top_patch = mpatches.Patch(color="#2ecc71", label="Top 5")
    bot_patch = mpatches.Patch(color="#e67e22", label="Bottom 5")
    ax.legend(handles=[top_patch, bot_patch])

    st.pyplot(fig)


# ─────────────────────────────────────────────────────────────
# PAGE SETUP
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Project Okavango",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Project Okavango — Environmental Data Explorer")

data = load_data()
maps = data.list_available_maps()

page = st.sidebar.radio(
    "Select Page",
    ["Page 1 - Data Explorer", "Page 2 - Image Viewer"]
)

if page == "Page 1 - Data Explorer":
    selected_name = st.selectbox(
        label="Select a dataset to explore:",
        options=list(maps.keys())
    )

    gdf = maps[selected_name]
    config = DATASET_CONFIG[selected_name]
    value_col = config["value_col"]
    label = config["label"]


    # ─────────────────────────────────────────────────────────────
    # WORLD MAP
    # ─────────────────────────────────────────────────────────────

    st.subheader(f"🗺️ World Map — {selected_name}")

    fig, ax = plt.subplots(1, 1, figsize=(18, 8))
    gdf.plot(
        column=value_col,
        ax=ax,
        legend=True,
        legend_kwds={"label": label, "orientation": "horizontal"},
        cmap=config["cmap"],
        missing_kwds={"color": "lightgrey", "label": "No data"},
        edgecolor="black",
        linewidth=0.3
    )
    ax.set_title(selected_name, fontsize=14)
    ax.axis("off")
    st.pyplot(fig)


    # ─────────────────────────────────────────────────────────────
    # CHART — specific to each dataset
    # ─────────────────────────────────────────────────────────────

    st.subheader(f"📊 {selected_name} — Country Breakdown")

    chart_type = config["chart_type"]

    if chart_type == "gainers_losers":
        chart_gainers_losers(gdf, value_col, label, selected_name)
    elif chart_type == "top_only":
        chart_top_only(gdf, value_col, label, selected_name)
    elif chart_type == "top_bottom":
        chart_top_bottom(gdf, value_col, label, selected_name)

elif page == "Page 2 - Image Viewer":

    st.header("🛰️ Select Location for Satellite Image")

    latitude = st.number_input(
        "Latitude",
        min_value=-90.0,
        max_value=90.0,
        value=0.0
    )

    longitude = st.number_input(
        "Longitude",
        min_value=-180.0,
        max_value=180.0,
        value=0.0
    )

    zoom = st.slider(
        "Zoom Level",
        min_value=1,
        max_value=18,
        value=10
    )

    st.write("Selected coordinates")
    st.write("Latitude:", latitude)
    st.write("Longitude:", longitude)
    st.write("Zoom:", zoom)