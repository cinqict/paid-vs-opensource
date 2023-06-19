import streamlit as st
import pandas as pd
import requests
from typing import Union, Optional, Callable, Dict
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from datetime import date
import os
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

# create a color palette
segmented_palette = ["#D81B60", "#1E88E5", "#FFC107", "#944EBC", "#004D40"]


def check_password():
    """Returns `True` if the user had the correct password.

    Parameters
    ----------
    None

    Returns
    -------
    bool
        `True` if the user had the correct password, `False` otherwise.

    Examples
    --------
    >>> import streamlit as st
    >>> from utils import check_password
    >>> check_password()

    """

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True


def get_current_and_forecast(
    lat=52.377956,
    lon=4.897070,
    feature_list=[
        "temperature_2m",
        "relativehumidity_2m",
        "windspeed_10m",
        "precipitation_probability",
        "rain",
    ],
):
    """
    Get current and forecast weather data from open-meteo.com

    Parameters
    ----------
    lat: float
        Latitude of the location you want to get the weather for.
    lon: float
        Longitude of the location you want to get the weather for.
    feature_list: list
        List of features you want to get the weather for.
        Options: "temperature_2m", "relativehumidity_2m", "windspeed_10m",
        "precipitation_probability", "rain"

    Returns
    -------
    df: pd.DataFrame
        Data frame containing the weather data.

    Examples
    --------
    >>> import pandas as pd
    >>> from utils import get_current_and_forecast
    >>> df = get_current_and_forecast()
    >>> df.head()

    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly={','.join(feature_list)}"
    response = requests.get(url)
    return pd.DataFrame(response.json()["hourly"])


def get_historical_weather(
    lat=52.377956,
    lon=4.897070,
    start_date="2022-01-01",
    end_date="2022-12-31",
    feature_list=[
        "temperature_2m",
        "relativehumidity_2m",
        "windspeed_10m",
        "rain",
    ],
):
    """
    Get historical weather data from open-meteo.com

    Parameters
    ----------
    lat: float
        Latitude of the location you want to get the weather for.
    lon: float
        Longitude of the location you want to get the weather for.
    start_date: str
        Start date of the period you want to get the weather for.
    end_date: str
        End date of the period you want to get the weather for.
    feature_list: list
        List of features you want to get the weather for.
        Options: "temperature_2m", "relativehumidity_2m",
        "windspeed_10m", "rain"

    Returns
    -------
    df: pd.DataFrame
        Data frame containing the weather data.

    Examples
    --------
    >>> import pandas as pd
    >>> from utils import get_historical_weather
    >>> df = get_historical_weather()
    >>> df.head()

    """
    url = f"https://archive-api.open-meteo.com/v1/era5?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly={','.join(feature_list)}"
    response = requests.get(url)
    return pd.DataFrame(response.json()["hourly"])


def apply_scaling(
    df: pd.DataFrame,
    method: Union[str, Optional[Callable]] = "MinMax",
    kwargs: Dict = {},
):
    r"""Utility function to be used in conjunction with pandas pipe()
    to scale columns of a data frame seperately.

    Parameters
    ----------
    df: pd.DataFrame
        The data frame you want to scale.
    method: Callable, str
        The name of the method you wish to use [method options: "MinMax",
        "Standard"], or an Sklearn transformer,
        see: https://scikit-learn.org/stable/modules/preprocessing.html
    kwargs: Dict
        Dictionary containing additional keywords to be added to the Scaler.

    Returns
    -------
    scal_df: pd.DataFrame
        The scaled data frame.

    Examples
    --------
    >>> import seaborn as sns
    >>> import pandas as pd
    >>> df = sns.load_dataset("iris")
    >>> scaled_df = (df
    ...             .select_dtypes("number")
    ...             .pipe(apply_scaling)
    ...             )

    """

    if method == "MinMax":
        scal_df = pd.DataFrame(
            MinMaxScaler(**kwargs).fit_transform(df),
            index=df.index,
            columns=df.columns,
        )
    elif method == "Standard":
        scal_df = pd.DataFrame(
            StandardScaler(**kwargs).fit_transform(df),
            index=df.index,
            columns=df.columns,
        )
    else:
        scal_df = pd.DataFrame(
            method(**kwargs).fit_transform(df),
            index=df.index,
            columns=df.columns,  # type: ignore
        )
    return scal_df


def get_disruption_prediction(data):
    """
    Get disruption prediction from the model API.

    Parameters
    ----------
    dict_data: pd.Series
        Dictionary containing the data to be used for the prediction.

    Returns
    -------
    pred: float
        The predicted probability of disruption.

    """
    try:
        response = requests.post(
            # "http://127.0.0.1:8000/predict_prepped_data",
            "http://localhost:8000/predict_prepped_data",
            data=data.to_json(),
        )
        print("option 1")
    except:
        try:
            response = requests.post(
                "http://localhost:30252/predict_prepped_data",
                data=data.to_json(),
            )
            print("option 2")
        except:
            try:
                response = requests.post(
                    # "http://10.103.226.248:8000/predict_prepped_data",
                    "http://10.106.228.98:8000/predict_prepped_data",
                    data=data.to_json(),
                )
                print("option 3")
            except:
                print("Could not connect to model API")
    
    return pd.DataFrame(response.json(), index=[0])


def get_amount_disruptions_NS():
    hdr = {
        # Request headers
        "Cache-Control": "no-cache",
        "Ocp-Apim-Subscription-Key": os.environ.get("NS_APP_PRIMARY"),
    }
    url = "https://gateway.apiportal.ns.nl/reisinformatie-api/api/v3/disruptions?isActive=false"
    response = requests.get(url, headers=hdr)
    print(response.status_code)

    df = pd.DataFrame(
        [
            (x["id"], x["title"], x["start"], x["end"], x["timespans"][0]["cause"]["label"])
            for x in response.json()
        ],
        columns=["id", "title", "start", "end", "cause"],
    ).assign(
        **{
            "start": lambda x: pd.to_datetime(x["start"]),
            "end": lambda x: pd.to_datetime(x["end"]),
            "duration_minutes": lambda x: (x["end"] - x["start"]).dt.total_seconds() / 60,
        }
    )

    amount_disruptions_NS = (
        df.loc[lambda x: x["start"].dt.date == date.today(), :]
        .loc[lambda x: x["end"].dt.date == date.today(), "duration_minutes"]
        .sum()
    )
    return round(amount_disruptions_NS, 2)
