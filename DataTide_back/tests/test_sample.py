# tests/test_sample.py
from fastapi.testclient import TestClient

def test_get_sample(client: TestClient):
    """Test the sample endpoint."""
    response = client.get("/api/sample/")
    assert response.status_code == 200
    assert response.json() == {"message": "이것은 sample router입니다. from sample.py"}
