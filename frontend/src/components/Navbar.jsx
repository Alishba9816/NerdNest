// Navbar.jsx
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { authService } from '../services/authService';
import { useEffect, useState } from 'react';

function Navbar() {
    const navigate = useNavigate();
    const location = useLocation();
    const isAuthenticated = authService.isAuthenticated();

    const [isScrolled, setIsScrolled] = useState(false);

    // ✅ ADDED — SCROLL ANIMATION LOGIC MOVED HERE
    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 50);
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const handleLogout = () => {
        authService.logout();
        navigate('/login');
    };

    const isActive = (path) => location.pathname === path;

    return (
        // ✅ APPLY SCROLLED CLASS
        <nav className={`navbar ${isScrolled ? 'scrolled' : ''}`}>
            <div className="navbar-content">
                <Link to={isAuthenticated ? "/dashboard" : "/"} className="navbar-logo">
                    NerdNest
                </Link>

                <ul className="navbar-navv">
                    {isAuthenticated ? (
                        <>
                            <li>
                                <Link 
                                    to="/dashboard" 
                                    className={isActive('/dashboard') ? 'active-link' : ''}
                                >
                                    Dashboard
                                </Link>
                            </li>

                            <li>
                                <Link 
                                    to="/papers"
                                    className={isActive('/papers') ? 'active-link' : ''}
                                >
                                    Library
                                </Link>
                            </li>

                            <li>
                                <button 
                                    onClick={handleLogout}
                                    className="btn btn-ghost"
                                >
                                    Logout
                                </button>
                            </li>
                        </>
                    ) : (
                        <>
                            <li><Link to="/login">Login</Link></li>

                            <li>
                                <Link to="/register" className="btn btn-primary">
                                    Sign Up
                                </Link>
                            </li>
                        </>
                    )}
                </ul>
            </div>
        </nav>
    );
}

export default Navbar;
