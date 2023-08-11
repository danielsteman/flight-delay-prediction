import json
import os
from io import BytesIO
from typing import Dict
from uuid import UUID, uuid4

import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from src.logger import setup_logger
from src.stats import Stats
from src.storage_manager import StorageManager
from src.utils import filter_nested_dict

logger = setup_logger()


class FlightTransformer:
    def __init__(
        self,
        bucket: str,
        experiment_id: UUID = uuid4(),
        in_memory: bool = True,
    ) -> None:
        self.storage_manager = StorageManager(bucket)
        self.experiment_id = experiment_id
        self.in_memory = in_memory
        self.stats = Stats()
        self.load_data()

    def load_data(self) -> None:
        local_data_path = "data/raw_flights.joblib"
        if os.path.exists(local_data_path):
            self.data = joblib.load(local_data_path)
        else:
            self.data = self.manager.download_all("raw_flights")
            if not self.in_memory:
                self.manager.save_locally(self.data, "raw_flights")

        n = len(self.data)
        self.stats.n_downloaded = n
        logger.info(f"Number of flights in {self.__class__.__name__}: {n}")

    @classmethod
    def parse_and_extract(self, data: str) -> Dict:
        keys_to_extract = [
            "expectedTimeGateClosing",
            "scheduleDateTime",
            "codeshares",
            "flightDirection",
            "transferPositions",
            "checkinAllocations",
            "terminal",
        ]
        extracted_data = filter_nested_dict(
            json.loads(data), keys_to_include=keys_to_extract
        )
        return extracted_data

    @classmethod
    def make_tabular(self, data: Dict) -> Dict:
        tabular_data = data
        tabular_data["codeshares"] = (
            len(data["codeshares"]["codeshares"]) if data["codeshares"] else 0
        )
        tabular_data["transferPositions"] = (
            data["transferPositions"]["transferPositions"][0]
            if data["transferPositions"]
            else 0
        )
        tabular_data["checkinAllocations"] = (
            len(data["checkinAllocations"]["checkinAllocations"])
            if data["checkinAllocations"]
            else 0
        )
        return tabular_data

    def transform(self) -> pd.DataFrame:
        tabular_flights = []

        for flight in self.data:
            dict_flight = self.parse_and_extract(flight)
            tabular_flight = self.make_tabular(dict_flight)
            tabular_flights.append(tabular_flight)

        df = pd.DataFrame(tabular_flights)

        df["expectedTimeGateClosing"] = pd.to_datetime(
            df["expectedTimeGateClosing"], format="%Y-%m-%dT%H:%M:%S.%f%z"
        )
        df["scheduleDateTime"] = pd.to_datetime(
            df["scheduleDateTime"], format="%Y-%m-%dT%H:%M:%S.%f%z"
        )

        label_encoder = LabelEncoder()
        df["flightDirection"] = label_encoder.fit_transform(df["flightDirection"])

        return df

    def upload(self, data: pd.DataFrame) -> None:
        parquet_buffer = BytesIO()
        data.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)
        path = f"{self.experiment_id}/train_set.parquet"
        blob = self.storage_manager.client.blob(path)

        logger.info(f"Stored train_set in {path}")

        blob.upload_from_file(parquet_buffer, content_type="application/octet-stream")
        parquet_buffer.close()

        self.stats.increment_uploads()
        logger.info(f"Stored {self.stats.n_uploaded} flights")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} with {len(self.data)} flights"
