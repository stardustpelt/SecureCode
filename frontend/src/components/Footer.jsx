// src/components/Footer.jsx
import React from 'react';

export default function Footer() {
  return (
    <footer className="site-footer border-t border-[var(--line)] py-8 mt-auto w-full">
      <div className="max-w-[1400px] mx-auto px-4 sm:px-8 lg:px-12 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[var(--accent)]" />
          <span className="font-semibold">SecureCode Static Security & Quality Scanner</span>
        </div>
        
        <div className="flex items-center gap-6 font-mono text-[11px] text-[var(--muted)]">
          <a 
            href="https://github.com/stardustpelt/secure-code" 
            target="_blank" 
            rel="noopener noreferrer" 
            className="hover:text-[var(--ink)] transition-colors"
          >
            GitHub
          </a>
          <a 
            href="https://github.com/stardustpelt/secure-code/releases" 
            target="_blank" 
            rel="noopener noreferrer" 
            className="hover:text-[var(--ink)] transition-colors"
          >
            CLI Releases
          </a>
          <span>Python AST Engine</span>
        </div>
      </div>
    </footer>
  );
}