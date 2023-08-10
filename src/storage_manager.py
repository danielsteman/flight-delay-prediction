from google.cloud import storage


class StorageManager:
    def __init__(self, bucket: str) -> None:
        self.client = storage.Client.from_service_account_json(
            ".gcp-credentials/credentials.json"
        ).get_bucket(bucket)
