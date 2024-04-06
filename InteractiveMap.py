import streamlit as st
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, PolyDrawTool, GMapOptions
from bokeh.tile_providers import get_provider, CARTODBPOSITRON
import geopandas as gpd
from shapely.geometry import Polygon

# Function to convert lat/lon to Web Mercator format
def wgs84_to_web_mercator(df, lon="lon", lat="lat"):
    k = 6378137
    df["x"] = df[lon] * (k * np.pi/180.0)
    df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
    return df

def main():
    st.title("Drawing Polygons on Map with Bokeh in Streamlit")

    # Map setup
    map_options = GMapOptions(lat=51.5, lng=-0.09, map_type="roadmap", zoom=10)
    p = figure(title="Draw on the map", x_range=(-2000000, 6000000), y_range=(-1000000, 7000000),
               x_axis_type="mercator", y_axis_type="mercator")
    p.add_tile(get_provider(CARTODBPOSITRON))

    # Drawing tool setup
    source = ColumnDataSource({'x': [], 'y': []})
    renderer = p.patches('x', 'y', source=source, alpha=0.8, color='red')
    draw_tool = PolyDrawTool(renderers=[renderer], num_objects=3)
    p.add_tools(draw_tool)
    p.toolbar.active_drag = draw_tool

    # Display Bokeh plot in Streamlit
    st.bokeh_chart(p)

    # Export button
    if st.button('Export Drawn Polygon'):
        # Converting the drawn coordinates to GeoJSON
        df = pd.DataFrame(source.data)
        if not df.empty:
            # Assuming each 'x' and 'y' are lists of coordinates for one polygon
            geometry = [Polygon(zip(xs, ys)) for xs, ys in zip(df['x'], df['y'])]
            gdf = gpd.GeoDataFrame(geometry=geometry)
            gdf.set_crs(epsg=3857, inplace=True)  # Set CRS to Web Mercator
            st.dataframe(gdf)
            gdf.to_file("drawn_polygon.geojson", driver="GeoJSON")

            with open("drawn_polygon.geojson", "r") as file:
                geojson_data = file.read()
                st.download_button(label="Download GeoJSON", data=geojson_data, file_name="drawn_polygon.geojson", mime="application/json")

if __name__ == "__main__":
    main()
