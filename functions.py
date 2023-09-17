import pandas as pd
from prophet import Prophet


def build_message(name: str):
    return f"Hello {name}!"

def clean_data(initial_dataset: pd.DataFrame):
    print("Cleaning Data")
    initial_dataset = initial_dataset.rename(columns={"Date": "ds", "Close": "y"})
    initial_dataset['ds'] = pd.to_datetime(initial_dataset['ds']).dt.tz_localize(None)
    cleaned_dataset = initial_dataset.copy()
    return cleaned_dataset

def retrained_model(cleaned_dataset: pd.DataFrame):
    print("Model Retraining")
    model = Prophet()
    model.fit(cleaned_dataset)
    return model

def predict(model):
    periods = 30
    return model.predict(model.make_future_dataframe(periods=periods)[-periods:])[['ds', 'yhat']].rename(columns = {'ds':'Date', 'yhat':'Close_Prediction'})