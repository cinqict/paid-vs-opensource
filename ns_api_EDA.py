# %%
import requests
import os
from dotenv import load_dotenv, find_dotenv
import pandas as pd
from datetime import date

# %%
_ = load_dotenv(find_dotenv())


# %%
hdr = {
    # Request headers
    "Cache-Control": "no-cache",
    "Ocp-Apim-Subscription-Key": os.environ.get("NS_APP_PRIMARY"),
}
url = "https://gateway.apiportal.ns.nl/reisinformatie-api/api/v3/disruptions?isActive=false"
response = requests.get(url, headers=hdr)
# %%
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
# %%
amount_disruptions_NS = (
    df.loc[lambda x: x["start"].dt.date == date.today(), :]
    .loc[lambda x: x["end"].dt.date == date.today(), "duration_minutes"]
    .sum()
)


# %%
def get_amount_disruptions_NS():
    hdr = {
        # Request headers
        "Cache-Control": "no-cache",
        "Ocp-Apim-Subscription-Key": os.environ.get("NS_APP_PRIMARY"),
    }
    url = "https://gateway.apiportal.ns.nl/reisinformatie-api/api/v3/disruptions?isActive=false"
    response = requests.get(url, headers=hdr)

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

