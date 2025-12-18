// ==================== src/pages/index.jsx (FIXED FOR GLOBAL NAVBAR) ====================
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { authService } from '../services/authService';
import '../css/index.css';
import '../css/App.css';

const HomePage = () => {
  const isAuthenticated = authService.isAuthenticated();

  useEffect(() => {
    // Scroll reveal animation
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
        }
      });
    }, observerOptions);

    document.querySelectorAll('.scroll-reveal').forEach(el => {
      observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  // Smooth scroll to section
  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="home-page">
      {/* Hero Section - Now with proper padding for global navbar */}
      <section className="hero" style={{ paddingTop: '80px' }}>
        <div className="floating-element"></div>
        <div className="floating-element"></div>
        <div className="floating-element"></div>
        
        <div className="hero-content">
          <h1 className="hero-title">
            Your Personal Research Library
          </h1>
          <p className="hero-subtitle">
            Organize, Annotate, and Master Your Research Papers
          </p>
          <p className="hero-description">
            nerdNest is the ultimate tool for researchers, students, and academics. 
            Upload your papers, highlight key findings, take notes, and organize 
            everything in one beautiful, intuitive interface. Never lose track of 
            your valuable research again.
          </p>
          <div className="hero-actions">
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="btn btn-primary">
                  Go to Dashboard
                </Link>
                <Link to="/papers/upload" className="btn btn-secondary">
                  Upload Paper
                </Link>
              </>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary">
                  Get Started Free
                </Link>
                <Link to="/login" className="btn btn-secondary">
                  Sign In
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features" id="features">
        <div className="features-container">
          <div className="features-header scroll-reveal">
            <h2 className="features-title">
              Everything You Need to Organize Your Research
            </h2>
            <p className="features-subtitle">
              Powerful features designed for serious researchers and students
            </p>
          </div>

          <div className="features-grid">
            <div className="feature-card scroll-reveal">
              <div className="feature-icon">
                📚
              </div>
              <h3 className="feature-title">Paper Library</h3>
              <p className="feature-description">
                Upload and organize all your research papers in one place. 
                PDF support with cloud storage. Drag-and-drop interface for quick uploads.
              </p>
            </div>

            <div className="feature-card scroll-reveal">
              <div className="feature-icon">
                ✏️
              </div>
              <h3 className="feature-title">Smart Annotations</h3>
              <p className="feature-description">
                Highlight important text, add notes, and place sticky notes directly 
                on your PDFs. Your annotations are saved and synced across devices.
              </p>
            </div>

            <div className="feature-card scroll-reveal">
              <div className="feature-icon">
                🏷️
              </div>
              <h3 className="feature-title">Tag & Organize</h3>
              <p className="feature-description">
                Create custom tags and categories to organize papers by topic, 
                project, or importance. Hierarchical categories for better structure.
              </p>
            </div>

            <div className="feature-card scroll-reveal">
              <div className="feature-icon">
                🔍
              </div>
              <h3 className="feature-title">Powerful Search</h3>
              <p className="feature-description">
                Find any paper instantly by title, author, or content. 
                Advanced filters and smart search help you locate what you need fast.
              </p>
            </div>

            <div className="feature-card scroll-reveal">
              <div className="feature-icon">
                📊
              </div>
              <h3 className="feature-title">Reading Progress</h3>
              <p className="feature-description">
                Track which papers you've read and which are pending. 
                Get insights about your reading habits and research progress.
              </p>
            </div>

            <div className="feature-card scroll-reveal">
              <div className="feature-icon">
                🎨
              </div>
              <h3 className="feature-title">Beautiful Interface</h3>
              <p className="feature-description">
                Clean, modern design that makes research enjoyable. 
                Dark mode optimized for long reading sessions.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="features" id="about" style={{ backgroundColor: 'var(--bg-primary)' }}>
        <div className="features-container">
          <div className="features-header scroll-reveal">
            <h2 className="features-title">Built for Researchers</h2>
            <p className="features-subtitle" style={{ maxWidth: '700px', margin: '0 auto' }}>
              We understand the challenges of managing research papers. 
              nerdNest was created by researchers, for researchers, to solve 
              the pain of scattered PDFs, lost notes, and disorganized references.
            </p>
          </div>

          <div className="scroll-reveal" style={{ 
            maxWidth: '800px', 
            margin: '3rem auto 0',
            textAlign: 'center'
          }}>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '2rem',
              marginTop: '2rem'
            }}>
              <div>
                <h3 style={{ 
                  fontSize: '2.5rem', 
                  color: 'var(--purple-primary)',
                  marginBottom: '0.5rem'
                }}>
                  1000+
                </h3>
                <p style={{ color: 'var(--text-muted)' }}>Researchers</p>
              </div>
              <div>
                <h3 style={{ 
                  fontSize: '2.5rem', 
                  color: 'var(--accent-cyan)',
                  marginBottom: '0.5rem'
                }}>
                  50K+
                </h3>
                <p style={{ color: 'var(--text-muted)' }}>Papers Organized</p>
              </div>
              <div>
                <h3 style={{ 
                  fontSize: '2.5rem', 
                  color: 'var(--accent-orange)',
                  marginBottom: '0.5rem'
                }}>
                  100K+
                </h3>
                <p style={{ color: 'var(--text-muted)' }}>Highlights Made</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta">
        <div className="cta-content scroll-reveal">
          <h2 className="cta-title">
            Ready to Transform Your Research Workflow?
          </h2>
          <p className="cta-description">
            Join researchers worldwide who trust nerdNest to manage their academic papers. 
            Get started in seconds - no credit card required, completely free to use.
          </p>
          <div className="cta-actions">
            {isAuthenticated ? (
              <>
                <Link to="/papers/upload" className="btn btn-primary">
                  Upload Your First Paper
                </Link>
                <Link to="/dashboard" className="btn btn-ghost">
                  Go to Dashboard
                </Link>
              </>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary">
                  Create Free Account
                </Link>
                <Link to="/login" className="btn btn-ghost">
                  Sign In
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <p className="footer-text">
            © 2025 nerdNest. Built for researchers, by researchers.
          </p>
          <div className="footer-links">
            {isAuthenticated ? (
              <>
                <Link to="/dashboard">Dashboard</Link>
                <Link to="/papers">Library</Link>
                <Link to="/papers/upload">Upload</Link>
              </>
            ) : (
              <>
                <Link to="/">Home</Link>
                <button 
                  onClick={() => scrollToSection('features')} 
                  style={{ 
                    background: 'none', 
                    border: 'none', 
                    color: 'var(--text-secondary)',
                    cursor: 'pointer',
                    textDecoration: 'none',
                    fontSize: 'inherit'
                  }}
                >
                  Features
                </button>
                <button 
                  onClick={() => scrollToSection('about')}
                  style={{ 
                    background: 'none', 
                    border: 'none', 
                    color: 'var(--text-secondary)',
                    cursor: 'pointer',
                    textDecoration: 'none',
                    fontSize: 'inherit'
                  }}
                >
                  About
                </button>
                <Link to="/login">Login</Link>
                <Link to="/register">Sign Up</Link>
              </>
            )}
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;