// App.jsx
import './css/App.css';
import { Routes, Route } from 'react-router-dom';

import Navbar from './components/Navbar';   // ✅ ADDED

import IndexPage from './pages';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import PapersPage from './pages/PapersPage';
import UploadPaperPage from './pages/UploadPaperPage';
import CategoryViewPage from './pages/CategoryViewPage';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
    return (
        <>
            {/* ✅ GLOBAL NAVBAR (NEW) */}
            <Navbar />

            {/* Routes */}
            <Routes>
                {/* Public routes */}
                <Route path="/" element={<IndexPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                {/* Protected routes */}
                <Route
                    path="/dashboard"
                    element={
                        <ProtectedRoute>
                            <DashboardPage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/papers"
                    element={
                        <ProtectedRoute>
                            <PapersPage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/papers/upload"
                    element={
                        <ProtectedRoute>
                            <UploadPaperPage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/categories/:categoryId"
                    element={
                        <ProtectedRoute>
                            <CategoryViewPage />
                        </ProtectedRoute>
                    }
                />

                {/* 404 */}
                <Route path="*" element={<NotFoundPage />} />
            </Routes>
        </>
    );
}

function NotFoundPage() {
    return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="text-center">
                <h1 style={{ fontSize: '4rem', marginBottom: '1rem' }}>404</h1>
                <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
                    Page not found
                </p>
                <a href="/" className="btn btn-primary">
                    Go Home
                </a>
            </div>
        </div>
    );
}

export default App;
