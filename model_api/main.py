from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import ExpectedInputPrepped

import pandas as pd
import xgboost as xgb

model = xgb.Booster()
model.load_model("xgb.model")


def prepped_data_predict(input_dict):
    df = pd.DataFrame(
        input_dict,
        index=[0],
    )
    prediction = model.predict(xgb.DMatrix(df))
    return str(prediction[0])


app = FastAPI()

origins = [
    "http://192.168.1.72:3000/",
    "http://localhost:3000/",
    "http://localhost:8501"
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
def read_root():
    return {"Welcome": "This is the API for the xgboost model"}


@app.post("/predict_prepped_data", tags=["Predict One Instance"])
def predict_prepped(body: ExpectedInputPrepped):
    return {"prediction": prepped_data_predict(body.dict())}
