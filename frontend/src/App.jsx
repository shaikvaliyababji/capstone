import React, { useState, useEffect } from 'react';
import { 
  Sliders, 
  Power, 
  Home, 
  Wifi, 
  WifiOff, 
  AlertTriangle 
} from 'lucide-react';

import Header from './components/Header';
import Sidebar from './components/Sidebar';
import RoomSection from './components/RoomSection';
import DeviceGrid from './components/DeviceGrid';
import { getDevices } from './services/api';

export default function App() {
  const [devices, setDevices] = useState([]);
  const [initialLoading, setInitialLoading] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState('Offline');
  const [globalError, setGlobalError] = useState(null);
  
  // Navigation & UI control state
  const [activeTab, setActiveTab] = useState('dashboard');
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  // Load device data from API
  const loadDevices = async (isRetry = false) => {
    if (isRetry) {
      setInitialLoading(true);
    }
    setGlobalError(null);
    try {
      const data = await getDevices();
      setDevices(data);
      setConnectionStatus('Connected');
      setGlobalError(null);
    } catch (err) {
      console.error('API Fetch Error:', err);
      setConnectionStatus('Offline');
      setGlobalError('Backend connection unavailable');
    } finally {
      setInitialLoading(false);
    }
  };

  useEffect(() => {
    loadDevices();
  }, []);

  // Derived state calculations (no hardcoding!)
  const totalDevices = devices.length;
  const activeDevices = devices.filter(d => d.status === 'ON' || d.status === 'UNLOCKED' || d.status === 'OPEN').length;
  
  const uniqueRooms = Array.from(
    new Set(devices.map(d => d.room).filter(Boolean))
  );
  const roomCount = uniqueRooms.length;

  // Group devices by room helper
  const groupDevicesByRoom = () => {
    return uniqueRooms.reduce((acc, room) => {
      acc[room] = devices.filter(d => d.room === room);
      return acc;
    }, {});
  };

  const groupedDevices = groupDevicesByRoom();

  const handleStateUpdate = async () => {
    // Silently reloads in background to keep UI fresh
    await loadDevices(false);
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        mobileOpen={mobileSidebarOpen}
        setMobileOpen={setMobileSidebarOpen}
      />

      {/* Main Panel */}
      <div className="main-content">
        <Header 
          connectionStatus={connectionStatus}
          totalDevices={totalDevices}
          activeDevices={activeDevices}
          roomCount={roomCount}
          onMenuToggle={() => setMobileSidebarOpen(!mobileSidebarOpen)}
        />

        {/* Global Loading Spinner */}
        {initialLoading ? (
          <div className="full-screen-loader">
            <div className="spinner" />
            <p className="loader-text">Loading your smart home...</p>
          </div>
        ) : globalError ? (
          /* Global API Connection Error State */
          <div className="error-container glass">
            <div className="error-icon-wrapper">
              <WifiOff size={32} />
            </div>
            <h2 className="error-title">Backend connection unavailable</h2>
            <p className="error-message">
              We're having trouble connecting to the AI-SmartHome backend service.<br />
              Please make sure your FastAPI server is running on <code style={{ background: 'rgba(0,0,0,0.3)', padding: '0.2rem 0.4rem', borderRadius: '4px' }}>http://127.0.0.1:8000</code>.
            </p>
            <button className="error-action-btn" onClick={() => loadDevices(true)}>
              Retry Connection
            </button>
          </div>
        ) : (
          /* Dashboard Main Content Views */
          <main style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
            
            {/* Top Summaries (Derived values) */}
            {activeTab === 'dashboard' && (
              <div className="stats-grid">
                <div className="stat-card glass">
                  <div className="stat-icon-wrapper">
                    <Sliders size={20} />
                  </div>
                  <div className="stat-info">
                    <span className="stat-label">Total Devices</span>
                    <strong className="stat-value">{totalDevices}</strong>
                  </div>
                </div>

                <div className="stat-card glass">
                  <div className="stat-icon-wrapper" style={{ color: activeDevices > 0 ? 'var(--accent-on)' : 'var(--text-secondary)' }}>
                    <Power size={20} />
                  </div>
                  <div className="stat-info">
                    <span className="stat-label">Active Devices</span>
                    <strong className="stat-value">{activeDevices}</strong>
                  </div>
                </div>

                <div className="stat-card glass">
                  <div className="stat-icon-wrapper">
                    <Home size={20} />
                  </div>
                  <div className="stat-info">
                    <span className="stat-label">Total Rooms</span>
                    <strong className="stat-value">{roomCount}</strong>
                  </div>
                </div>

                <div className="stat-card glass">
                  <div className="stat-icon-wrapper" style={{ color: connectionStatus === 'Connected' ? 'var(--accent-on)' : 'var(--danger)' }}>
                    <Wifi size={20} />
                  </div>
                  <div className="stat-info">
                    <span className="stat-label">System Status</span>
                    <strong className="stat-value" style={{ fontSize: '1.1rem', marginTop: '0.2rem' }}>
                      {connectionStatus === 'Connected' ? 'Online' : 'Offline'}
                    </strong>
                  </div>
                </div>
              </div>
            )}

            {/* TAB VIEWS */}
            {activeTab === 'dashboard' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '-1.5rem' }}>
                  Overview by Room
                </h2>
                {uniqueRooms.map(room => (
                  <RoomSection
                    key={room}
                    roomName={room}
                    devices={groupedDevices[room]}
                    onStateUpdate={handleStateUpdate}
                  />
                ))}
              </div>
            )}

            {activeTab === 'rooms' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
                {uniqueRooms.map(room => (
                  <RoomSection
                    key={room}
                    roomName={room}
                    devices={groupedDevices[room]}
                    onStateUpdate={handleStateUpdate}
                  />
                ))}
              </div>
            )}

            {activeTab === 'devices' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-primary)', paddingBottom: '0.25rem', borderBottom: '1px solid var(--border)' }}>
                  All Connected Devices
                </h2>
                <DeviceGrid
                  devices={devices}
                  onStateUpdate={handleStateUpdate}
                />
              </div>
            )}

          </main>
        )}
      </div>
    </div>
  );
}
