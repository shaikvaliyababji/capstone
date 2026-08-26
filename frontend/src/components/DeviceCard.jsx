import React, { useState } from 'react';
import { RefreshCw, AlertTriangle } from 'lucide-react';
import { formatDeviceName, getDeviceIcon } from '../utils/deviceUtils';
import { turnDeviceOn, turnDeviceOff } from '../services/api';

/**
 * DeviceCard component for controlling and displaying a single device.
 * @param {Object} props
 * @param {Object} props.device - Device schema object ({id, name, room, category, status})
 * @param {Function} props.onStateUpdate - Callback to notify parent of state changes (e.g. to reload list)
 */
export default function DeviceCard({ device, onStateUpdate }) {
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const IconComponent = getDeviceIcon(device.category);
  const isCurrentlyOn = device.status === 'ON' || device.status === 'UNLOCKED' || device.status === 'OPEN';
  const displayName = formatDeviceName(device.name);
  const displayRoom = formatDeviceName(device.room);
  const displayCategory = formatDeviceName(device.category);

  const handleToggle = async () => {
    if (loading) return;
    setErrorMsg(null);
    setLoading(true);

    try {
      if (isCurrentlyOn) {
        await turnDeviceOff(device.name);
      } else {
        await turnDeviceOn(device.name);
      }
      // Notify parent to refresh list from backend
      await onStateUpdate();
    } catch (err) {
      console.error(err);
      setErrorMsg(`Failed to turn ${isCurrentlyOn ? 'OFF' : 'ON'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    setErrorMsg(null);
    handleToggle();
  };

  return (
    <div className={`device-card glass ${isCurrentlyOn ? 'on' : ''}`}>
      {/* Loading Overlay */}
      {loading && (
        <div className="device-card-loading-overlay">
          <div className="spinner" />
        </div>
      )}

      {/* Error Overlay */}
      {errorMsg && (
        <div className="device-card-error-overlay">
          <AlertTriangle size={20} className="text-danger" style={{ color: 'var(--danger)' }} />
          <span className="card-error-text">{errorMsg}</span>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className="card-retry-btn" onClick={handleRetry}>
              Retry
            </button>
            <button 
              className="card-retry-btn" 
              style={{ background: 'rgba(255,255,255,0.05)', borderColor: 'var(--border)' }}
              onClick={() => setErrorMsg(null)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Card Header Info */}
      <div className="device-card-top">
        <div className="device-meta">
          <h3 className="device-name" title={displayName}>{displayName}</h3>
          <span className="device-details">
            {displayRoom} • {displayCategory}
          </span>
        </div>
        <div className="device-icon-container">
          <IconComponent size={20} />
        </div>
      </div>

      {/* Card Action Controls */}
      <div className="device-card-bottom">
        <span className="device-status-label">{device.status}</span>
        
        <label className="switch" htmlFor={`toggle-${device.id}`}>
          <input
            id={`toggle-${device.id}`}
            type="checkbox"
            checked={isCurrentlyOn}
            onChange={handleToggle}
            disabled={loading}
            aria-label={`Toggle status for ${displayName}`}
          />
          <span className="slider" />
        </label>
      </div>
    </div>
  );
}
