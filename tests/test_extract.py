from src.extract import FlightsClient, PaginatedRequestsIterator


class TestPaginatedRequestsIterator:
    def test_remove_base(self):
        endpoint = PaginatedRequestsIterator._remove_base(
            "https://api.schiphol.nl:443/public-flights/flights"
        )
        assert endpoint == "flights"

    def test_remove_base_from_random_string(self):
        endpoint = PaginatedRequestsIterator._remove_base("some_random_ass_string")
        assert endpoint == "some_random_ass_string"


class TestFlightsClient:
    def test_get_request(self):
        client = FlightsClient()
        response = client.request("flights")
        assert response.status_code == 200
        data = response.json()
        assert data
