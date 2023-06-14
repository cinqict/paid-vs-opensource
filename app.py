import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils import (
    get_current_and_forecast,
    get_historical_weather,
    check_password,
    segmented_palette,
)


# config
st.set_page_config(
    page_title="Weather App",
    page_icon=":sunny:",
    layout="wide",
    initial_sidebar_state="expanded",
)


# cache functions
@st.cache_data()
def cache_current(latitude=None, longitude=None, feature_list=None):
    if any([latitude, longitude, feature_list]) is None:
        return get_current_and_forecast()
    else:
        return get_current_and_forecast(
            lat=latitude, lon=longitude, feature_list=feature_list
        )


@st.cache_data()
def cache_historical(
    latitude=None, longitude=None, start_date=None, end_date=None, feature_list=None
):
    if any([latitude, longitude, start_date, end_date, feature_list]) is None:
        return get_historical_weather()
    else:
        return get_historical_weather(
            lat=latitude,
            lon=longitude,
            start_date=start_date,
            end_date=end_date,
            feature_list=feature_list,
        )


st.title("Weather Forecast App")

st.write(
    "This app shows the weather forecast for the next 7 days and historical weather data for a location of your choice."
)

# if check_password():
st.sidebar.title("Settings")
latitude = st.sidebar.number_input(
    "latitude",
    min_value=-90.0,
    max_value=90.0,
    value=52.520008,
    step=0.2,
    format="%.6f",
)

longitude = st.sidebar.number_input(
    "longitude",
    min_value=-180.0,
    max_value=180.0,
    value=13.404954,
    step=0.2,
    format="%.6f",
)

feature_list = st.sidebar.multiselect(
    label="Select features",
    options=[
        "temperature_2m",
        "relativehumidity_2m",
        "windspeed_10m",
        "rain",
    ],
    default=["temperature_2m", "rain"],
)

date_range = st.sidebar.date_input(
    label="Select date range",
    value=[pd.to_datetime("2022-01-01"), pd.to_datetime("2022-12-30")],
    min_value=pd.to_datetime("2022-01-01"),
    max_value=datetime.now().date(),
)

# current weather
st.header("Current weather and 7 day forecast")
df_current = cache_current(
    latitude=latitude, longitude=longitude, feature_list=feature_list
)
plot_df = df_current.melt(id_vars="time")
current_line_chart = px.line(
    plot_df,
    x="time",
    y="value",
    color="variable",
    title="Current weather",
    labels={"time": "Time", "value": "Value", "variable": "Feature"},
    color_discrete_sequence=segmented_palette,
)
st.plotly_chart(current_line_chart, use_container_width=True)

# historical weather
st.header("Historical weather")

if len(date_range) < 2:
    st.error("Please select a date range")
    st.stop()

if date_range[0] > date_range[1]:
    st.error("Start date must be before end date")
    st.stop()

df_historical = cache_historical(
    latitude=latitude,
    longitude=longitude,
    start_date=date_range[0].strftime("%Y-%m-%d"),
    end_date=date_range[1].strftime("%Y-%m-%d"),
    feature_list=feature_list,
)
plot_df = df_historical.melt(id_vars="time")
historical_line_chart = px.line(
    plot_df,
    x="time",
    y="value",
    color="variable",
    title="Historical weather",
    labels={"time": "Time", "value": "Value", "variable": "Feature"},
    color_discrete_sequence=segmented_palette,
)
st.plotly_chart(historical_line_chart, use_container_width=True)
