# tests/test_sample.py
from fastapi.testclient import TestClient

def test_get_sample(client: TestClient):
    """Test the sample endpoint."""
    response = client.get("/sample/")
    assert response.status_code == 200
    assert response.json() == {"message": "테스트 샘플 router입니다. from sample.py"}
