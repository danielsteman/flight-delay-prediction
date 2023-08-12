import os
import sys

import pytest

# Append the repository root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.flight_transformer import FlightTransformer  # noqa: E402


@pytest.fixture(scope="class")
def flight_transformer_instance():
    return FlightTransformer("flight-delay-prediction")


class TestFlightTransformer:
    @pytest.fixture(autouse=True)
    def setup(self, flight_transformer_instance):
        self.transformer = flight_transformer_instance

    def test_load_data(self):
        assert self.transformer
