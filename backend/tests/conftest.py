import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.base import Base
from app.database.session import get_db
from app.models.device import Device
from app.services.device.manager import DeviceManager

TEST_DB_PATH = "./test_shared_smarthome.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Remove any existing test db
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Seed default devices
    db = TestingSessionLocal()
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

    # Reset DeviceManager cache
    DeviceManager._initialized = False
    DeviceManager._cache = {}

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass


@pytest.fixture
def client():
    return TestClient(app)
