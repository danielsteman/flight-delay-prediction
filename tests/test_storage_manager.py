import json
from io import BytesIO

import pandas as pd

from lib.enums import ContentType
from lib.storage_manager import StorageManager


class TestStorageManager:
    def test_json_upload_and_download(self):
        manager = StorageManager("flight-delay-prediction")
        data = json.dumps({"hoi": "hoi"})
        manager.upload(data, "test.json")
        file = manager.download("test.json")
        assert file == '{"hoi": "hoi"}'
        manager.client.delete_blob("test.json")

    def test_stream_upload_and_download(self):
        manager = StorageManager("flight-delay-prediction")
        byte_stream = BytesIO()
        df = pd.DataFrame([{"a": 1}])
        df.to_parquet(byte_stream, index=False)
        byte_stream.seek(0)
        manager.upload(byte_stream, "test.parquet", content_type=ContentType.STREAM)
        file = manager.download("test.parquet", content_type=ContentType.STREAM)
        df = pd.read_parquet(file)
        assert "a" in df.columns
        manager.client.delete_blob("test.parquet")
