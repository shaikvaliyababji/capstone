import pytest




def test_voice_device_on(client):
    response = client.post("/voice/command", json={"text": "Turn on the living room light"})
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "device_control"
    assert len(data["actions"]) == 1
    assert data["actions"][0]["device"] == "living_room_light"
    assert data["actions"][0]["target_status"] == "ON"
    assert data["actions"][0]["success"] is True


def test_voice_device_off(client):
    response = client.post("/voice/command", json={"text": "Turn off living room light"})
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "device_control"
    assert data["actions"][0]["device"] == "living_room_light"
    assert data["actions"][0]["target_status"] == "OFF"


def test_voice_group_lights_off(client):
    # First turn on kitchen and bedroom
    client.post("/devices/kitchen_light/on")
    client.post("/devices/bedroom_light/on")

    response = client.post("/voice/command", json={"text": "Turn off all lights"})
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "group_control"
    # Should have turned off 3 lights
    devices_affected = [a["device"] for a in data["actions"]]
    assert "kitchen_light" in devices_affected
    assert "bedroom_light" in devices_affected
    assert "living_room_light" in devices_affected
    for a in data["actions"]:
        assert a["target_status"] == "OFF"


def test_voice_lock_door(client):
    # Unlock first
    client.post("/devices/door/on")
    response = client.post("/voice/command", json={"text": "Lock the front door"})
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "device_control"
    assert data["actions"][0]["device"] == "door"
    assert data["actions"][0]["target_status"] == "LOCKED"


def test_voice_scene_good_night(client):
    # Turn on a light and unlock door first
    client.post("/devices/bedroom_light/on")
    client.post("/devices/door/on")

    response = client.post("/voice/command", json={"text": "Good night assistant"})
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "scene_control"
    assert "Good night" in data["response"]

    # Verify door is locked and bedroom light is off
    dev_resp = client.get("/devices")
    devices = {d["name"]: d for d in dev_resp.json()}
    assert devices["bedroom_light"]["status"] == "OFF"
    assert devices["door"]["status"] == "LOCKED"
    assert devices["curtains"]["status"] == "CLOSED"


def test_voice_status_query(client):
    # Turn on fan
    client.post("/devices/fan/on")
    response = client.post("/voice/command", json={"text": "What devices are on?"})
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "status_query"
    assert "Fan" in data["response"]


def test_voice_scenes_endpoint(client):
    response = client.get("/voice/scenes")
    assert response.status_code == 200
    scenes = response.json()
    assert len(scenes) >= 5
    scene_ids = [s["id"] for s in scenes]
    assert "good_night" in scene_ids
    assert "movie_mode" in scene_ids
    assert "welcome_home" in scene_ids


def test_voice_empty_command(client):
    response = client.post("/voice/command", json={"text": "   "})
    assert response.status_code == 400


def test_voice_hindi_device_on(client):
    response = client.post("/voice/command", json={"text": "लिविंग रूम की लाइट चालू करो"})
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "device_control"
    assert data["language"] == "hi"
    assert data["actions"][0]["device"] == "living_room_light"
    assert data["actions"][0]["target_status"] == "ON"
    assert "चालू" in data["response"]


def test_voice_hindi_good_night(client):
    response = client.post("/voice/command", json={"text": "शुभ रात्रि"})
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "scene_control"
    assert data["language"] == "hi"
    assert "शुभ रात्रि" in data["response"]


def test_voice_telugu_fan_on(client):
    response = client.post("/voice/command", json={"text": "ఫ్యాన్ ఆన్ చేయి"})
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "device_control"
    assert data["language"] == "te"
    assert data["actions"][0]["device"] == "fan"
    assert data["actions"][0]["target_status"] == "ON"


def test_voice_spanish_lights_off(client):
    response = client.post("/voice/command", json={"text": "apaga todas las luces", "language": "es"})
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "group_control"
    assert data["language"] == "es"


def test_voice_hinglish_command(client):
    response = client.post("/voice/command", json={"text": "bedroom ki light on karo"})
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "device_control"
    assert data["actions"][0]["device"] == "bedroom_light"
    assert data["actions"][0]["target_status"] == "ON"


def test_voice_tts_streaming(client):
    # Test Telugu TTS audio streaming
    response_te = client.get("/voice/tts", params={"text": "లైట్ ఆన్ చేయబడింది", "lang": "te"})
    assert response_te.status_code == 200
    assert response_te.headers["content-type"] == "audio/mpeg"
    assert len(response_te.content) > 1000

    # Test Hindi TTS audio streaming
    response_hi = client.get("/voice/tts", params={"text": "लाइट चालू कर दी गई है", "lang": "hi"})
    assert response_hi.status_code == 200
    assert response_hi.headers["content-type"] == "audio/mpeg"
    assert len(response_hi.content) > 1000

    # Test empty validation
    response_empty = client.get("/voice/tts", params={"text": "   ", "lang": "en"})
    assert response_empty.status_code == 400

