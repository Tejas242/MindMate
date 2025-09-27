import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Components
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import StudentDashboard from './pages/StudentDashboard';
import ChatPage from './pages/ChatPage';
import CounsellorDashboard from './pages/CounsellorDashboard';
import LoadingSpinner from './components/LoadingSpinner';

// Protected Route Component
const ProtectedRoute = ({ children, requiredRole }) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user.role !== requiredRole && !(requiredRole === 'counsellor' && user.role === 'admin')) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

// App Content (inside AuthProvider)
const AppContent = () => {
  const { loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Protected Routes */}
          <Route path="/" element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/chat" element={
            <ProtectedRoute requiredRole="student">
              <Layout>
                <ChatPage />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/chat/:sessionId" element={
            <ProtectedRoute requiredRole="student">
              <Layout>
                <ChatPage />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/counsellor" element={
            <ProtectedRoute requiredRole="counsellor">
              <Layout>
                <CounsellorDashboard />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/unauthorized" element={
            <div className="flex items-center justify-center min-h-screen">
              <div className="text-center">
                <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
                <p className="text-gray-600">You don't have permission to access this page.</p>
              </div>
            </div>
          } />
          
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
      <Toaster position="top-right" />
    </Router>
  );
};

// Dashboard Component (route to appropriate dashboard based on role)
const Dashboard = () => {
  const { user } = useAuth();
  
  if (user.role === 'student') {
    return <StudentDashboard />;
  } else if (user.role === 'counsellor' || user.role === 'admin') {
    return <CounsellorDashboard />;
  }
  
  return <Navigate to="/unauthorized" replace />;
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
