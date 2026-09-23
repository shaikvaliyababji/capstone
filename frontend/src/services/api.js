const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

/**
 * Fetch all devices and their statuses.
 */
export async function getDevices() {
  const response = await fetch(`${API_BASE_URL}/devices/`);
  if (!response.ok) {
    throw new Error(`Failed to fetch devices: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Turn a device ON.
 * @param {string} deviceName - The name of the device (e.g., 'bedroom_light')
 */
export async function turnDeviceOn(deviceName) {
  const encodedName = encodeURIComponent(deviceName);
  const response = await fetch(`${API_BASE_URL}/devices/${encodedName}/on`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to turn ON ${deviceName}: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Turn a device OFF.
 * @param {string} deviceName - The name of the device (e.g., 'bedroom_light')
 */
export async function turnDeviceOff(deviceName) {
  const encodedName = encodeURIComponent(deviceName);
  const response = await fetch(`${API_BASE_URL}/devices/${encodedName}/off`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to turn OFF ${deviceName}: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Send natural language or voice command to the AI assistant.
 * @param {string} text - Voice or typed user query
 * @param {string} [language='en'] - Preferred language locale code
 */
export async function sendVoiceCommand(text, language = 'en') {
  const response = await fetch(`${API_BASE_URL}/voice/command`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text, language }),
  });
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `Failed to process voice command: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch available smart home scene presets.
 */
export async function getVoiceScenes() {
  const response = await fetch(`${API_BASE_URL}/voice/scenes`);
  if (!response.ok) {
    throw new Error(`Failed to fetch scenes: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Return streaming URL for authentic native spoken TTS audio.
 * @param {string} text - Spoken response text
 * @param {string} [language='en'] - Target language code
 */
export function getTtsAudioUrl(text, language = 'en') {
  const cleanLang = (language || 'en').split('-')[0].toLowerCase();
  return `${API_BASE_URL}/voice/tts?text=${encodeURIComponent(text)}&lang=${cleanLang}`;
}

