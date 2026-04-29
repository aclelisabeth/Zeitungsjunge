import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import { userAPI } from '../api/client';
import { useUIStore } from '../store';
import './ProfilePage.css';

const ProfilePage = () => {
  const { user, logout } = useAuth();
  const { showNotification } = useUIStore();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: user?.email || '',
    full_name: user?.full_name || '',
    full_name_field: user?.full_name || ''
  });
  const [preferences, setPreferences] = useState({});
  const [loading, setLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      const response = await userAPI.getPreferences();
      setPreferences(response.data);
    } catch (error) {
      showNotification('Failed to load preferences', 'error');
    }
  };

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await userAPI.updateProfile({
        email: formData.email,
        full_name: formData.full_name_field
      });
      setEditMode(false);
      showNotification('Profile updated successfully', 'success');
    } catch (error) {
      showNotification('Failed to update profile', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      try {
        await userAPI.deleteProfile();
        logout();
        navigate('/login');
        showNotification('Account deleted', 'success');
      } catch (error) {
        showNotification('Failed to delete account', 'error');
      }
    }
  };

  return (
    <div className="profile-page">
      <h1>Profile Settings</h1>

      {/* Profile Section */}
      <section className="profile-section">
        <h2>Account Information</h2>
        {!editMode ? (
          <div className="profile-info">
            <div className="info-item">
              <label>Username:</label>
              <span>{user?.username}</span>
            </div>
            <div className="info-item">
              <label>Email:</label>
              <span>{user?.email}</span>
            </div>
            <div className="info-item">
              <label>Full Name:</label>
              <span>{user?.full_name || 'Not set'}</span>
            </div>
            <button 
              onClick={() => setEditMode(true)}
              className="edit-btn"
            >
              Edit Profile
            </button>
          </div>
        ) : (
          <form onSubmit={handleSaveProfile} className="profile-form">
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleProfileChange}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="full_name_field">Full Name</label>
              <input
                type="text"
                id="full_name_field"
                name="full_name_field"
                value={formData.full_name_field}
                onChange={handleProfileChange}
                disabled={loading}
              />
            </div>

            <div className="button-group">
              <button 
                type="submit" 
                className="save-btn"
                disabled={loading}
              >
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
              <button 
                type="button"
                onClick={() => {
                  setEditMode(false);
                  setFormData({
                    email: user?.email || '',
                    full_name: user?.full_name || '',
                    full_name_field: user?.full_name || ''
                  });
                }}
                className="cancel-btn"
                disabled={loading}
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </section>

      {/* Preferences Section */}
      <section className="profile-section">
        <h2>Preferences</h2>
        <div className="preferences-info">
          <p>Default Region: <strong>{preferences.preferred_regions || 'global'}</strong></p>
          <p>Theme: <strong>{preferences.theme || 'light'}</strong></p>
          <p>Articles per page: <strong>{preferences.articles_per_page || 15}</strong></p>
        </div>
      </section>

      {/* Danger Zone */}
      <section className="profile-section danger-zone">
        <h2>Danger Zone</h2>
        <button 
          onClick={handleDeleteAccount}
          className="delete-btn"
        >
          Delete Account
        </button>
      </section>
    </div>
  );
};

export default ProfilePage;
