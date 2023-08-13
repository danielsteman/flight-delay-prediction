import json
import os
from io import BytesIO
from typing import Dict
from uuid import UUID, uuid4

import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from lib.logger import setup_logger
from lib.stats import Stats
from lib.storage_manager import StorageManager
from lib.utils import filter_nested_dict

logger = setup_logger()


class FlightTransformer:
    def __init__(
        self,
        bucket: str,
        experiment_id: UUID = uuid4(),
        cache_to_disk: bool = False,
    ) -> None:
        self.storage_manager = StorageManager(bucket)
        self.experiment_id = experiment_id
        self.cache_to_disk = cache_to_disk
        self.stats = Stats()
        self.load_data()

    def load_data(self) -> None:
        local_data_path = "data/raw_flights.joblib"
        if os.path.exists(local_data_path):
            self.data = joblib.load(local_data_path)
        else:
            self.data = self.storage_manager.download_all("raw_flights")
            if self.cache_to_disk:
                self.storage_manager.save_locally(self.data, "raw_flights")

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

        df["delay"] = df["scheduleDateTime"] - df["expectedTimeGateClosing"]
        df_cleaned = df.dropna(subset=["delay"])

        df_cleaned["delay_in_seconds"] = df_cleaned["delay"].apply(lambda x: x.seconds)
        df_cleaned = df_cleaned.drop(
            columns=["delay", "scheduleDateTime", "expectedTimeGateClosing"]
        )
        df_cleaned = df_cleaned.fillna(0)

        logger.info(f"Columns after tranformation: {df_cleaned.columns}")

        return df_cleaned

    def upload(self, data: pd.DataFrame) -> None:
        parquet_buffer = BytesIO()
        data.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)
        path = (
            f"experiments/experiment_{self.experiment_id}/transformed_flights.parquet"
        )
        blob = self.storage_manager.client.blob(path)

        logger.info(f"Stored data in {path}")

        blob.upload_from_file(parquet_buffer, content_type="application/octet-stream")
        parquet_buffer.close()

        self.stats.increment_uploads()
        logger.info(f"Stored {self.stats.n_uploaded} file(s)")
        logger.info(f"Stored {self.n_flights} flights")

    @property
    def n_flights(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} with {self.n_flights} flights"
