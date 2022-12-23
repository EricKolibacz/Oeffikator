import datetime

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class TimeTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, start_time: str = "12000", max_trip_time: int = 120):
        self.start_time = datetime.datetime.strptime(start_time, "%H%M%S")
        self.max_trip_time = max_trip_time

    def fit(self, X: pd.DataFrame):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.dropna()
        X.drop(X[X["Time"] == "error"].index, inplace=True)
        X.drop(X[~X["Time"].str.match(r"(\b\d{6}\b)", na=False)].index, inplace=True)
        # X.loc[:, :] = X[X["Time"] != "error"]
        # X.loc[:, :] = X[X["Time"].str.match(r"(\b\d{6}\b)", na=False)]  # Remove wrong time formate
        X.loc[:, "Time"] = pd.to_datetime(X["Time"], format="%H%M%S")
        X.loc[:, "Time"] = X["Time"] - self.start_time
        X.loc[:, "Time"] = X["Time"].dt.total_seconds() / 60
        X.drop(X[X["Time"] < 0].index, inplace=True)  # drop all items where time is negative
        X.drop(X[X["Time"] > self.max_trip_time].index, inplace=True)  # drop all items where time is negative
        return X
