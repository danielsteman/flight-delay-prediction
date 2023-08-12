from dataclasses import dataclass


@dataclass
class Stats:
    n_downloaded: int = 0
    n_uploaded: int = 0

    def increment_downloads(self):
        self.n_downloaded += 1

    def increment_uploads(self):
        self.n_uploaded += 1
