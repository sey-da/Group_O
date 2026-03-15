"""
Streamlit app for Project Okavango.
Displays world maps and dataset-specific charts for environmental data.
"""
import yaml
from pathlib import Path
from ai_analysis import AIAnalysis          
import requests
import math
from PIL import Image
from io import BytesIO

import os
import sys

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

sys.path.append(os.path.dirname(__file__))
from class_environment_data import EnvironmentData


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


@st.cache_resource
def load_data() -> EnvironmentData:
    """Load and cache the EnvironmentData instance."""
    return EnvironmentData()


def chart_gainers_losers(gdf, value_col: str, label: str, title: str) -> None:
    """
    Bar chart showing top 5 countries gaining (green)
    and top 5 countries losing (red) for the given column.
    """
    df = gdf[["NAME", value_col]].dropna()
    top5 = df.nlargest(5, value_col)
    bottom5 = df.nsmallest(5, value_col)
    import pandas as pd
    combined = pd.concat([top5, bottom5])
    colors = ["#2ecc71"] * 5 + ["#e74c3c"] * 5
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.barh(combined["NAME"], combined[value_col], color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel(label)
    ax.set_title(title)
    ax.invert_yaxis()
    gain_patch = mpatches.Patch(color="#2ecc71", label="Top 5 Gaining")
    loss_patch = mpatches.Patch(color="#e74c3c", label="Top 5 Losing")
    ax.legend(handles=[gain_patch, loss_patch])
    st.pyplot(fig)


def chart_top_only(gdf, value_col: str, label: str, title: str) -> None:
    """Bar chart showing the top 10 countries with the highest values."""
    df = gdf[["NAME", value_col]].dropna()
    top10 = df.nlargest(10, value_col)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.barh(top10["NAME"], top10[value_col], color="#e74c3c")
    ax.set_xlabel(label)
    ax.set_title(title)
    ax.invert_yaxis()
    st.pyplot(fig)


def chart_top_bottom(gdf, value_col: str, label: str, title: str) -> None:
    """Bar chart showing top 5 (green) and bottom 5 (orange) countries."""
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
    top_patch = mpatches.Patch(color="#2ecc71", label="Top 5")
    bot_patch = mpatches.Patch(color="#e67e22", label="Bottom 5")
    ax.legend(handles=[top_patch, bot_patch])
    st.pyplot(fig)


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

    latitude = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=-3.47)
    longitude = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=-62.21)
    zoom = st.slider("Zoom Level", min_value=1, max_value=18, value=10)

    st.write("Selected coordinates")
    st.write("Latitude:", latitude)
    st.write("Longitude:", longitude)
    st.write("Zoom:", zoom)

    if st.button("Download Satellite Image"):
        lat_rad = math.radians(latitude)
        n = 2 ** zoom
        xtile = int((longitude + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        url = f"https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{ytile}/{xtile}"
        response = requests.get(url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            Path("images").mkdir(exist_ok=True)
            filename = f"images/satellite_{latitude}_{longitude}_{zoom}.png"
            image.save(filename)
            st.success("Image downloaded successfully")
            st.image(image)
        else:
            st.error("Image download failed")

    # ─────────────────────────────────────────────────────────
    # BUTTON TO RUN THE AI ANALYSIS
    # ─────────────────────────────────────────────────────────

    if st.button("Analyse Area with AI"):         
        image_path = f"images/satellite_{latitude}_{longitude}_{zoom}.png"

        if not Path(image_path).exists():
            st.error("No image found for these coordinates. Please download the image first.")
        else:
            ai = AIAnalysis(config_path="models.yaml") 

            st.subheader("Satellite Image and AI Description")
            col1, col2 = st.columns(2)

            with col1:
                st.image(image_path, caption="Satellite Image", width=500)

            with col2:
                with st.spinner("Analysing image... (this may take 1-2 minutes)"):
                    description = ai.describe_image(image_path)    
                st.markdown("**AI Image Description:**")
                st.write(description)

            st.subheader("Environmental Risk Assessment")

            with st.spinner("Assessing environmental risk..."):
                result = ai.assess_environmental_risk(description)
            ai.log_to_database(
                latitude=latitude,
                longitude=longitude,
                zoom=zoom,
                image_description=description,
                text_response=result["response"],
                danger=result["is_at_risk"]
            )  

            st.markdown("**Risk Analysis:**")
            st.write(result["response"])

            if result["is_at_risk"]:
                st.error("⚠️ ENVIRONMENTAL RISK DETECTED — This area may be at risk.")
            else:
                st.success("✅ NO SIGNIFICANT RISK DETECTED — This area appears safe.")   