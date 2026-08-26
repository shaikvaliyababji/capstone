from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate


class DeviceRepository:
    @staticmethod
    def get_all(db: Session) -> List[Device]:
        stmt = select(Device)
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_by_id(db: Session, device_id: int) -> Optional[Device]:
        stmt = select(Device).where(Device.id == device_id)
        return db.scalars(stmt).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Device]:
        stmt = select(Device).where(Device.name == name)
        return db.scalars(stmt).first()

    @staticmethod
    def create(db: Session, device_in: DeviceCreate) -> Device:
        db_device = Device(
            name=device_in.name,
            room=device_in.room,
            category=device_in.category,
            status=device_in.status
        )
        db.add(db_device)
        db.commit()
        db.refresh(db_device)
        return db_device

    @staticmethod
    def update(db: Session, db_device: Device, device_in: DeviceUpdate) -> Device:
        update_data = device_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_device, field, value)
        db.add(db_device)
        db.commit()
        db.refresh(db_device)
        return db_device

    @staticmethod
    def update_status(db: Session, db_device: Device, status: str) -> Device:
        db_device.status = status
        db.add(db_device)
        db.commit()
        db.refresh(db_device)
        return db_device

    @staticmethod
    def delete(db: Session, device_id: int) -> bool:
        stmt = select(Device).where(Device.id == device_id)
        db_device = db.scalars(stmt).first()
        if db_device:
            db.delete(db_device)
            db.commit()
            return True
        return False
