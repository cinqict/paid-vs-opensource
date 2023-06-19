import streamlit as st
import pandas as pd
import plotly.express as px
from utils import (
    get_current_and_forecast,
    get_historical_weather,
    check_password,
    segmented_palette,
    get_disruption_prediction,
    get_amount_disruptions_NS,
)


# config
st.set_page_config(
    page_title="Predicting Disruptions Due to Weather",
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


@st.cache_data(ttl=60)
def cache_current_disruptions():
    return get_amount_disruptions_NS()


# if check_password():
st.sidebar.title("Settings")
latitude = st.sidebar.number_input(
    "latitude",
    min_value=-90.0,
    max_value=90.0,
    value=52.3116485,
    step=0.2,
    format="%.6f",
)

longitude = st.sidebar.number_input(
    "longitude",
    min_value=-180.0,
    max_value=180.0,
    value=4.9451244,
    step=0.2,
    format="%.6f",
)

# feature_list = st.sidebar.multiselect(
#     label="Select features",
#     options=[
#         "temperature_2m",
#         "relativehumidity_2m",
#         "windspeed_10m",
#         "rain",
#     ],
#     default=["temperature_2m", "rain"],
# )

feature_list = ["temperature_2m", "rain"]

df_current = cache_current(
    latitude=latitude, longitude=longitude, feature_list=feature_list
)

prepped_df = (
    df_current.assign(**{"date": lambda x: pd.to_datetime(x["time"]).dt.date})
    .groupby("date")
    .agg({"temperature_2m": ["mean", "min", "max"], "rain": "sum"})
)
prepped_df.columns = ["_".join(col) for col in prepped_df.columns]
full_pred_df = (
    pd.concat(
        [
            get_disruption_prediction(prepped_df.iloc[i, :])
            for i in range(prepped_df.shape[0])
        ]
    )
    .reset_index(drop=True)
    .assign(**{"date": prepped_df.index})
)

features_prediction_df = pd.merge(prepped_df.reset_index(), full_pred_df, on="date")

st.title("Disruption Prediction Due to Weather")

st.write(
    """This app shows the weather forecast for the next 7 days a location of your choice,
    and based on the current weather and the forecast, predicts the amount of minutes
    of disruptions predicted."""
)
disruption_prediction = (
    get_disruption_prediction(prepped_df.iloc[0, :]).astype(float).round(2).iloc[0, 0]
)
st.markdown(
    f"#### Train disruption prediction in minutes for the Netherlands for today: :green[{disruption_prediction}]"
)
st.markdown(
    f"#### Train disruption prediction in minutes for the Netherlands for today according to NS: :blue[{cache_current_disruptions()}]"
)
st.write("Based on the following weather features:")
st.write(prepped_df.iloc[[0], :])

# current weather
st.header("Current weather and 7 day forecast")
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

plot_df = prepped_df.reset_index().melt(id_vars="date")

current_box_chart = px.box(
    plot_df,
    x="date",
    y="value",
    color="variable",
)

# prediction_line_chart = px.line(
#     data_frame=full_pred_df,
#     x="date",
#     y="prediction",
# )

st.header("Weather Features used for prediction")
st.plotly_chart(current_box_chart, use_container_width=True)
# st.plotly_chart(prediction_line_chart, use_container_width=True)
