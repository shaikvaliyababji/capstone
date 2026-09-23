import React from 'react';
import { 
  Home, 
  LayoutDashboard, 
  Cpu, 
  Workflow, 
  Mic, 
  Settings, 
  X 
} from 'lucide-react';

/**
 * Sidebar component for primary dashboard navigation.
 * @param {Object} props
 * @param {string} props.activeTab - Currently active navigation tab
 * @param {Function} props.setActiveTab - Hook to update active tab
 * @param {boolean} props.mobileOpen - Status of sidebar drawer on mobile
 * @param {Function} props.setMobileOpen - Hook to close mobile sidebar drawer
 */
export default function Sidebar({ 
  activeTab, 
  setActiveTab, 
  mobileOpen, 
  setMobileOpen 
}) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, disabled: false },
    { id: 'rooms', label: 'Rooms', icon: Home, disabled: false },
    { id: 'devices', label: 'Devices', icon: Cpu, disabled: false },
    { id: 'automation', label: 'Automation', icon: Workflow, disabled: true },
    { id: 'voice', label: 'Voice Control', icon: Mic, disabled: false },
    { id: 'settings', label: 'Settings', icon: Settings, disabled: true }
  ];

  const handleNavClick = (id, disabled) => {
    if (disabled) return;
    setActiveTab(id);
    setMobileOpen(false); // Close sidebar on mobile after clicking
  };

  return (
    <>
      {/* Mobile Drawer Overlay */}
      {mobileOpen && (
        <div 
          className="sidebar-overlay" 
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside className={`app-sidebar glass ${mobileOpen ? 'mobile-open' : ''}`}>
        <div className="sidebar-brand">
          <Home className="brand-icon" size={24} />
          <span className="brand-name">AI-SmartHome</span>
          <button 
            className="menu-toggle-btn"
            style={{ marginLeft: 'auto' }}
            onClick={() => setMobileOpen(false)}
            aria-label="Close Sidebar Menu"
          >
            <X size={20} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id, item.disabled)}
                className={`nav-item ${isActive ? 'active' : ''} ${item.disabled ? 'disabled' : ''}`}
                disabled={item.disabled}
              >
                <span className="nav-item-content">
                  <Icon size={18} />
                  <span>{item.label}</span>
                </span>
                {item.disabled && (
                  <span className="badge-coming-soon">Coming Soon</span>
                )}
              </button>
            );
          })}
        </nav>

        <div style={{ padding: '1rem', borderTop: '1px solid var(--border)', fontSize: '0.7rem', color: 'var(--text-muted)', textAlign: 'center' }}>
          AI-SmartHome IoT v1.0.0
        </div>
      </aside>
    </>
  );
}
