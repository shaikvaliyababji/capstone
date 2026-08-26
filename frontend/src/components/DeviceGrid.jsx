import React from 'react';
import DeviceCard from './DeviceCard';

/**
 * DeviceGrid renders a flat, responsive layout of DeviceCards.
 * Used for views where room grouping is not needed.
 * @param {Object} props
 * @param {Array} props.devices - Flat array of device objects
 * @param {Function} props.onStateUpdate - Callback to update parent state
 */
export default function DeviceGrid({ devices, onStateUpdate }) {
  return (
    <div className="device-grid">
      {devices.map(device => (
        <DeviceCard 
          key={device.id} 
          device={device} 
          onStateUpdate={onStateUpdate} 
        />
      ))}
    </div>
  );
}
