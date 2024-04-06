import streamlit as st
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, PolyDrawTool
from bokeh.tile_providers import get_provider, CARTODBPOSITRON
import geopandas as gpd
from shapely.geometry import Polygon

def main():
    st.title("Drawing Polygons on Map with Bokeh in Streamlit")

    # Define initial empty ColumnDataSource with 'xs' and 'ys' columns for polygon vertices
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

    # Button to update the GeoDataFrame and display below the map
    if st.button('Update and Show Geometry'):
        # Converting the drawn coordinates to GeoDataFrame
        df = source.to_df()
        if not df.empty:
            # Converting to GeoDataFrame for display
            geometry = [Polygon(zip(xs, ys)) for xs, ys in zip(df['xs'], df['ys'])]
            gdf = gpd.GeoDataFrame(geometry=geometry)
            gdf.set_crs(epsg=3857, inplace=True)  # Set CRS to Web Mercator

            # Display GeoDataFrame below the map
            st.write(gdf)

            # Export functionality
            gdf.to_file("drawn_polygon.geojson", driver="GeoJSON")
            with open("drawn_polygon.geojson", "r") as file:
                geojson_data = file.read()
                st.download_button(label="Download GeoJSON", data=geojson_data, file_name="drawn_polygon.geojson", mime="application/json")
if __name__ == "__main__":
    main()

