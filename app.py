import streamlit as st
from utils.fire_utils import fetch_live_fires
from utils.flood_utils import get_rainfall_risk
from utils.seismic_utils import get_seismic_zone
from utils.routing_utils import get_response_time
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="AI Property Underwriting Tool - India", layout="wide")
st.title("🏠 AI Property Underwriting Tool (India)")
st.markdown("Enter coordinates of the property to assess NATCAT and emergency exposure risk.")

col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("Latitude", value=28.6139, format="%.6f")
with col2:
    lon = st.number_input("Longitude", value=77.2090, format="%.6f")

if st.button("Analyze Risk"):
    st.subheader("📊 Exposure Results")
    seismic_zone = get_seismic_zone(lat, lon)
    rainfall_risk = get_rainfall_risk(lat, lon)
    response_time = get_response_time(lat, lon)
    fire_nearby = fetch_live_fires(lat, lon)

    summary_data = {
        "Seismic Zone": [seismic_zone],
        "Rainfall Risk": [rainfall_risk],
        "Fire Response Time": [response_time],
        "Nearby Fire Hotspots (last 24h)": [len(fire_nearby) if fire_nearby is not None else "N/A"]
    }
    st.table(pd.DataFrame(summary_data))

    st.subheader("🗺️ Map of Risk Location & Hotspots")
    m = folium.Map(location=[lat, lon], zoom_start=8)
    folium.Marker([lat, lon], tooltip="Property Location", icon=folium.Icon(color="blue")).add_to(m)
    if fire_nearby is not None:
        for _, row in fire_nearby.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=4,
                color='red',
                fill=True,
                fill_color='red',
                tooltip="Fire Hotspot"
            ).add_to(m)
    st_folium(m, width=700, height=500)