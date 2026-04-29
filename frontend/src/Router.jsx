import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import useAuth from './hooks/useAuth';

// Pages
import HomePage from './pages/HomePage';
import SearchPage from './pages/SearchPage';
import BookmarksPage from './pages/BookmarksPage';
import ProfilePage from './pages/ProfilePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import NotFoundPage from './pages/NotFoundPage';

// Layout
import MainLayout from './components/MainLayout';
import AuthLayout from './components/AuthLayout';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, getCurrentUser } = useAuth();
  
  useEffect(() => {
    if (isAuthenticated) {
      getCurrentUser();
    }
  }, [isAuthenticated, getCurrentUser]);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Public Route Component (redirect if already logged in)
const PublicRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return children;
};

function Router() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Auth Routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <AuthLayout>
                <LoginPage />
              </AuthLayout>
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <AuthLayout>
                <RegisterPage />
              </AuthLayout>
            </PublicRoute>
          }
        />

        {/* Protected Routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MainLayout>
                <HomePage />
              </MainLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/search"
          element={
            <ProtectedRoute>
              <MainLayout>
                <SearchPage />
              </MainLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/bookmarks"
          element={
            <ProtectedRoute>
              <MainLayout>
                <BookmarksPage />
              </MainLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <MainLayout>
                <ProfilePage />
              </MainLayout>
            </ProtectedRoute>
          }
        />

        {/* Not Found */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default Router;
