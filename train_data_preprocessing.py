# %%
import pandas as pd
from glob import glob
import seaborn as sns

# %%
glob("data/*.csv")

# %%
df = pd.concat(
    [pd.read_csv(f) for f in glob("data/*.csv")], axis=0, ignore_index=True
).assign(
    **{
        "start_time": lambda x: pd.to_datetime(x["start_time"]),
        "end_time": lambda x: pd.to_datetime(x["end_time"]),
        "date": lambda x: pd.to_datetime(x["start_time"]).dt.date,
    }
)
# %%
prepped_df = df.groupby("date").agg({"duration_minutes": "sum"})
# %%
_ = sns.lineplot(data=prepped_df, x="date", y="duration_minutes")
# %%
