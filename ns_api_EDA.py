# %%
import requests
import os
from dotenv import load_dotenv, find_dotenv
import pandas as pd

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
    [(x["id"], x["title"], x["start"], x["end"], x["timespans"][0]["cause"]["label"]) for x in response.json()],
    columns=["id", "title", "start", "end", "cause"],
).assign(**{
    "start": lambda x: pd.to_datetime(x["start"]),
    "end": lambda x: pd.to_datetime(x["end"]),
    "duration_minutes": lambda x: (x["end"] - x["start"]).dt.total_seconds() / 60})
# %%
df.info()
# %%
df
# %%
