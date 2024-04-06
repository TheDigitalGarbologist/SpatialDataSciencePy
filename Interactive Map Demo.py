import streamlit as st
import streamlit.components.v1 as components

# HTML and JS for the Leaflet map
leaflet_map_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <style>
        #map { height: 400px; }
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([51.505, -0.09], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }).addTo(map);
    </script>
</body>
</html>
"""

def main():
    st.title("Streamlit Leaflet Map Integration")

    # Use the `components.html` function to render the custom HTML/JS for the Leaflet map
    components.html(leaflet_map_html, height=450)

if __name__ == "__main__":
    main()
