import json
import os
from typing import Dict

import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from src.logger import setup_logger
from src.storage_manager import StorageManager
from src.utils import filter_nested_dict

logger = setup_logger()


class FlightTransformer:
    def __init__(self, bucket: str) -> None:
        self.storage_manager = StorageManager(bucket)
        self.get_data()

    def get_data(self) -> None:
        local_data_path = "data/raw_flights.joblib"
        if os.path.exists(local_data_path):
            self.data = joblib.load(local_data_path)
        else:
            self.data = self.manager.download_all("raw_flights")
            self.manager.save_locally(self.data, "raw_flights")

        logger.info(f"Number of flights in {self.__class__.__name__}: {len(self.data)}")

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
