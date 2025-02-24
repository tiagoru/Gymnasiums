# Description: This is a Streamlit app that displays a map of Munich with Gymnasiums and the user's location.
# tryinh to help citizens to find the nearest gymnasiums in Munich
# this is a test version of the app
# Author: Tiago Russomanno
# Date: 2021-09-29
# Libraries: pandas, streamlit, folium, geopy
############################################################################################

import streamlit as st
import folium
from geopy.geocoders import Nominatim
import pandas as pd
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from geopy.distance import geodesic

# 📝 **App Header**
st.markdown("""
# 🏫 Munich Gymnasiums Map (Test Version)
This is a **Streamlit test version** that displays a map of **Munich** with Gymnasiums and the user's location.  
🔍 **Helping citizens find the nearest Gymnasiums in Munich!**  
👤 **Author**: Tiago Russomanno
---
""")

# 🚀 Load CSV Once
if "df" not in st.session_state:
    try:
        df = pd.read_csv("munich_gymnasiums_extended.csv")
        st.session_state.df = df  # Store in session state
    except Exception as e:
        st.error(f"❌ Error loading CSV: {e}")
        st.stop()

df = st.session_state.df  # Use stored data

# 📌 Ensure Latitude & Longitude Columns Exist
if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
    st.error("❌ CSV file is missing 'Latitude' or 'Longitude' columns!")
    st.stop()

# 🔄 Reload Button
if st.button("🔄 Reload Map"):
    st.session_state.user_coords = None  # Reset user coordinates
    st.rerun()  # Rerun the app

# 🔍 Manage Session State for User Coordinates
if "user_coords" not in st.session_state:
    st.session_state.user_coords = None

# 📍 User Location Input
st.header("📍 Enter Your Location")
location_input = st.text_input("Enter address or coordinates (e.g., 'Munich' or '48.18, 11.55'):")

if location_input and st.session_state.user_coords is None:  # Only run geocoder once
    geolocator = Nominatim(user_agent="my_app", timeout=10)
    try:
        location = geolocator.geocode(location_input)
        if location:
            st.session_state.user_coords = (location.latitude, location.longitude)
            st.write(f"✅ Your Location: {location.address}")
        else:
            st.error("❌ Location not found.")
    except Exception as e:
        st.error(f"❌ Error geocoding: {e}")

# 🗺️ Display Map (Only If Location is Found)
if st.session_state.user_coords:
    my_coords = st.session_state.user_coords

    # Create the map
    m = folium.Map(location=my_coords, zoom_start=12)
    folium.Marker(my_coords, popup="Your Location", icon=folium.Icon(color='red')).add_to(m)

    # 🔵 Add Distance Circles (1 km, 2 km, 3 km, 4 km, 5 km)
    for distance in [1, 2, 3, 4, 5]:
        folium.Circle(
            radius=distance * 1000,  # Convert km to meters
            location=my_coords,
            color='blue',
            fill=True,
            fill_opacity=0.1,
            popup=f"{distance} km radius"
        ).add_to(m)

    # 📌 Add Schools to the Map
    marker_cluster = MarkerCluster().add_to(m)  # Cluster for better visibility

    for _, row in df.iterrows():
        try:
            school_coords = (row["Latitude"], row["Longitude"])  # Ensure correct order
            # Calculate the distance between user location and school
            distance = geodesic(my_coords, school_coords).km
            popup_text = (f"<b>{row['School Name']}</b><br>"
                          f"Distance: {distance:.2f} km<br>"
                          f"Focus: {row.get('Focus', 'N/A')}")
            
            folium.Marker(
                location=school_coords,
                popup=popup_text,
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(marker_cluster)
        except Exception as e:
            st.error(f"❌ Error adding school: {e}")

    # 📌 Display the Map
    st_folium(m, width=700, height=500)

    # 📖 **Abbreviations Legend**
    st.markdown("### 📘 Gymnasium Focus Abbreviations")
    st.write("""
    - **HG**: Humanistisches Gymnasium  
    - **MuG**: Musisches Gymnasium  
    - **NTG**: Naturwissenschaftlich-technologisches Gymnasium  
    - **SG**: Sprachliches Gymnasium  
    - **SG.HG**: Sprachliches Gymnasium mit humanistischem Profil  
    - **WSG-S**: Wirtschafts- und Sozialwissenschaftliches Gymnasium mit sozialwissenschaftlichem Profil  
    - **WSG-W**: Wirtschafts- und Sozialwissenschaftliches Gymnasium mit wirtschaftswissenschaftlichem Profil  
    """)

