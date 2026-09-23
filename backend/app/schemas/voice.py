from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class VoiceCommandRequest(BaseModel):
    text: str
    language: Optional[str] = "en"


class DeviceActionResult(BaseModel):
    device: str
    action: str
    target_status: str
    success: bool
    message: Optional[str] = None


class VoiceCommandResponse(BaseModel):
    query: str
    intent: str
    response: str
    language: Optional[str] = "en"
    actions: List[DeviceActionResult] = []
    active_devices_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class SceneInfo(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    example_phrases: List[str]
