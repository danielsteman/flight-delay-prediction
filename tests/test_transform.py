import pytest

from lib.flight_transformer import FlightTransformer


@pytest.fixture(scope="class")
def flight_transformer_instance():
    return FlightTransformer("flight-delay-prediction")


class TestFlightTransformer:
    @pytest.fixture(autouse=True)
    def setup(self, flight_transformer_instance):
        self.transformer = flight_transformer_instance

    def test_load_data(self):
        assert self.transformer
