import streamlit as st
import geopandas as gpd
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, PolyDrawTool
from bokeh.tile_providers import get_provider, CARTODBPOSITRON_RETINA
from shapely.geometry import Polygon

def main():
    st.title("Drawing and Exporting Polygons on Map with Bokeh in Streamlit")

    # Define initial empty ColumnDataSource for polygon vertices
    source = ColumnDataSource(data={'xs': [], 'ys': []})

    # Map setup
    tile_provider = get_provider(CARTODBPOSITRON_RETINA)
    p = figure(title="Draw on the map", x_axis_type="mercator", y_axis_type="mercator",
               x_range=(-10000000, 10000000), y_range=(-10000000, 10000000),
               sizing_mode="scale_width", height=400)
    p.add_tile(tile_provider)

    # Drawing tool setup
    renderer = p.patches('xs', 'ys', source=source, fill_alpha=0.6, line_color='black')
    draw_tool = PolyDrawTool(renderers=[renderer])
    p.add_tools(draw_tool)
    p.toolbar.active_toggle = draw_tool

    # Display Bokeh plot in Streamlit
    st.bokeh_chart(p, use_container_width=True)

    if st.button('Export and Show Drawn Polygon'):
        # Converting the drawn coordinates to a GeoDataFrame
        df = pd.DataFrame(source.data)
        if not df.empty:
            geometry = [Polygon(zip(xs, ys)) for xs, ys in zip(df['xs'], df['ys'])]
            gdf = gpd.GeoDataFrame(geometry=geometry)
            gdf.set_crs(epsg=4326, inplace=True)  # Set CRS to WGS84

            # Display GeoDataFrame below the map
            st.write(gdf)

            # Export GeoDataFrame to GeoJSON
            geojson = gdf.to_json()
            st.download_button(label="Download GeoJSON", data=geojson, file_name="drawn_polygon.geojson", mime="application/json")

if __name__ == "__main__":
    main()
