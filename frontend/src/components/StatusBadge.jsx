import React from 'react';

/**
 * StatusBadge component showing a status pill with a pulsing dot.
 * @param {Object} props
 * @param {string} props.status - The status label (e.g. 'Connected', 'Offline', 'ON', 'OFF')
 */
export default function StatusBadge({ status }) {
  const isActive = status === 'Connected' || status === 'ON' || status === 'Active' || status === 'UNLOCKED' || status === 'OPEN';
  const isOffline = status === 'Offline' || status === 'OFF' || status === 'LOCKED' || status === 'CLOSED';

  const getClassName = () => {
    if (isActive) return 'online';
    if (isOffline) return 'offline';
    return '';
  };

  return (
    <span className={`status-pill ${getClassName()}`}>
      <span className={`status-dot ${isActive ? 'active' : ''}`} />
      {status}
    </span>
  );
}
