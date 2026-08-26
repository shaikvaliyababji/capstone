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
