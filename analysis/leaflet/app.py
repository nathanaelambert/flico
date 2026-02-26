import streamlit as st
import folium
from streamlit_folium import st_folium
from data_processing import get_institutions

st.set_page_config(page_title="Leaflet Flickr Commons", layout="wide")

st.title("Locating Flickr Commons pictures")

# Sidebar UI
st.sidebar.header("Map controls")
zoom = st.sidebar.slider("Zoom level", 1, 18, 13)
lat = st.sidebar.number_input("Center latitude", value=47.3769)   # Zürich
lon = st.sidebar.number_input("Center longitude", value=8.5417)

# Create Leaflet (Folium) map
m = folium.Map(location=[lat, lon], zoom_start=zoom)

# Example marker
folium.Marker(
    [lat, lon],
    popup="Center",
    tooltip="Drag or zoom the map",
).add_to(m)

# Render in Streamlit and capture interactions
map_data = st_folium(m, width=None, height=700, use_container_width=True)


# Example: load institutions
institutions = get_institutions()
st.markdown("**Institutions found:**")
st.json(institutions[:5])  # first 5