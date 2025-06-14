import streamlit as st
from utils.elevation_utils import get_elevation, classify_flood_risk
from utils.exposure_utils import get_nearby_exposures
from utils.fire_utils import fetch_live_fires
from utils.pdf_utils import generate_pdf_report
import pandas as pd
import folium
from streamlit_folium import st_folium
import tempfile
import os

st.set_page_config(page_title="AI Property Underwriter - India", layout="wide")
st.title("🏠 AI Property Underwriting Tool - India")
st.markdown("Enter coordinates to assess risk and generate a printable PDF report.")

col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("Latitude", value=28.6139, format="%.6f")
with col2:
    lon = st.number_input("Longitude", value=77.2090, format="%.6f")

if st.button("Analyze & Generate Report"):
    st.subheader("📊 Risk Assessment Summary")

    elevation = get_elevation(lat, lon)
    flood_risk = classify_flood_risk(elevation)
    exposure_count, exposures = get_nearby_exposures(lat, lon)
    fire_data = fetch_live_fires(lat, lon)
    fire_count = len(fire_data) if fire_data is not None else "Unavailable"

    st.markdown(f"**Elevation:** {elevation if elevation is not None else 'Unavailable'} m")
    st.markdown(f"**Urban Flood Risk:** {flood_risk}")
    st.markdown(f"**Nearby Fire-prone Units:** {exposure_count}")
    st.markdown(f"**Nearby Fire Hotspots (Last 24h):** {fire_count}")

    # Map view
    st.subheader("🗺️ Map View")
    m = folium.Map(location=[lat, lon], zoom_start=10)
    folium.Marker([lat, lon], tooltip="Property Location", icon=folium.Icon(color="blue")).add_to(m)
    if fire_data is not None:
        for _, row in fire_data.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=4,
                color='red',
                fill=True,
                fill_color='red',
                tooltip="Fire Hotspot"
            ).add_to(m)
    st_folium(m, width=700, height=500)

    # Prepare data for PDF
    report_data = {
        "Coordinates": f"Latitude: {lat}, Longitude: {lon}",
        "Elevation": f"{elevation if elevation is not None else 'Unavailable'} m",
        "Urban Flood Risk": flood_risk,
        "Borrowed Fire Exposure": f"{exposure_count} hazardous facilities nearby",
        "Nearby Fire Hotspots (24h)": fire_count
    }

    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    generate_pdf_report(report_data, tmp_pdf.name)

    with open(tmp_pdf.name, "rb") as f:
        st.download_button(
            label="📄 Download PDF Report",
            data=f,
            file_name="underwriting_report.pdf",
            mime="application/pdf"
        )

    os.unlink(tmp_pdf.name)