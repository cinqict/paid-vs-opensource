import streamlit as st
import pandas as pd
import requests
from ast import literal_eval
import re
from typing import Union, Optional, Callable, Dict
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from skforecast.ForecasterAutoreg import ForecasterAutoreg
from skforecast.model_selection import grid_search_forecaster

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


def run_forecast(data, outcome, feature_list, random_state=42, steps=100):
    """
    Run a forecast using the given data, outcome and feature list. The
    forecast is run using a Random Forest Regressor as the underlying
    regressor.

    Parameters
    ----------
    data: pd.DataFrame
        Data frame containing the data to be used for the forecast.
    outcome: str
        Name of the column containing the outcome variable.
    feature_list: list
        List of features to be used for the forecast.
    random_state: int
        Random state to be used for the forecast.
    steps: int
        Number of steps to be forecasted.

    Returns
    -------
    results_grid_df: pd.DataFrame
        Data frame containing the results of the forecast.

    Examples
    --------
    >>> import pandas as pd
    >>> from utils import run_forecast
    >>> df = pd.read_csv("data/processed/df.csv", index_col=0)
    >>> results_grid_df = run_forecast(df, "demand", ["temperature_2m", "rain"])

    """
    df_train = data.iloc[:-steps]
    df_test = data.iloc[-steps:]

    forecaster = ForecasterAutoreg(
        regressor=RandomForestRegressor(random_state=random_state),
        lags=12,  # This value will be replaced in the grid search
    )

    # Lags used as predictors
    lags_grid = [10, 20]

    # Regressor's hyperparameters
    param_grid = {"n_estimators": [50, 80, 100], "max_depth": [13, 15, 20]}

    try:
        results_grid_df = pd.read_csv("params.csv")
    except FileNotFoundError:
        print("'top_params.csv' file not found")
        results_grid_df = grid_search_forecaster(
            forecaster=forecaster,
            y=df_train[outcome],
            exog=df_train[feature_list],
            param_grid=param_grid,
            lags_grid=lags_grid,
            steps=steps,
            refit=True,
            metric="mean_squared_error",
            initial_train_size=int(data.shape[0] * 0.5),
            fixed_train_size=False,
            return_best=True,
            verbose=False,
        )
        results_grid_df.to_csv("params.csv", index=False)

    top_params_df = results_grid_df.head(1)

    try:
        forecaster = ForecasterAutoreg(
            regressor=RandomForestRegressor(
                **top_params_df["params"].iloc[0], random_state=random_state
            ),
            lags=int(
                top_params_df["lags"].iloc[0][-1]
            ),
        )
    except TypeError:
        lag_list = [int(x) for x in re.sub("\D", " ", top_params_df["lags"].iloc[0]).split()]
        forecaster = ForecasterAutoreg(
            regressor=RandomForestRegressor(
                **literal_eval(top_params_df["params"].iloc[0]), random_state=random_state
            ),
            lags=lag_list[-1],
        )

    forecaster.fit(y=df_train[outcome])
    y_forecast = forecaster.predict(steps=steps)
    y_forecast.index = df_test.index

    forecaster.fit(y=df_train[outcome], exog=df_train[feature_list])
    y_forecast_w_pred = forecaster.predict(steps=steps, exog=df_test[feature_list])
    y_forecast_w_pred.index = df_test.index

    return pd.concat(
        [
            df_train[outcome].reset_index().assign(**{"type": "train"}),
            df_test[outcome].reset_index().assign(**{"type": "test"}),
            y_forecast.reset_index()
            .rename(columns={"pred": outcome})
            .assign(**{"type": "forecast"}),
            y_forecast_w_pred.reset_index()
            .rename(columns={"pred": outcome})
            .assign(**{"type": "forecast with predictors"}),
        ]
    )
