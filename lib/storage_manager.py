from typing import Any, List, Optional

import joblib
from google.cloud import storage

from lib.logger import setup_logger

logger = setup_logger()


class StorageManager:
    def __init__(self, bucket: str) -> None:
        self.client = storage.Client.from_service_account_json(
            "gcp-credentials.json"
        ).get_bucket(bucket)

    def download(self, blob_name) -> str:
        data = self.client.blob(blob_name).download_as_bytes().decode("utf-8")
        return data

    def upload(self, data: str, path: str) -> None:
        blob = self.client.blob(path)
        blob.upload_from_string(data, content_type="application/json")

    def download_all(self, prefix: Optional[str] = None, **kwargs) -> List[Any]:
        blob_data = []
        for blob in self.client.list_blobs(prefix=prefix, **kwargs):
            data = self.download(blob.name)
            blob_data.append(data)

            logger.info(f"Downloaded {blob.name}")

        return blob_data

    @classmethod
    def save_locally(self, data: Any, name: str) -> None:
        path = f"data/{name}.joblib"
        joblib.dump(data, path)
        logger.info(f"Serialized and saved data in {path}")
