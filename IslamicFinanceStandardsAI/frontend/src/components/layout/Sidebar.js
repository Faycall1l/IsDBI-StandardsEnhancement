import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <h3 className="sidebar-title">Main</h3>
        <nav className="sidebar-menu">
          <NavLink to="/" className={({ isActive }) => 
            isActive ? "sidebar-menu-item active" : "sidebar-menu-item"
          } end>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="7" height="9" />
              <rect x="14" y="3" width="7" height="5" />
              <rect x="14" y="12" width="7" height="9" />
              <rect x="3" y="16" width="7" height="5" />
            </svg>
            Dashboard
          </NavLink>
          <NavLink to="/process-document" className={({ isActive }) => 
            isActive ? "sidebar-menu-item active" : "sidebar-menu-item"
          }>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="12" y1="18" x2="12" y2="12" />
              <line x1="9" y1="15" x2="15" y2="15" />
            </svg>
            Process Document
          </NavLink>
        </nav>
      </div>

      <div className="sidebar-section">
        <h3 className="sidebar-title">Standards</h3>
        <nav className="sidebar-menu">
          <NavLink to="/standards" className={({ isActive }) => 
            isActive ? "sidebar-menu-item active" : "sidebar-menu-item"
          } end>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
            </svg>
            All Standards
          </NavLink>
          <NavLink to="/standards?type=FAS" className={({ isActive }) => 
            isActive ? "sidebar-menu-item active" : "sidebar-menu-item"
          }>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
            </svg>
            FAS Standards
          </NavLink>
          <NavLink to="/standards?type=SS" className={({ isActive }) => 
            isActive ? "sidebar-menu-item active" : "sidebar-menu-item"
          }>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
              <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
            </svg>
            Shariah Standards
          </NavLink>
        </nav>
      </div>

      <div className="sidebar-section">
        <h3 className="sidebar-title">Enhancements</h3>
        <nav className="sidebar-menu">
          <NavLink to="/enhancements" className={({ isActive }) => 
            isActive ? "sidebar-menu-item active" : "sidebar-menu-item"
          } end>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
            </svg>
            All Enhancements
          </NavLink>
          <NavLink to="/enhancements?status=PROPOSED" className={({ isActive }) => 
            isActive ? "sidebar-menu-item active" : "sidebar-menu-item"
          }>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
            Proposed
          </NavLink>
          <NavLink to="/enhancements?status=APPROVED" className={({ isActive }) => 
            isActive ? "sidebar-menu-item active" : "sidebar-menu-item"
          }>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            Approved
          </NavLink>
        </nav>
      </div>

      <div className="sidebar-section">
        <h3 className="sidebar-title">Validation</h3>
        <nav className="sidebar-menu">
          <NavLink to="/validations" className={({ isActive }) => 
            isActive ? "sidebar-menu-item active" : "sidebar-menu-item"
          }>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
              <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
              <path d="M9 14l2 2 4-4" />
            </svg>
            Validation Results
          </NavLink>
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar;
