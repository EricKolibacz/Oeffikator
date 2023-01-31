import requests.exceptions

from tests.api_commons import AppTestClient

client = AppTestClient("http://0.0.0.0:8001")


# TEST CASES: Basic API tests (how it behaves on different edge cases)


def test_alive():
    """Test whether the oeffikator is there."""
    try:
        response = client.alive()
        assert response.status_code == 200
        return
    except requests.exceptions.ConnectionError:
        pass
    # having this assert in the `except` block prints the entire stacktrace, which is confusing
    assert False, "test-app not found; start it via `docker compose up` in the tests folder"
