import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.base import Base
from app.database.session import get_db

# Use a test SQLite database
TEST_DATABASE_URL = "sqlite:///./test_smarthome.db"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # Create the tables
    Base.metadata.create_all(bind=engine)
    
    # Seed default devices
    from app.models.device import Device
    db = TestingSessionLocal()
    if db.query(Device).count() == 0:
        default_devices = [
            Device(name="bedroom_light", room="bedroom", category="light", status="OFF"),
            Device(name="living_room_light", room="living_room", category="light", status="OFF"),
            Device(name="kitchen_light", room="kitchen", category="light", status="OFF"),
            Device(name="fan", room="living_room", category="fan", status="OFF"),
            Device(name="ac", room="bedroom", category="ac", status="OFF"),
            Device(name="door", room="entrance", category="security", status="LOCKED"),
            Device(name="curtains", room="living_room", category="comfort", status="CLOSED"),
        ]
        db.add_all(default_devices)
        db.commit()
    db.close()
    
    yield
    
    # Drop database tables
    Base.metadata.drop_all(bind=engine)
    
    # Clean up the test database file
    db_path = "./test_smarthome.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception as e:
            print(f"Could not remove test database file: {e}")


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AI Smart Home Running"}


def test_get_devices():
    response = client.get("/devices")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7
    # Verify bedroom_light is in there
    bedroom_light = next(d for d in data if d["name"] == "bedroom_light")
    assert bedroom_light["status"] == "OFF"
    assert bedroom_light["category"] == "light"


def test_turn_on_device():
    # Turn ON bedroom_light
    response = client.post("/devices/bedroom_light/on")
    assert response.status_code == 200
    assert response.json() == {"message": "bedroom_light turned ON"}
    
    # Get devices and verify state in cache/DB
    response = client.get("/devices")
    data = response.json()
    bedroom_light = next(d for d in data if d["name"] == "bedroom_light")
    assert bedroom_light["status"] == "ON"


def test_turn_off_device():
    # Turn OFF bedroom_light
    response = client.post("/devices/bedroom_light/off")
    assert response.status_code == 200
    assert response.json() == {"message": "bedroom_light turned OFF"}
    
    # Get devices and verify state in cache/DB
    response = client.get("/devices")
    data = response.json()
    bedroom_light = next(d for d in data if d["name"] == "bedroom_light")
    assert bedroom_light["status"] == "OFF"


def test_device_not_found():
    response = client.post("/devices/non_existent_device/on")
    assert response.status_code == 404
    assert "Device 'non_existent_device' not found" in response.json()["detail"]
