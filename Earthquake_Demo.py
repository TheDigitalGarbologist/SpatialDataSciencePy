import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import TimestampedGeoJson
import requests
import matplotlib.pyplot as plt

# Function to fetch earthquake data from USGS with new caching
@st.cache_data(ttl=600)  # Cache the data for 10 minutes
def fetch_earthquake_data():
    api_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return data['features']
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching earthquake data: {e}")
        return None

# Function to transform data for plotting
def transform_data(data):
    earthquake_data = {
        'Latitude': [feature['geometry']['coordinates'][1] for feature in data],
        'Longitude': [feature['geometry']['coordinates'][0] for feature in data],
        'Magnitude': [feature['properties']['mag'] for feature in data],
        'Place': [feature['properties']['place'] for feature in data],
        'Time': [pd.to_datetime(feature['properties']['time'], unit='ms') for feature in data],
        'Depth': [feature['properties'].get('depth', 'N/A') for feature in data]  # Assuming depth is included
    }
    df = pd.DataFrame(earthquake_data)
    return df

# Function to create a Folium map with stylized animated markers
def create_folium_map(df):
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=2)
    
    # Add a tile layer for ESRI Imagery
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Tiles © Esri',
        name='Esri Imagery',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Create a list of features for TimestampedGeoJson with enhanced styling
    features = []
    for i, row in df.iterrows():
        magnitude = row['Magnitude']
        color = 'red' if magnitude >= 5 else 'orange' if magnitude >= 3 else 'yellow'
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row['Longitude'], row['Latitude']]
            },
            'properties': {
                'time': row['Time'].isoformat(),
                'popup': f"Place: {row['Place']}<br>Magnitude: {row['Magnitude']}<br>Time: {row['Time']}<br>Depth: {row['Depth']} km",
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': color,
                    'fillOpacity': 0.7,
                    'stroke': 'true',
                    'color': 'black',
                    'weight': 1,
                    'radius': row['Magnitude'] * 2
                }
            }
        }
        features.append(feature)
    
    # Create TimestampedGeoJson with enhanced styling
    TimestampedGeoJson({
        'type': 'FeatureCollection',
        'features': features
    }, period='PT1H', add_last_point=True, auto_play=True, loop=False).add_to(m)
    
    # Add a tile layer for ESRI World Imagery Labels
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
        attr='Labels © Esri',
        name='Esri World Imagery Labels',
        overlay=True,
        control=True
    ).add_to(m)
    
    folium.LayerControl().add_to(m)
    
    return m

# Function to filter data based on user input
def filter_data(df, min_magnitude, max_magnitude, region):
    filtered_df = df[(df['Magnitude'] >= min_magnitude) & (df['Magnitude'] <= max_magnitude)]
    if region and region != "All":
        filtered_df = filtered_df[filtered_df['Place'].str.contains(region, case=False, na=False)]
    return filtered_df

# Main Streamlit app
def main():
    st.title("Recent Earthquakes")
    
    st.write("""
        This map shows recent earthquakes around the world with an animation showing their occurrence over time.
        Data is sourced from the US Geological Survey (USGS). You can access the data [here](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php).
        The map is updated every 10 minutes.
    """)

    # Fetch and transform data
    data = fetch_earthquake_data()
    if data:
        df = transform_data(data)
    
        # Sidebar filters
        st.sidebar.header("Filters")
        min_magnitude = st.sidebar.slider("Minimum Magnitude", min_value=0.0, max_value=10.0, value=2.5)
        max_magnitude = st.sidebar.slider("Maximum Magnitude", min_value=0.0, max_value=10.0, value=10.0)
        regions = ["All", "California", "Japan", "Indonesia", "Alaska", "Chile", "Mexico", "New Zealand", "Turkey"]
        region = st.sidebar.selectbox("Region", regions)
    
        # Filter data
        filtered_data = filter_data(df, min_magnitude, max_magnitude, region)
    
        # Placeholder for the map
        map_placeholder = st.empty()
    
        # Create and display the Folium map
        folium_map = create_folium_map(filtered_data)
        with map_placeholder:
            folium_static(folium_map)
    
        # Display additional stats
        st.subheader("Earthquake Statistics")
        st.write(f"Total earthquakes in the past day: {len(filtered_data)}")
        st.write(f"Strongest earthquake magnitude: {filtered_data['Magnitude'].max()}")
        st.write(f"Weakest earthquake magnitude: {filtered_data['Magnitude'].min()}")

        # Display a chart of earthquake magnitudes
        st.subheader("Earthquake Magnitudes")
        fig, ax = plt.subplots()
        filtered_data['Magnitude'].hist(bins=20, ax=ax)
        ax.set_title("Distribution of Earthquake Magnitudes")
        ax.set_xlabel("Magnitude")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)

        # Refresh button to manually update data
        if st.button('Refresh Data'):
            data = fetch_earthquake_data()
            if data:
                df = transform_data(data)
                filtered_data = filter_data(df, min_magnitude, max_magnitude, region)
                folium_map = create_folium_map(filtered_data)
                with map_placeholder:
                    folium_static(folium_map)

if __name__ == "__main__":
    main()
