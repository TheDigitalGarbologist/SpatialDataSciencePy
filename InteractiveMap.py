import streamlit as st
import geopandas as gpd
import json
from shapely.geometry import shape

# Initialize session state
if 'geojson_data' not in st.session_state:
    st.session_state['geojson_data'] = None

# Placeholder HTML and JavaScript
leaflet_map_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Leaflet Draw Example</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet-draw/dist/leaflet.draw.css"/>
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet-draw/dist/leaflet.draw.js"></script>
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
        var drawnItems = new L.FeatureGroup();
        map.addLayer(drawnItems);
        var drawControl = new L.Control.Draw({
            edit: {
                featureGroup: drawnItems
            },
            draw: {
                polygon: true,
                polyline: false,
                rectangle: false,
                circle: false,
                circlemarker: false,
            }
        });
        map.addControl(drawControl);
        map.on(L.Draw.Event.CREATED, function (event) {
            var layer = event.layer;
            drawnItems.addLayer(layer);
            var drawnGeoJSON = layer.toGeoJSON();
            console.log(drawnGeoJSON);
            // Here you would send the GeoJSON data back to your Streamlit app's server
        });
    </script>
</body>
</html>
"""

def convert_and_download(geojson_data):
    if geojson_data:
        gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
        gdf.set_crs(epsg=4326, inplace=True)

        # Export to Shapefile
        shapefile_path = "drawn_locations.shp"
        gdf.to_file(shapefile_path, driver='ESRI Shapefile')

        # Export to GeoJSON
        geojson_path = "drawn_locations.geojson"
        gdf.to_file(geojson_path, driver='GeoJSON')

        with open(shapefile_path, "rb") as file:
            st.download_button(label="Download Shapefile", data=file, file_name="drawn_locations.zip", mime="application/zip")

        with open(geojson_path, "rb") as file:
            st.download_button(label="Download GeoJSON", data=file, file_name="drawn_locations.geojson", mime="application/json")

def main():
    st.title("Streamlit Leaflet Map Integration")

    # Display the map
    st.components.v1.html(leaflet_map_html, height=450)

    # Button to trigger the conversion and download
    if st.button('Export Drawn Locations'):
        convert_and_download(st.session_state['geojson_data'])

if __name__ == "__main__":
    main()


# import streamlit as st
# import streamlit.components.v1 as components

# # HTML and JS for the Leaflet map
# leaflet_map_html = """
# <!DOCTYPE html>
# <html>
# <head>
#     <title>Leaflet Draw Example</title>
#     <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
#     <link rel="stylesheet" href="https://unpkg.com/leaflet-draw/dist/leaflet.draw.css"/>
#     <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
#     <script src="https://unpkg.com/leaflet-draw/dist/leaflet.draw.js"></script>
#     <style>
#         #map { height: 400px; }
#     </style>
# </head>
# <body>
#     <div id="map"></div>
#     <script>
#         var map = L.map('map').setView([51.505, -0.09], 13);
#         L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
#             maxZoom: 19,
#             attribution: '© OpenStreetMap'
#         }).addTo(map);

#         // FeatureGroup is where we will store editable layers
#         var drawnItems = new L.FeatureGroup();
#         map.addLayer(drawnItems);

#         var drawControl = new L.Control.Draw({
#             edit: {
#                 featureGroup: drawnItems
#             },
#             draw: {
#                 polygon: true,
#                 polyline: false,
#                 rectangle: false,
#                 circle: false,
#                 circlemarker: false,
#             }
#         });
#         map.addControl(drawControl);

#         map.on(L.Draw.Event.CREATED, function (event) {
#             var layer = event.layer;
#             drawnItems.addLayer(layer);

#             // Convert the drawn layer to GeoJSON
#             var drawnGeoJSON = layer.toGeoJSON();
#             console.log(drawnGeoJSON);

#             // Ideally, here you would send the GeoJSON data back to your Streamlit app's server
#             // This requires a custom Streamlit component
#         });
#     </script>
# </body>
# </html>
# """

# def main():
#     st.title("Streamlit Leaflet Map Integration")

#     # Use the `components.html` function to render the custom HTML/JS for the Leaflet map
#     components.html(leaflet_map_html, height=450)

# if __name__ == "__main__":
#     main()
