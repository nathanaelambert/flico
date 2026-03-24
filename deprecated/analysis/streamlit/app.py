import streamlit as st
import os
from pathlib import Path
import folium
import pandas as pd
from streamlit_folium import st_folium

st.set_page_config(page_title="Leaflet Flickr Commons", layout="wide")
st.title("Flickr Commons pictures")

@st.cache_data
def get_located_data():
    csv_path = Path(__file__).parent.parent.parent / "metadata_combined" / "flickr_commons_pictures.csv"
    df = pd.read_csv(csv_path)
    df_located = df[(df["latitude"] != 0) & (df["longitude"] != 0)]
    return df_located

df_located = get_located_data()


st.header("Map")

m = folium.Map(location=[df_located["latitude"].mean(), df_located["longitude"].mean()],
               zoom_start=2, tiles='OpenStreetMap')

data = df_located[['latitude', 'longitude', 'title', 'institution', 'image_url']].values.tolist()

callback = """
function (row) {
    // row[0] = latitude, row[1] = longitude, row[2] = title, row[3] = institution, row[4] = image_url
    var marker = L.marker(new L.LatLng(row[0], row[1]), {
        icon: L.divIcon({
            className: 'pin-marker',
            html: '<div style="background: #ff0000; width: 20px; height: 20px; border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%; border: 3px solid #fff; box-shadow: 0 2px 6px rgba(0,0,0,0.3);"></div>',
            iconSize: [26, 26],
            iconAnchor: [13, 26]
        })
    });
    
    // Build HTML popup content
    var popup_html = '<div style="font-family: Arial; max-width: 300px;">' +
                     '<h3 style="margin: 0 0 10px 0; color: #333;">' + row[2] + '</h3>' +
                     '<h4 style="margin: 0 0 15px 0; color: #666; font-weight: normal;">' + row[3] + '</h4>' +
                     '</div>';
    
    marker.bindPopup(popup_html);
    return marker;
};

"""

cluster = folium.plugins.FastMarkerCluster(data=data, callback=callback).add_to(m)

st_folium(m, width=700, height=500)













st.header("View Sample Data")
selected_columns = st.multiselect(
    "Select columns to display:",
    options=df_located.columns.tolist(),
    default=df_located.columns[:3].tolist()
)
if selected_columns:
    display_cols = [col for col in selected_columns if col in df_located.columns]
else:
    display_cols = df_located.columns.tolist()
sample_df = df_located[display_cols].sample(
    n=min(10, len(df_located)), random_state=42
).reset_index(drop=True)
st.dataframe(sample_df)

