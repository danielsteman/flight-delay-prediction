from google.cloud import storage


class StorageManager:
    def __init__(self, bucket: str) -> None:
        self.client = storage.Client.from_service_account_json(
            ".gcp-credentials/credentials.json"
        ).get_bucket(bucket)

    def download(self, path) -> str:
        data = self.client.blob(path).download_as_string().decode("utf-8")
        return data

    def upload(self, data: str, path: str) -> None:
        blob = self.client.blob(path)
        blob.upload_from_string(data, content_type="application/json")
