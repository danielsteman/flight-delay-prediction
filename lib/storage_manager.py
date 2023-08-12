from io import BytesIO
from typing import Any, List, Optional

import joblib
from google.cloud import storage

from lib.enums import ContentType
from lib.logger import setup_logger

logger = setup_logger()


class StorageManager:
    def __init__(self, bucket: str) -> None:
        self.client = storage.Client.from_service_account_json(
            "gcp-credentials.json"
        ).get_bucket(bucket)

    def download(
        self, path, content_type: ContentType = ContentType.JSON
    ) -> str | BytesIO:
        match content_type:
            case ContentType.JSON:
                data = self.client.blob(path).download_as_bytes().decode("utf-8")
            case ContentType.STREAM:
                data = BytesIO()
                self.client.blob(path).download_to_file(data)
                data.seek(0)
            case _:
                raise ValueError(f"Unsupported content_type: {content_type}")
        return data

    def upload(
        self,
        data: str | BytesIO,
        path: str,
        content_type: ContentType = ContentType.JSON,
    ) -> None:
        blob = self.client.blob(path)
        match content_type:
            case ContentType.JSON:
                blob.upload_from_string(data, content_type=content_type.value)
            case ContentType.STREAM:
                self.client.blob(path).upload_from_file(
                    data, content_type=content_type.value
                )
            case _:
                raise ValueError(f"Unsupported content_type: {content_type}")

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
