from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.device.manager import DeviceManager
from app.services.ai.nlp_service import NLPService
from app.schemas.voice import (
    VoiceCommandResponse,
    DeviceActionResult,
    SceneInfo
)


class VoiceService:
    """
    Orchestrator for natural language & voice commands.
    Connects NLP intent detection with DeviceManager execution and persistence.
    """

    @classmethod
    def execute_command(cls, db: Session, query: str, language: Optional[str] = "en") -> VoiceCommandResponse:
        """
        Execute natural language command on devices and return full results.
        """
        # Fetch current device state from manager
        current_devices = DeviceManager.get_all_devices(db)

        # Process through NLP engine
        nlp_result = NLPService.process_command(query, current_devices, language=language)

        actions_taken: List[DeviceActionResult] = []

        # Execute any target device actions
        for act in nlp_result.get("actions", []):
            dev_name = act.get("device")
            action_type = act.get("action", "on").lower()

            if action_type == "on":
                success = DeviceManager.turn_on(db, dev_name)
            else:
                success = DeviceManager.turn_off(db, dev_name)

            # Look up resulting state
            updated_device = DeviceManager.get_device(db, dev_name)
            target_status = updated_device.get("status", "UNKNOWN") if updated_device else "UNKNOWN"

            actions_taken.append(
                DeviceActionResult(
                    device=dev_name,
                    action=action_type,
                    target_status=target_status,
                    success=success,
                    message=f"{dev_name} successfully set to {target_status}" if success else f"Failed to modify {dev_name}"
                )
            )

        # Compute new active devices count
        fresh_devices = DeviceManager.get_all_devices(db)
        active_count = sum(
            1 for d in fresh_devices
            if d.get("status") in ["ON", "UNLOCKED", "OPEN"]
        )

        return VoiceCommandResponse(
            query=query,
            intent=nlp_result.get("intent", "device_control"),
            response=nlp_result.get("response", "Done."),
            language=nlp_result.get("language", language or "en"),
            actions=actions_taken,
            active_devices_count=active_count
        )

    @classmethod
    def get_available_scenes(cls) -> List[SceneInfo]:
        """Return smart scenes supported by the assistant."""
        scenes = NLPService.get_scenes()
        return [SceneInfo(**s) for s in scenes]
