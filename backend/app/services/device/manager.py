from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.repositories.device_repository import DeviceRepository
from app.services.device.simulator import DeviceSimulator

# In-memory hardware simulator instance
simulator = DeviceSimulator()


class DeviceManager:
    # In-memory device cache
    _cache: Dict[str, dict] = {}
    _initialized: bool = False

    @classmethod
    def _load_cache_if_needed(cls, db: Session):
        if not cls._initialized or not cls._cache:
            db_devices = DeviceRepository.get_all(db)
            for d in db_devices:
                cls._cache[d.name] = {
                    "id": d.id,
                    "name": d.name,
                    "room": d.room,
                    "category": d.category,
                    "status": d.status
                }
                # Sync simulator state with DB status
                if d.name in simulator.devices:
                    if d.status == "ON":
                        simulator.devices[d.name] = True
                    elif d.status == "OFF":
                        simulator.devices[d.name] = False
                    elif d.status in ("LOCKED", "locked", "Locked"):
                        simulator.devices[d.name] = "locked"
                    elif d.status in ("UNLOCKED", "unlocked", "Unlocked"):
                        simulator.devices[d.name] = "unlocked"
                    elif d.status in ("OPEN", "open", "Open"):
                        simulator.devices[d.name] = "open"
                    elif d.status in ("CLOSED", "closed", "Closed"):
                        simulator.devices[d.name] = "closed"
            cls._initialized = True

    @classmethod
    def get_all_devices(cls, db: Session) -> List[dict]:
        cls._load_cache_if_needed(db)
        return list(cls._cache.values())

    @classmethod
    def get_device(cls, db: Session, name: str) -> Optional[dict]:
        cls._load_cache_if_needed(db)
        return cls._cache.get(name)

    @classmethod
    def turn_on(cls, db: Session, name: str) -> bool:
        cls._load_cache_if_needed(db)
        if name not in cls._cache:
            return False

        # Determine target status based on category/name
        device_info = cls._cache[name]
        category = device_info["category"]
        
        if category == "security":
            target_status = "UNLOCKED"
        elif category == "comfort":
            target_status = "OPEN"
        else:
            target_status = "ON"

        # Update simulated hardware
        hardware_success = simulator.turn_on(name)
        if not hardware_success:
            return False

        # Update cache
        device_info["status"] = target_status

        # Persist to SQLite
        db_device = DeviceRepository.get_by_name(db, name)
        if db_device:
            DeviceRepository.update_status(db, db_device, target_status)

        return True

    @classmethod
    def turn_off(cls, db: Session, name: str) -> bool:
        cls._load_cache_if_needed(db)
        if name not in cls._cache:
            return False

        # Determine target status based on category/name
        device_info = cls._cache[name]
        category = device_info["category"]
        
        if category == "security":
            target_status = "LOCKED"
        elif category == "comfort":
            target_status = "CLOSED"
        else:
            target_status = "OFF"

        # Update simulated hardware
        hardware_success = simulator.turn_off(name)
        if not hardware_success:
            return False

        # Update cache
        device_info["status"] = target_status

        # Persist to SQLite
        db_device = DeviceRepository.get_by_name(db, name)
        if db_device:
            DeviceRepository.update_status(db, db_device, target_status)

        return True