# tests/test_items.py
from fastapi.testclient import TestClient

def test_read_items_empty(client: TestClient):
    """Test reading items when the database is empty."""
    response = client.get("/items/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_and_read_item(client: TestClient):
    """Test creating a single item and then reading it."""
    # Define the item payload
    item_payload = {"item_name": "Test Mackerel"}
    
    # Create the item
    response_create = client.post("/items/", json=item_payload)
    assert response_create.status_code == 200
    created_item = response_create.json()
    assert "item_pk" in created_item
    assert created_item["item_name"] == item_payload["item_name"]
    
    item_pk = created_item["item_pk"]

    # Read the specific item by its pk
    response_read_one = client.get(f"/items/{item_pk}")
    assert response_read_one.status_code == 200
    read_item = response_read_one.json()
    assert read_item == created_item

    # Read all items and expect a list containing the created item
    response_read_all = client.get("/items/")
    assert response_read_all.status_code == 200
    assert len(response_read_all.json()) == 1
    assert response_read_all.json()[0] == created_item

def test_read_nonexistent_item(client: TestClient):
    """Test reading an item that does not exist."""
    response = client.get("/items/9999") # Assuming 9999 does not exist
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}
