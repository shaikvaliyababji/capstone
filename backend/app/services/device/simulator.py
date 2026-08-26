class DeviceSimulator:
    def __init__(self):
        self.devices = {
            "bedroom_light": False,
            "living_room_light": False,
            "kitchen_light": False,
            "fan": False,
            "ac": False,
            "door": "locked",
            "curtains": "closed"
        }

    def get_devices(self):
        return self.devices

    def turn_on(self, device):
        if device not in self.devices:
            return False

        if device == "door":
            self.devices["door"] = "unlocked"

        elif device == "curtains":
            self.devices["curtains"] = "open"

        else:
            self.devices[device] = True

        return True

    def turn_off(self, device):
        if device not in self.devices:
            return False

        if device == "door":
            self.devices["door"] = "locked"

        elif device == "curtains":
            self.devices["curtains"] = "closed"

        else:
            self.devices[device] = False

        return True