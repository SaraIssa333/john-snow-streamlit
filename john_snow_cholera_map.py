#developed by Fouad Zablith

import streamlit as st
import pandas as pd
import pydeck as pdk
from PIL import Image

# load the data from excel in a dataframe
data = pd.read_excel('CholeraPumps_Deaths.xls')
df = pd.DataFrame(data, columns=['count', 'geometry'])

# clean and replace the coordinates data to fit the PyDeck map
df = df.replace({'<Point><coordinates>': ''}, regex=True)
df = df.replace({'</coordinates></Point>': ''}, regex=True)

# create new longitude and latitude columns in dataframe
split = df['geometry'].str.split(',', n=1, expand=True)
df['lon'] = split[0].astype(float)
df['lat'] = split[1].astype(float)

df.drop(columns=['geometry'], inplace=True)

# title
st.title("John Snow's 1854 Cholera Deaths Map in London")
st.subheader(
    "An interactive recreation of Snow's famous map that helped identify the source of the 1854 cholera outbreak in London."
)

# separate deaths and pumps
deaths_df = df[df['count'] != -999]
pumps_df = df[df['count'] == -999]

# slider to filter deaths
death_to_filter = st.slider('Number of Deaths', 0, 15, 2)

# filter death records only
filtered_df = deaths_df[deaths_df['count'] >= death_to_filter]

st.subheader(f"Map of locations with at least {death_to_filter} deaths")

# checkbox to show pumps
show_pumps = st.checkbox('Show pumps', value=True)
pump_radius = 5 if show_pumps else 0

# summary metrics
col1, col2, col3 = st.columns(3)
col1.metric("Death locations shown", len(filtered_df))
col2.metric("Total deaths shown", int(filtered_df["count"].sum()))
col3.metric("Pumps shown", len(pumps_df) if show_pumps else 0)

# map style selector
map_styles = {
    "Light": "mapbox://styles/mapbox/light-v9",
    "Dark": "mapbox://styles/mapbox/dark-v10",
    "Satellite": "mapbox://styles/mapbox/satellite-v9"
}
selected_style = st.selectbox("Choose map style", list(map_styles.keys()))

# map
st.pydeck_chart(pdk.Deck(
    map_style=map_styles[selected_style],
    initial_view_state=pdk.ViewState(
        latitude=51.5134,
        longitude=-0.1365,
        zoom=15.5,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=filtered_df,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius='count',
            pickable=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=pumps_df,
            get_position='[lon, lat]',
            get_color='[0, 0, 255, 160]',
            get_radius=pump_radius,
            pickable=True,
        ),
    ],
    tooltip={
        "text": "Deaths: {count}"
    }
))

st.markdown(
    "The red dots show the locations of deaths, with dot size reflecting the number of deaths. The blue dots show the locations of water pumps."
)

with st.expander("About this map"):
    st.write(
        """
        John Snow's 1854 cholera map is one of the most famous examples of data visualization
        in public health history. By mapping deaths and comparing them to water pump locations,
        Snow helped identify the Broad Street pump as the center of the outbreak.
        """
    )

image = Image.open('Snow-cholera-map-1.jpg')

st.subheader('Original map of John Snow')
st.image(
    image,
    caption='Original map by John Snow showing the clusters of cholera cases in the London epidemic of 1854, drawn and lithographed by Charles Cheffins',
    use_container_width=True
)

st.markdown("Source and more details on John Snow's work: [Wikipedia - John Snow](https://en.wikipedia.org/wiki/John_Snow)")
st.markdown("Developed by [Fouad Zablith](http://fouad.zablith.org).")