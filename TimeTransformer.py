import datetime

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class TimeTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, start_time="12000", max_trip_time=120):
        self.start_time = datetime.datetime.strptime("120000", "%H%M%S")
        self.max_trip_time = max_trip_time

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X.loc[:, :] = X[X["Time"] != "error"]
        X["Time"] = pd.to_datetime(X["Time"], format="%H%M%S")
        X["Time"] = X["Time"] - self.start_time
        X["Time"] = X["Time"].dt.total_seconds() / 60
        X = X.dropna()
        X = X[X["Time"] > 0]  # drop all items where time is negative
        X = X[X["Time"] < self.max_trip_time]  # drop all items where time is negative
        return X
