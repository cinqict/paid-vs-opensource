# %%
import os
import requests
import pandas as pd
import json
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())


# %%
def create_tf_serving_json(data):
    return {
        "inputs": {name: data[name].tolist() for name in data.keys()}
        if isinstance(data, dict)
        else data.tolist()
    }


def score_model(dataset):
    # url = "https://adb-3715028202055514.14.azuredatabricks.net/serving-endpoints/disruptions_prediction/invocations"
    # url = "https://adb-1846146254154564.4.azuredatabricks.net/serving-endpoints/disruptions_prediction/invocations"
    # url = "https://adb-8041947923484593.13.azuredatabricks.net/serving-endpoints/disruption-prediction/invocations"
    url = 'https://adb-5056669161281979.19.azuredatabricks.net/serving-endpoints/disruption-prediction-model/invocations'
    headers = {
        "Authorization": f'Bearer {os.environ.get("DATABRICKS_TOKEN")}',
        "Content-Type": "application/json",
    }
    ds_dict = (
        {"dataframe_split": dataset.to_dict(orient="split")}
        if isinstance(dataset, pd.DataFrame)
        else create_tf_serving_json(dataset)
    )
    data_json = json.dumps(ds_dict, allow_nan=True)
    response = requests.request(method="POST", headers=headers, url=url, data=data_json)
    if response.status_code != 200:
        raise Exception(
            f"Request failed with status {response.status_code}, {response.text}"
        )
    return pd.DataFrame(response.json())


# %%
X = pd.DataFrame(
    {
        "temperature_2m_mean": [10.0],
        "temperature_2m_min": [8.0],
        "temperature_2m_max": [12.0],
        "rain_sum": [0.0],
    }
)
print(score_model(X))
# %%
