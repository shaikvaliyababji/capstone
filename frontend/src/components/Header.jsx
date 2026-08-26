import React from 'react';
import { Menu, Activity, ShieldCheck, Database } from 'lucide-react';
import StatusBadge from './StatusBadge';

/**
 * Header component displaying logo, system status summaries, and responsive triggers.
 * @param {Object} props
 * @param {string} props.connectionStatus - 'Connected' | 'Offline'
 * @param {number} props.totalDevices - Number of total devices
 * @param {number} props.activeDevices - Number of active (ON) devices
 * @param {number} props.roomCount - Number of unique rooms
 * @param {Function} props.onMenuToggle - Handler to toggle mobile sidebar
 */
export default function Header({ 
  connectionStatus, 
  totalDevices, 
  activeDevices, 
  roomCount, 
  onMenuToggle 
}) {
  return (
    <header className="app-header glass">
      <div className="header-left">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button 
            className="menu-toggle-btn" 
            onClick={onMenuToggle}
            aria-label="Toggle Sidebar Menu"
          >
            <Menu size={22} />
          </button>
          <div>
            <h1 className="header-logo">AI-SmartHome</h1>
            <p className="header-subtitle">AI-Powered Smart Home</p>
          </div>
        </div>
      </div>

      <div className="header-right">
        {/* System metrics showing derived state */}
        <div className="stats-indicator-group" style={{ display: 'flex', gap: '1rem' }}>
          <div className="header-stat-pill" style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', background: 'rgba(255,255,255,0.03)', padding: '0.25rem 0.5rem', borderRadius: '4px', border: '1px solid var(--border)' }}>
            <Database size={12} className="text-secondary" />
            <span style={{ color: 'var(--text-secondary)' }}>Devices:</span>
            <strong style={{ color: 'var(--text-primary)' }}>{totalDevices}</strong>
          </div>
          <div className="header-stat-pill" style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', background: 'rgba(255,255,255,0.03)', padding: '0.25rem 0.5rem', borderRadius: '4px', border: '1px solid var(--border)' }}>
            <Activity size={12} className="text-secondary" />
            <span style={{ color: 'var(--text-secondary)' }}>Active:</span>
            <strong style={{ color: 'var(--text-primary)' }}>{activeDevices}</strong>
          </div>
          <div className="header-stat-pill" style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', background: 'rgba(255,255,255,0.03)', padding: '0.25rem 0.5rem', borderRadius: '4px', border: '1px solid var(--border)' }}>
            <ShieldCheck size={12} className="text-secondary" />
            <span style={{ color: 'var(--text-secondary)' }}>Rooms:</span>
            <strong style={{ color: 'var(--text-primary)' }}>{roomCount}</strong>
          </div>
        </div>

        <StatusBadge status={connectionStatus} />
      </div>
    </header>
  );
}
