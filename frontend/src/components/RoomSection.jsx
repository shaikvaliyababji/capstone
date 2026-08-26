import React from 'react';
import DeviceCard from './DeviceCard';
import { formatDeviceName } from '../utils/deviceUtils';

/**
 * RoomSection groups and renders a list of DeviceCards belonging to a specific room.
 * @param {Object} props
 * @param {string} props.roomName - The raw snake_case room identifier (e.g. 'living_room')
 * @param {Array} props.devices - Array of device objects in this room
 * @param {Function} props.onStateUpdate - Callback to update parent state when a device state updates
 */
export default function RoomSection({ roomName, devices, onStateUpdate }) {
  const displayRoom = formatDeviceName(roomName);

  return (
    <section className="room-section" aria-labelledby={`room-title-${roomName}`}>
      <div className="room-title-wrapper">
        <h2 id={`room-title-${roomName}`} className="room-title">
          {displayRoom}
        </h2>
        <span className="room-device-count">
          {devices.length} {devices.length === 1 ? 'device' : 'devices'}
        </span>
      </div>

      <div className="device-grid">
        {devices.map(device => (
          <DeviceCard 
            key={device.id} 
            device={device} 
            onStateUpdate={onStateUpdate} 
          />
        ))}
      </div>
    </section>
  );
}
