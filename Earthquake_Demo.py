import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import TimestampedGeoJson
import requests
import matplotlib.pyplot as plt
import imageio
from io import BytesIO
from PIL import Image
import os

# Custom CSS for stat boxes
st.markdown(
    """
    <style>
    .stat-box {
        background-color: #ff4b4b;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        text-align: center;
        color: white;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to fetch earthquake data from USGS with caching
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
        'Depth': [feature['properties'].get('depth', 'N/A') for feature in data]
    }
    df = pd.DataFrame(earthquake_data)
    return df

# Function to create a Folium map with stylized animated markers
def create_folium_map(df, time_index=None):
    m = folium.Map(location=[0,0], zoom_start=1, scrollWheelZoom=False)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Tiles © Esri',
        name='Esri Imagery',
        overlay=False,
        control=True
    ).add_to(m)

    features = []
    for i, row in df.iterrows():
        if time_index is not None and i > time_index:
            continue
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

    TimestampedGeoJson({
        'type': 'FeatureCollection',
        'features': features
    }, period='PT1H', add_last_point=True, auto_play=True, loop=True, max_speed=2).add_to(m)

    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
        attr='Labels © Esri',
        name='Esri World Imagery Labels',
        overlay=True,
        control=True
    ).add_to(m)

    folium.LayerControl().add_to(m)
    
    return m

# Function to create frames for the GIF
def create_gif_frames(df, num_frames, output_folder):
    for i in range(num_frames):
        m = create_folium_map(df, time_index=i)
        img_data = BytesIO()
        m.save(img_data, close_file=False)
        img_data.seek(0)
        img = Image.open(img_data)
        img.save(f"{output_folder}/frame_{i}.png")

# Function to create a GIF from saved frames
def create_gif_from_frames(frame_folder, output_file, fps=2):
    frame_files = [f"{frame_folder}/frame_{i}.png" for i in range(len(os.listdir(frame_folder)))]
    images = [imageio.imread(frame) for frame in frame_files]
    imageio.mimsave(output_file, images, fps=fps)

# Main Streamlit app
def main():
    st.title("Recent Earthquakes")
    
    st.write("""
        This map shows earthquakes around the world over the last 24 hours with an animation showing their occurrence over time.
        Data is sourced from the US Geological Survey (USGS). You can access the data [here](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php).
        The map is updated every 10 minutes.
    """)

    # Fetch and transform data
    data = fetch_earthquake_data()
    if data:
        df = transform_data(data)

        # Display additional stats using columns for better layout
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="stat-box">Total earthquakes: {}</div>'.format(len(df)), unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="stat-box">Strongest magnitude: {}</div>'.format(df['Magnitude'].max()), unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="stat-box">Weakest magnitude: {}</div>'.format(df['Magnitude'].min()), unsafe_allow_html=True)

        # Placeholder for the map
        map_placeholder = st.empty()
    
        # Create and display the Folium map
        folium_map = create_folium_map(df)
        with map_placeholder:
            folium_static(folium_map)
    
        # Display a chart of earthquake magnitudes
        st.subheader("Earthquake Magnitudes")
        fig, ax = plt.subplots()
        df['Magnitude'].hist(bins=20, ax=ax)
        ax.set_title("Distribution of Earthquake Magnitudes")
        ax.set_xlabel("Magnitude")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)

        # Add an option to create a GIF
        num_frames = st.number_input('Number of Frames for GIF', min_value=1, max_value=100, value=10)
        gif_output_folder = '/tmp/gif_frames'
        gif_output_file = '/tmp/earthquake_map.gif'
        
        if st.button('Create GIF'):
            os.makedirs(gif_output_folder, exist_ok=True)
            create_gif_frames(df, num_frames, gif_output_folder)
            create_gif_from_frames(gif_output_folder, gif_output_file)
            st.image(gif_output_file, caption='Generated Earthquake Map GIF')
            
            # Clean up frames after creating the GIF
            for file in os.listdir(gif_output_folder):
                os.remove(os.path.join(gif_output_folder, file))
            os.rmdir(gif_output_folder)

        # Refresh button to manually update data
        if st.button('Refresh Data'):
            data = fetch_earthquake_data()
            if data:
                df = transform_data(data)
                folium_map = create_folium_map(df)
                with map_placeholder:
                    folium_static(folium_map)

if __name__ == "__main__":
    main()





# import streamlit as st
# import pandas as pd
# import folium
# from streamlit_folium import folium_static
# from folium.plugins import TimestampedGeoJson
# import requests
# import matplotlib.pyplot as plt

# # Custom CSS for stat boxes
# st.markdown(
#     """
#     <style>
#     .stat-box {
#         background-color: #ff4b4b;
#         padding: 10px;
#         border-radius: 5px;
#         margin: 10px 0;
#         text-align: center;
#         color: white;
#         font-weight: bold;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# # Function to fetch earthquake data from USGS with caching
# @st.cache_data(ttl=600)  # Cache the data for 10 minutes
# def fetch_earthquake_data():
#     api_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
#     try:
#         response = requests.get(api_url)
#         response.raise_for_status()
#         data = response.json()
#         return data['features']
#     except requests.exceptions.RequestException as e:
#         st.error(f"Error fetching earthquake data: {e}")
#         return None

# # Function to transform data for plotting
# def transform_data(data):
#     earthquake_data = {
#         'Latitude': [feature['geometry']['coordinates'][1] for feature in data],
#         'Longitude': [feature['geometry']['coordinates'][0] for feature in data],
#         'Magnitude': [feature['properties']['mag'] for feature in data],
#         'Place': [feature['properties']['place'] for feature in data],
#         'Time': [pd.to_datetime(feature['properties']['time'], unit='ms') for feature in data],
#         'Depth': [feature['properties'].get('depth', 'N/A') for feature in data]
#     }
#     df = pd.DataFrame(earthquake_data)
#     return df

# # Function to create a Folium map with stylized animated markers
# def create_folium_map(df):
#     m = folium.Map(location=[0,0], zoom_start=1, scrollWheelZoom=False)
#     # Add a tile layer for ESRI Imagery
#     folium.TileLayer(
#         tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
#         attr='Tiles © Esri',
#         name='Esri Imagery',
#         overlay=False,
#         control=True
#     ).add_to(m)
#     # Create a list of features for TimestampedGeoJson with enhanced styling
#     features = []
#     for i, row in df.iterrows():
#         magnitude = row['Magnitude']
#         color = 'red' if magnitude >= 5 else 'orange' if magnitude >= 3 else 'yellow'
#         feature = {
#             'type': 'Feature',
#             'geometry': {
#                 'type': 'Point',
#                 'coordinates': [row['Longitude'], row['Latitude']]
#             },
#             'properties': {
#                 'time': row['Time'].isoformat(),
#                 'popup': f"Place: {row['Place']}<br>Magnitude: {row['Magnitude']}<br>Time: {row['Time']}<br>Depth: {row['Depth']} km",
#                 'icon': 'circle',
#                 'iconstyle': {
#                     'fillColor': color,
#                     'fillOpacity': 0.7,
#                     'stroke': 'true',
#                     'color': 'black',
#                     'weight': 1,
#                     'radius': row['Magnitude'] * 2
#                 }
#             }
#         }
#         features.append(feature)
    
#     # Create TimestampedGeoJson with enhanced styling
#     TimestampedGeoJson({
#         'type': 'FeatureCollection',
#         'features': features
#     }, period='PT1H', add_last_point=True, auto_play=True, loop=True, max_speed=2).add_to(m)
    
#     # Add a tile layer for ESRI World Imagery Labels
#     folium.TileLayer(
#         tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
#         attr='Labels © Esri',
#         name='Esri World Imagery Labels',
#         overlay=True,
#         control=True
#     ).add_to(m)
    
#     folium.LayerControl().add_to(m)
    
#     return m

# # Main Streamlit app
# def main():
#     st.title("Recent Earthquakes")
    
#     st.write("""
#         This map shows earthquakes around the world over the last 24 hours with an animation showing their occurrence over time.
#         Data is sourced from the US Geological Survey (USGS). You can access the data [here](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php).
#         The map is updated every 10 minutes.
#     """)

#     # Fetch and transform data
#     data = fetch_earthquake_data()
#     if data:
#         df = transform_data(data)

#         # Display additional stats using columns for better layout
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.markdown('<div class="stat-box">Total earthquakes: {}</div>'.format(len(df)), unsafe_allow_html=True)
#         with col2:
#             st.markdown('<div class="stat-box">Strongest magnitude: {}</div>'.format(df['Magnitude'].max()), unsafe_allow_html=True)
#         with col3:
#             st.markdown('<div class="stat-box">Weakest magnitude: {}</div>'.format(df['Magnitude'].min()), unsafe_allow_html=True)

#         # Placeholder for the map
#         map_placeholder = st.empty()
    
#         # Create and display the Folium map
#         folium_map = create_folium_map(df)
#         with map_placeholder:
#             folium_static(folium_map)
    
#         # Display a chart of earthquake magnitudes
#         st.subheader("Earthquake Magnitudes")
#         fig, ax = plt.subplots()
#         df['Magnitude'].hist(bins=20, ax=ax)
#         ax.set_title("Distribution of Earthquake Magnitudes")
#         ax.set_xlabel("Magnitude")
#         ax.set_ylabel("Frequency")
#         st.pyplot(fig)

#         # Refresh button to manually update data
#         if st.button('Refresh Data'):
#             data = fetch_earthquake_data()
#             if data:
#                 df = transform_data(data)
#                 folium_map = create_folium_map(df)
#                 with map_placeholder:
#                     folium_static(folium_map)

# if __name__ == "__main__":
#     main()
