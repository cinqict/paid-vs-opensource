# %%
import os
from sqlalchemy import create_engine
import pandas as pd
import seaborn as sns
from dotenv import load_dotenv, find_dotenv
from sklearn.model_selection import RepeatedStratifiedKFold, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_validate
import xgboost as xgb
from utils import get_historical_weather


# %%
_ = load_dotenv(find_dotenv())

# %%
# mysql+pymysql://<user>:<password>@<host>[:<port>]/<dbname>
train_engine = create_engine(os.environ.get("MYSQL_CONNECT_URL") + "train_data")

# %%
train_df = (
    pd.read_sql_query("SELECT * FROM raw_data;", train_engine)
    .assign(
        **{
            "start_time": lambda x: pd.to_datetime(x["start_time"]),
            "end_time": lambda x: pd.to_datetime(x["end_time"]),
            "date": lambda x: pd.to_datetime(x["start_time"]).dt.date,
        }
    )
    .groupby("date")
    .agg({"duration_minutes": "sum"})
)
# %%
weather_df = (
    get_historical_weather(
        lat=52.520008,
        lon=13.404954,
        start_date=str(train_df.index.min()),
        end_date=str(train_df.index.max()),
    )
    .assign(**{"date": lambda x: pd.to_datetime(x["time"]).dt.date})
    .groupby("date")
    .agg({"temperature_2m": ["mean", "min", "max"], "rain": "sum"})
)
weather_df.columns = ["_".join(col) for col in weather_df.columns]
# %%
# cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=1)
# %%
df = pd.merge(train_df, weather_df, on="date", how="left")
# %%
X = df.drop(columns=["duration_minutes"])
y = df["duration_minutes"]

# %%
# n_features_to_select = 2
max_depth = [1, 2, 5, 10, 50, 100]
n_estimators = [1, 2, 5, 10, 50, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300]

# Instanciate Random Forest
# rf = RandomForestRegressor(
#     random_state=42, oob_score=False
# )  # use oob_score with many trees

rf = xgb.XGBRegressor(
    random_state=42,
)

# Define params_dt
# params_rf = {
#     "max_depth": max_depth,
#     "n_estimators": n_estimators,
#     "max_features": ["log2", "sqrt"],
#     "criterion": ["poisson", "squared_error", "friedman_mse", "absolute_error"],
# }

params_rf = {
    "max_depth": [1, 2, 5, 10, 50, 100],
    "n_estimators": [
        1,
        2,
        5,
        10,
        50,
        100,
        120,
        140,
        160,
        180,
        200,
        220,
        240,
        260,
        280,
        300,
    ],
    "eta": [0.1],
    "colsample_bytree": [1.0],
    "colsample_bylevel": [0.3],
    "subsample": [0.9],
    "gamma": [0],
    "lambda": [1],
    "alpha": [0],
    "min_child_weight": [1],
}

# Instantiate grid_dt
grid_dt = GridSearchCV(
    estimator=rf,
    param_grid=params_rf,
    scoring="neg_mean_squared_error",
    cv=10,
    n_jobs=-2,
)

# %%
_ = grid_dt.fit(X, y)
# %%
# Extract the best estimator
optimized_rf = grid_dt.best_estimator_

# %%
optimized_rf.save_model("model_api/xgb.model")
# %%
new_model = xgb.Booster()
new_model.load_model("model_api/xgb.model")
# %%
y_pred = new_model.predict(xgb.DMatrix(X))
# %%
pred_test_df = pd.DataFrame({"y_pred": y_pred, "y_true": y}).set_index(y.index)
# %%
_ = sns.lineplot(
    data=pred_test_df.reset_index().melt(id_vars="date"),
    x="date",
    y="value",
    hue="variable",
)
# %%
_ = (
    pred_test_df.diff(axis=1)
    .rename(columns={"y_true": "pred_true_diff"})
    .loc[lambda x: x["pred_true_diff"].abs() < 500, :]
    .dropna(axis=1)
    .plot()
)
# %%
X.columns
# %%
weather_df.iloc[0, :].to_dict()
# %%
