from pydantic import BaseModel, ConfigDict
from typing import Optional


class DeviceBase(BaseModel):
    name: str
    room: str
    category: str
    status: str = "OFF"


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    room: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None


class DeviceResponse(DeviceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
