import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Leaf, Scan, BookOpen, Menu, X } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();
  const [scrolled, setScrolled]   = useState(false);
  const [menuOpen, setMenuOpen]   = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const links = [
    { to: '/',         label: 'Home',     icon: <Leaf size={16} /> },
    { to: '/detect',   label: 'Detect',   icon: <Scan size={16} /> },
    { to: '/diseases', label: 'Diseases', icon: <BookOpen size={16} /> },
  ];

  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 1000,
      padding: '0 24px',
      background: scrolled
        ? 'rgba(11, 17, 32, 0.95)'
        : 'transparent',
      backdropFilter: scrolled ? 'blur(16px)' : 'none',
      borderBottom: scrolled ? '1px solid rgba(255,255,255,0.08)' : 'none',
      transition: 'all 0.3s ease',
    }}>
      <div style={{
        maxWidth: 1200, margin: '0 auto',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        height: 70,
      }}>
        {/* Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 38, height: 38,
            background: 'linear-gradient(135deg, #22c55e, #16a34a)',
            borderRadius: 10,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 20px rgba(34, 197, 94, 0.4)',
          }}>
            <Leaf size={20} color="white" />
          </div>
          <span style={{
            fontFamily: 'Outfit, sans-serif',
            fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc',
          }}>
            Crop<span style={{ color: '#22c55e' }}>Guard</span> AI
          </span>
        </Link>

        {/* Desktop links */}
        <div className="desktop-nav" style={{ display: 'flex', gap: 8 }}>
          {links.map(({ to, label, icon }) => {
            const active = location.pathname === to;
            return (
              <Link
                key={to} to={to}
                style={{
                  display: 'flex', alignItems: 'center', gap: 7,
                  padding: '8px 18px',
                  borderRadius: 10,
                  fontSize: '0.9rem', fontWeight: 500,
                  color: active ? '#22c55e' : '#94a3b8',
                  background: active ? 'rgba(34, 197, 94, 0.1)' : 'transparent',
                  border: active ? '1px solid rgba(34, 197, 94, 0.2)' : '1px solid transparent',
                  transition: 'all 0.2s',
                }}
              >
                {icon}{label}
              </Link>
            );
          })}
        </div>

        {/* CTA */}
        <Link to="/detect" className="btn btn-primary" style={{ padding: '10px 20px', fontSize: '0.85rem' }}>
          <Scan size={15} /> Analyse Leaf
        </Link>

        {/* Mobile menu button */}
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          style={{
            display: 'none',
            background: 'none', border: 'none',
            color: '#f8fafc', cursor: 'pointer',
          }}
          className="mobile-menu-btn"
        >
          {menuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile dropdown */}
      {menuOpen && (
        <div style={{
          background: '#0f172a',
          borderTop: '1px solid rgba(255,255,255,0.08)',
          padding: '12px 0',
        }}>
          {links.map(({ to, label, icon }) => (
            <Link
              key={to} to={to}
              onClick={() => setMenuOpen(false)}
              style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '12px 24px',
                color: location.pathname === to ? '#22c55e' : '#94a3b8',
                fontSize: '0.95rem',
              }}
            >
              {icon}{label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  );
};

export default Navbar;
