// src/components/Navbar.jsx
import React, { useState } from 'react';
import { Shield, Terminal, BookOpen, Info, Menu, X, Github } from 'lucide-react';

export default function Navbar({ currentPage, onNavigate }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { id: 'home', label: 'Home', icon: Shield },
    { id: 'app', label: 'Analyzer', icon: Terminal },
    { id: 'docs', label: 'Docs', icon: BookOpen },
    { id: 'about', label: 'About', icon: Info },
  ];

  const handleNavClick = (id) => {
    onNavigate(id);
    setMobileMenuOpen(false);
  };

  return (
    <header className="glass-panel site-header sticky top-0 z-50 flex items-center px-4 sm:px-8 lg:px-12 w-full">
      <div className="max-w-full w-full mx-auto flex items-center justify-between">
        {/* Brand Logo */}
        <div 
          onClick={() => handleNavClick('home')} 
          className="brand-link flex items-center gap-3 cursor-pointer select-none"
        >
          <div className="brand-mark flex items-center justify-center font-bold text-sm">
            S
          </div>
          <div>
            <span className="font-bold tracking-tight text-base sm:text-lg block leading-none">SecureCode</span>
            <span className="brand-caption font-mono text-[10px] uppercase font-semibold block mt-0.5">STATIC ANALYZER</span>
          </div>
        </div>

        {/* Desktop Navigation */}
        <nav className="site-nav hidden md:flex items-center gap-1 lg:gap-2">
          {navItems.map((item) => {
            const isActive = currentPage === item.id;
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                aria-current={isActive ? 'page' : undefined}
                className={`flex items-center gap-2 px-3.5 py-2 text-sm font-medium transition-all rounded-lg ${
                  isActive 
                    ? 'text-[var(--ink)] font-bold bg-[var(--surface-raised)] border border-[var(--line)] shadow-sm' 
                    : 'text-[var(--muted)] hover:text-[var(--ink)] hover:bg-[var(--surface)]'
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </button>
            );
          })}

          <a
            href="https://github.com/stardustpelt/secure-code"
            target="_blank"
            rel="noopener noreferrer"
            className="ml-2 p-2.5 rounded-full border border-transparent hover:border-[var(--line)] hover:bg-[var(--surface)] transition-all flex items-center justify-center text-[var(--muted)] hover:text-[var(--ink)]"
            title="GitHub Repository"
          >
            <Github className="w-4 h-4" />
          </a>
        </nav>

        {/* Mobile Menu Button */}
        <div className="flex md:hidden items-center gap-2">
          <a
            href="https://github.com/stardustpelt/secure-code"
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 rounded-full text-[var(--muted)] hover:text-[var(--ink)]"
            title="GitHub Repository"
          >
            <Github className="w-4 h-4" />
          </a>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="menu-toggle p-2 text-[var(--ink)] focus:outline-none"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Dropdown Menu */}
      {mobileMenuOpen && (
        <div className="absolute top-full left-0 right-0 glass-panel mobile-menu p-4 border-t border-[var(--line)] shadow-lg md:hidden flex flex-col gap-2">
          {navItems.map((item) => {
            const isActive = currentPage === item.id;
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium w-full text-left transition-colors ${
                  isActive ? 'bg-[var(--accent)] text-[var(--accent-ink)] font-bold' : 'hover:bg-[var(--surface)] text-[var(--muted)] hover:text-[var(--ink)]'
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
}