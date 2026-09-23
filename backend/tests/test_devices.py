import pytest




def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AI Smart Home Running"}


def test_get_devices(client):
    response = client.get("/devices")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7
    # Verify bedroom_light is in there
    bedroom_light = next(d for d in data if d["name"] == "bedroom_light")
    assert bedroom_light["status"] == "OFF"
    assert bedroom_light["category"] == "light"


def test_turn_on_device(client):
    # Turn ON bedroom_light
    response = client.post("/devices/bedroom_light/on")
    assert response.status_code == 200
    assert response.json() == {"message": "bedroom_light turned ON"}
    
    # Get devices and verify state in cache/DB
    response = client.get("/devices")
    data = response.json()
    bedroom_light = next(d for d in data if d["name"] == "bedroom_light")
    assert bedroom_light["status"] == "ON"


def test_turn_off_device(client):
    # Turn OFF bedroom_light
    response = client.post("/devices/bedroom_light/off")
    assert response.status_code == 200
    assert response.json() == {"message": "bedroom_light turned OFF"}
    
    # Get devices and verify state in cache/DB
    response = client.get("/devices")
    data = response.json()
    bedroom_light = next(d for d in data if d["name"] == "bedroom_light")
    assert bedroom_light["status"] == "OFF"


def test_device_not_found(client):
    response = client.post("/devices/non_existent_device/on")
    assert response.status_code == 404
    assert "Device 'non_existent_device' not found" in response.json()["detail"]
