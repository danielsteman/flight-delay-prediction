import json
from io import BytesIO
from typing import Dict, List

import joblib
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from lib.enums import ContentType
from lib.storage_manager import StorageManager


class FlightDelayModel:
    def __init__(self, bucket: str, experiment_id: str) -> None:
        self.experiment_id = experiment_id
        self.storage_manager = StorageManager(bucket)

    def save_metrics(self, y_test: List[float], y_pred: List[float]) -> None:
        metrics: Dict[str, float] = {
            "Mean Squared Error": mean_squared_error(y_test, y_pred),
            "Mean Absolute Error": mean_absolute_error(y_test, y_pred),
            "R-squared": r2_score(y_test, y_pred),
        }
        self.storage_manager.upload(
            json.dumps(metrics),
            f"experiments/experiment_{self.experiment_id}/metrics.json",
        )

    def save_model(self, model: BaseEstimator) -> None:
        serialized_model = BytesIO()
        joblib.dump(model, serialized_model)
        serialized_model.seek(0)
        self.storage_manager.upload(
            serialized_model,
            f"experiments/experiment_{self.experiment_id}/flight_delay_model.joblib",
            content_type=ContentType.STREAM,
        )

    def train(self) -> BaseEstimator:
        data = self.storage_manager.download(
            f"experiments/experiment_{self.experiment_id}/transformed_flights.parquet",
            content_type=ContentType.STREAM,
        )
        df = pd.read_parquet(data)

        independent_var = "delay_in_seconds"
        y = df[independent_var]
        X = df.drop(columns=[independent_var])

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = LinearRegression()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        self.save_metrics(y_test, y_pred)
        self.save_model(model)

        return model
