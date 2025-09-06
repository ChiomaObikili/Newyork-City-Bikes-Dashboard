# st_dashboard2.py

# Import libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from PIL import Image

########################### Initial settings ################################
st.set_page_config(page_title='New York City Bikes Strategy Dashboard', layout='wide')
st.title("Newyork City Bikes Strategy Dashboard")

# Sidebar selector
st.sidebar.title("Aspect Selector")
page = st.sidebar.selectbox('Select an aspect of the analysis', [
    "Intro page",
    "Weather component and bike usage",
    "Most popular stations",
    "Interactive map with aggregated bike trips",
    "Recommendations"
])

########################## Import data ######################################
df = pd.read_csv('reduced_data_to_plot_small.csv')  
top20 = pd.read_csv('top20_small.csv')

########################### Pages ############################################

# --- Intro page ---
if page == "Intro page":
    st.markdown("#### This dashboard aims at providing helpful insights on the expansion problems Newyork City Bikes currently faces.")
    st.markdown("""Currently, New York City’s bike-sharing system faces challenges with customers reporting limited bike availability at certain times. This analysis explores the potential reasons behind these shortages. The dashboard is organized into four sections for clarity and ease of exploration:""")
    st.markdown("- Most popular stations")
    st.markdown("- Weather component and bike usage")
    st.markdown("- Interactive map with aggregated bike trips")
    st.markdown("- Recommendations")
    st.markdown("The dropdown menu on the left 'Aspect Selector' will take you to the different aspects of the analysis our team looked at.")

    myImage = Image.open("Newyork pic1.WEBP") #source: https://nyc.hollandbikes.com/de/fahrradverleih-brooklyn/
    st.image(myImage)

# --- Weather component and bike usage ---
elif page == 'Weather component and bike usage':
    df = pd.read_csv('reduced_data_to_plot_small.csv')  
    top20 = pd.read_csv('top20_small.csv')             


    # Making sure 'date' column exists and is datetime
    print("Columns in df:", df.columns.tolist())  # Debugging step

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
    else:
        st.error("No 'date' column found in reduced_data_to_plot.csv")
        st.stop()

    # Aggregating daily bikes ride
    daily_rides = df.groupby('date').size().reset_index(name='bike_rides_daily')

    # Merge with temperature (assuming 'avgTemp' is daily)
    df_daily = pd.merge(daily_rides, df[['date', 'avgTemp']].drop_duplicates(), on='date')

    # Filtering data for 2022
    df_2022 = df_daily[df_daily['date'].dt.year == 2022]

    # taking a random 100k rows 
    df_sample = df_2022.sample(n=min(100000, len(df_2022)), random_state=42).sort_values('date')

    fig_2 = make_subplots(specs=[[{"secondary_y": True}]])

    # Daily bike rides
    fig_2.add_trace(
        go.Scatter(
            x=df_sample['date'],
            y=df_sample['bike_rides_daily'],
            name='Daily bike rides',
            marker={'color': 'blue'},
            mode='lines+markers'
        ),
        secondary_y=False
    )

    # Daily temperature
    fig_2.add_trace(
        go.Scatter(
            x=df_sample['date'],
            y=df_sample['avgTemp'],
            name='Daily temperature',
            marker={'color': 'red'},
            mode='lines+markers'
        ),
        secondary_y=True
    )

    fig_2.update_layout(
        title='Newyork Daily Bike Rides and Temperature in 2022 (Sampled Points)',
        xaxis_title='Date',
        yaxis_title='Bike Rides',
        yaxis2_title='Temperature (°C)',
        legend_title='Metrics',
        template='plotly_white'
    )

    st.plotly_chart(fig_2, use_container_width=True)
    st.markdown("""The chart shows that bike usage goes up when the weather is warmer and drops when it gets colder. On very cold days, fewer people ride bikes, while on milder days, the number of rides increases.This means the shortage problem is most likely a summer issue, from around May to October, when more people want to ride bikes.""")

# --- Most popular stations ---
elif page == 'Most popular stations':
    with st.sidebar:
        season_filter = st.multiselect(label= 'Select the season', options=df['season'].unique(),
            default=df['season'].unique())
    df_filtered = df[df['season'].isin(season_filter)]

    # Define total rides
    total_rides = len(df_filtered)
    st.metric(label='Total Bike Rides', value=f"{total_rides:,}")

    # Bar chart
    df_filtered['value'] = 1 
    df_groupby_bar = df_filtered.groupby('start_station_name', as_index=False).agg({'value': 'sum'})
    top20_stations = df_groupby_bar.nlargest(20, 'value')

    fig = go.Figure(go.Bar(
        x=top20_stations['start_station_name'], 
        y=top20_stations['value'], 
        marker={'color': top20_stations['value'], 'colorscale': 'Blues'}
    ))
    fig.update_layout(
        title='Top 20 most popular bike stations in Newyork City',
        xaxis_title='Start stations',
        yaxis_title ='Sum of trips',
        width=900, height=600
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""From the bar chart, we can see that certain bike stations are much more popular than others. The top three start stations are W 21 St & 6 Ave, 1 Ave & E 6 St, and E 17 St & E 6 St. There’s a noticeable gap between the busiest stations and the less frequently used ones, showing that riders clearly prefer a handful of key locations. This is a finding that we could cross reference with the interactive map that you can access through the side bar select box.""")

# --- Interactive map ---
elif page == 'Interactive map with aggregated bike trips': 
    st.write("Interactive map showing aggregated bike trips over Newyork City")
    # Load the smaller HTML map
    with open("Newyork Bikes Trips Aggregated.html", 'r') as f:
        html_data = f.read()
    st.header("Aggregated Bike Trips in Newyork")
    st.components.v1.html(html_data,height=1000)
    st.markdown("#### Using the filter on the left hand side of the map we can check whether the most popular start stations also appear in the most popular trips.")
    st.markdown("The most popular start stations are:")
    st.markdown("Wythe Ave & Metropolitan Ave, West End Ave, and West St & Liberty St. These locations stand out as key hubs for Citi Bike trips.")
    st.markdown("""Williamsburg and the Financial District are especially busy because people use bikes to commute to work, they are also popular for social and leisure trips. This shows that Citi Bikes are being used not just for daily commuting but also for recreational purposes.""")

# --- Recommendations / Conclusions ---
else:
    st.header("Conclusions and recommendations")
    bikes = Image.open("Newyork pic2.WEBP")
    st.image(bikes)
    st.markdown("### Our analysis has shown that Citi Bikes should focus on the following objectives moving forward:")

    st.markdown("- Expand the number of stations in high-demand areas such as Williamsburg (Wythe Ave & Metropolitan Ave), the Upper West Side (West End Ave), and the Financial District (West St & Liberty St), where both commuting and leisure trips are common.")
    st.markdown("- Ensure that these popular stations are fully stocked with bikes during the warmer months (May to October), when demand peaks, while adjusting supply in colder months to reduce unnecessary operational costs.")
    st.markdown("- Monitor rider patterns more closely using seasonal and station-level data, so bike availability can be better aligned with customer needs in both work-related and recreational areas.")
