# Test Script
import streamlit as st
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, FreehandDrawTool, GMapOptions
from bokeh.tile_providers import get_provider, CARTODBPOSITRON
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString
import pyproj

# Function to convert lat/lon to Web Mercator format
def wgs84_to_web_mercator(df, lon="lon", lat="lat"):
    k = 6378137
    df["x"] = df[lon] * (k * np.pi/180.0)
    df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
    return df

def main():
    st.title("Drawing on Map with Bokeh in Streamlit")

    # Map setup
    map_options = GMapOptions(lat=51.5, lng=-0.09, map_type="roadmap", zoom=10)
    p = figure(title="Draw on the map", x_range=(-2000000, 6000000), y_range=(-1000000, 7000000),
               x_axis_type="mercator", y_axis_type="mercator")
    p.add_tile(get_provider(CARTODBPOSITRON))

    # Drawing tool setup
    source = ColumnDataSource({'x': [], 'y': []})
    renderer = p.multi_line('x', 'y', source=source, line_width=2, alpha=0.8, color='red')
    draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=3)
    p.add_tools(draw_tool)
    p.toolbar.active_drag = draw_tool

    # Display Bokeh plot in Streamlit
    st.bokeh_chart(p)

    # Export button
    if st.button('Export Drawn Geometry'):
        # Converting the drawn coordinates to GeoJSON
        df = pd.DataFrame(source.data)
        if not df.empty:
            df = wgs84_to_web_mercator(df, lon="x", lat="y")
            geometry = [LineString(zip(df['x'], df['y']))]
            gdf = gpd.GeoDataFrame(geometry=geometry)
            gdf.set_crs(epsg=3857, inplace=True)  # Set CRS to Web Mercator
            gdf.to_file("drawn_geometry.geojson", driver="GeoJSON")

            with open("drawn_geometry.geojson", "r") as file:
                geojson_data = file.read()
                st.download_button(label="Download GeoJSON", data=geojson_data, file_name="drawn_geometry.geojson", mime="application/json")

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
