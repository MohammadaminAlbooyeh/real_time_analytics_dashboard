import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useSelector } from 'react-redux';
import { selectIsAuthenticated } from './store/selectors/dashboardSelectors';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import AnalyticsPage from './pages/AnalyticsPage';
import AlertsPage from './pages/AlertsPage';
import MetricsPage from './pages/MetricsPage';
import ReportsPage from './pages/ReportsPage';
import DataSourcesPage from './pages/DataSourcesPage';
import SettingsPage from './pages/SettingsPage';

function ProtectedRoute({ children }) {
  const isAuth = useSelector(selectIsAuthenticated);
  if (!isAuth && !localStorage.getItem('token')) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function AppLayout({ children }) {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <div style={{ flex: 1, marginLeft: 'var(--sidebar-width)' }}>
        <Header />
        <main style={{ padding: '24px' }}>{children}</main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ToastContainer
        position="top-right"
        theme="dark"
        autoClose={4000}
        hideProgressBar
      />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppLayout><DashboardPage /></AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <AppLayout><AnalyticsPage /></AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/alerts"
          element={
            <ProtectedRoute>
              <AppLayout><AlertsPage /></AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/metrics"
          element={
            <ProtectedRoute>
              <AppLayout><MetricsPage /></AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/reports"
          element={
            <ProtectedRoute>
              <AppLayout><ReportsPage /></AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/datasources"
          element={
            <ProtectedRoute>
              <AppLayout><DataSourcesPage /></AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <AppLayout><SettingsPage /></AppLayout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
