import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Moon, Sun, Menu, X, Terminal } from 'lucide-react';

function Layout({ children, currentPage, onNavigate }) {
  const [isDark, setIsDark] = React.useState(false);
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);

  const toggleTheme = () => {
    setIsDark(!isDark);
    document.documentElement.classList.toggle('dark');
  };

  const handleNavigate = (page) => {
    onNavigate(page);
    setIsMenuOpen(false);
  };

  const navLinks = [
    { id: 'home', label: 'Analyzer' },
    { id: 'docs', label: 'Docs' },
    { id: 'about', label: 'About' },
  ];

  return (
    <div className="min-h-screen page-bg">
      <div className="workbench-topline" aria-hidden="true" />

      {/* Header */}
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        className="sticky top-0 z-50 glass-panel site-header px-4 sm:px-8 py-3 flex items-center justify-between"
      >
        {/* Logo */}
        <button
          onClick={() => handleNavigate('home')}
          className="flex items-center gap-3 group brand-link"
        >
          <div className="brand-mark flex items-center justify-center text-[15px] font-black text-[#1d2a20] transition-transform group-hover:-rotate-6">
            S
          </div>
          <div className="flex flex-col leading-none">
            <span className="text-base font-bold text-slate-900 dark:text-slate-100">SecureCode</span>
            <span className="brand-caption text-[10px] font-medium uppercase">Python Analyzer</span>
          </div>
        </button>

        {/* Desktop Nav */}
        <nav className="hidden sm:flex items-center gap-1 site-nav" aria-label="Main navigation">
          {navLinks.map(link => (
            <button
              key={link.id}
              onClick={() => handleNavigate(link.id)}
              aria-current={currentPage === link.id ? 'page' : undefined}
              className={`px-4 py-2 text-sm font-medium transition-all ${
                currentPage === link.id
                  ? 'site-nav-active text-slate-900 dark:text-slate-100'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              {link.label}
            </button>
          ))}
        </nav>

        {/* Right controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={toggleTheme}
            className="theme-toggle p-2 text-slate-500 dark:text-slate-400 transition-colors"
            aria-label="Toggle theme"
          >
            {isDark
              ? <Sun className="w-4 h-4 text-amber-400" />
              : <Moon className="w-4 h-4" />
            }
          </button>
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="sm:hidden menu-toggle p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            aria-label={isMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
          >
            {isMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </button>
        </div>
      </motion.header>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
            className="sm:hidden fixed top-[57px] left-0 right-0 z-40 glass-panel mobile-menu px-4 py-3"
          >
            <nav className="flex flex-col gap-1">
              {navLinks.map(link => (
                <button
                  key={link.id}
                  onClick={() => handleNavigate(link.id)}
                  aria-current={currentPage === link.id ? 'page' : undefined}
                  className={`text-left py-2.5 px-4 text-sm font-medium transition-all ${
                    currentPage === link.id
                      ? 'site-nav-active text-slate-900 dark:text-slate-100'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  {link.label}
                </button>
              ))}
            </nav>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Page content */}
      <main id="main-content" className="px-4 sm:px-6 md:px-8 py-8 max-w-6xl mx-auto">
        {children}
      </main>

      {/* Footer */}
      <footer className="site-footer border-t border-slate-200 dark:border-slate-800 mt-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-8 py-6 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <div className="brand-mark brand-mark-small flex items-center justify-center text-[11px] font-black text-[#1d2a20]">
              S
            </div>
            <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">SecureCode</span>
          </div>
          <div className="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-500">
            <Terminal size={12} />
            <span>Python Security & Code Quality Analyzer</span>
          </div>
          <p className="text-xs text-slate-400 dark:text-slate-600">© 2025 noob_sandip</p>
        </div>
      </footer>
    </div>
  );
}

export default Layout;
