from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.device.manager import DeviceManager
from app.schemas.device import DeviceResponse

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get("/", response_model=List[DeviceResponse])
def get_devices(db: Session = Depends(get_db)):
    """
    Get all smart-home devices and their current status (cached read).
    """
    return DeviceManager.get_all_devices(db)


@router.post("/{device}/on")
def turn_on(device: str, db: Session = Depends(get_db)):
    """
    Turn on a device, updates cache and persists state to database.
    """
    if not DeviceManager.turn_on(db, device):
        raise HTTPException(status_code=404, detail=f"Device '{device}' not found")

    return {"message": f"{device} turned ON"}


@router.post("/{device}/off")
def turn_off(device: str, db: Session = Depends(get_db)):
    """
    Turn off a device, updates cache and persists state to database.
    """
    if not DeviceManager.turn_off(db, device):
        raise HTTPException(status_code=404, detail=f"Device '{device}' not found")

    return {"message": f"{device} turned OFF"}