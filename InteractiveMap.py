import streamlit as st
from bokeh.plotting import figure
from bokeh.tile_providers import get_provider, CARTODBPOSITRON_RETINA

def main():
    st.title("Testing Bokeh Map in Streamlit")

    # Map setup
    tile_provider = get_provider(CARTODBPOSITRON_RETINA)
    p = figure(title="Simple Map Test", x_axis_type="mercator", y_axis_type="mercator",
               x_range=(-10000000, 10000000), y_range=(-10000000, 10000000),
               sizing_mode="scale_width", height=400)
    p.add_tile(tile_provider)

    # Display Bokeh plot in Streamlit
    st.bokeh_chart(p, use_container_width=True)

if __name__ == "__main__":
    main()
