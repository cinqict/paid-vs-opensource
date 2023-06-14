# %%
import plotly.express as px
from utils import (
    apply_scaling,
    get_current_and_forecast,
    get_historical_weather,
    segmented_palette,
    run_forecast,
)

# from prophet import Prophet


# %%
for_df = get_current_and_forecast()

# %%
plot_df = for_df.melt(id_vars=["time"])
px.line(
    plot_df,
    x="time",
    y="value",
    color="variable",
    color_discrete_sequence=segmented_palette,
)

# %%
his_df = get_historical_weather()
# %%
plot_df = his_df.melt(id_vars=["time"])
px.line(
    plot_df,
    x="time",
    y="value",
    color="variable",
    color_discrete_sequence=segmented_palette,
)
# %%
px.imshow(
    his_df.set_index("time").pipe(apply_scaling).T,
    aspect="auto",
    color_continuous_scale="RdBu_r",
)
# %%
# mod = Prophet()
# mod.fit(his_df.rename(columns={"time": "ds", "temperature_2m": "y"}))
# %%
future_df = run_forecast(
    data=his_df, outcome="temperature_2m", feature_list=["temperature_2m", "rain"],
    steps=7
)
# %%
px.line(data_frame=future_df, x="index", y="temperature_2m", color="type",
        color_discrete_sequence=segmented_palette)
# %%
his_df
# %%
