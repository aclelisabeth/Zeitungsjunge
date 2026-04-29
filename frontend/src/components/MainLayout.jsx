import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import { useUIStore } from '../store';
import './MainLayout.css';

const MainLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const { sidebarOpen, toggleSidebar, notificationMessage, notificationType } = useUIStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <div className="main-layout">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <button 
            className="menu-toggle"
            onClick={toggleSidebar}
            title="Toggle sidebar"
          >
            ☰
          </button>
          
          <Link to="/" className="logo">
            <h1>Zeitungsjunge</h1>
          </Link>

          <div className="header-actions">
            <span className="user-info">{user?.full_name || user?.username}</span>
            <button 
              className="logout-btn"
              onClick={handleLogout}
              title="Logout"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="layout-container">
        {/* Sidebar */}
        <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
          <nav className="sidebar-nav">
            <Link 
              to="/" 
              className={`nav-item ${isActive('/') ? 'active' : ''}`}
            >
              <span className="icon">📰</span>
              <span className="label">Home</span>
            </Link>
            
            <Link 
              to="/search" 
              className={`nav-item ${isActive('/search') ? 'active' : ''}`}
            >
              <span className="icon">🔍</span>
              <span className="label">Search</span>
            </Link>
            
            <Link 
              to="/bookmarks" 
              className={`nav-item ${isActive('/bookmarks') ? 'active' : ''}`}
            >
              <span className="icon">⭐</span>
              <span className="label">Bookmarks</span>
            </Link>
            
            <Link 
              to="/profile" 
              className={`nav-item ${isActive('/profile') ? 'active' : ''}`}
            >
              <span className="icon">👤</span>
              <span className="label">Profile</span>
            </Link>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="main-content">
          {notificationMessage && (
            <div className={`notification notification-${notificationType}`}>
              {notificationMessage}
            </div>
          )}
          {children}
        </main>
      </div>

      {/* Footer */}
      <footer className="footer">
        <p>[OK] Zeitungsjunge v2.0.0 - News Aggregation & Summarization</p>
      </footer>
    </div>
  );
};

export default MainLayout;
