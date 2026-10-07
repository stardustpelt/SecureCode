// src/pages/LandingPage.jsx
import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Terminal, ArrowRight, CheckCircle2, Lock, FileCode2 } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.45, delay },
});

export default function LandingPage({ onNavigate }) {
  return (
    <div className="page-bg flex flex-col min-h-screen">
      <Navbar currentPage="home" onNavigate={onNavigate} />

      <main className="page-container flex-1 space-y-16 py-12">
        {/* Hero Section */}
        <motion.section {...fadeUp(0)} className="space-y-6 text-center max-w-3xl mx-auto pt-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-semibold feature-pill mx-auto">
            <Shield className="w-3.5 h-3.5 text-[var(--accent-ink)] dark:text-[var(--accent)]" />
            STATIC SECURITY & QUALITY SCANNER
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight">
            Analyze Python code securely without execution.
          </h1>

          <p className="text-sm sm:text-base text-[var(--muted)] leading-relaxed max-w-2xl mx-auto">
            SecureCode inspects Python code snippets and project files locally using Abstract Syntax Tree (AST) parsing to detect vulnerabilities, code quality concerns, and syntax issues instantly.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <button
              onClick={() => onNavigate('app')}
              className="px-6 py-3 rounded-full text-sm font-bold btn-primary shadow-lg transition-all inline-flex items-center gap-2"
            >
              Launch Analyzer <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => onNavigate('docs')}
              className="px-6 py-3 rounded-full text-sm font-bold btn-secondary transition-all"
            >
              Read Documentation
            </button>
          </div>
        </motion.section>

        {/* Feature Highlights Grid */}
        <motion.div {...fadeUp(0.1)} className="grid sm:grid-cols-3 gap-6 pt-4">
          <div className="glass-panel p-6 rounded-2xl space-y-3">
            <div className="w-10 h-10 rounded-xl accent-bg flex items-center justify-center font-bold">
              <Lock className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold">Safe AST Parsing</h3>
            <p className="text-sm text-[var(--muted)] leading-relaxed">
              Never executes untrusted code. Code is examined strictly as text via static analysis rules.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl space-y-3">
            <div className="w-10 h-10 rounded-xl accent-bg flex items-center justify-center font-bold">
              <Terminal className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold">CLI & Web Workflow</h3>
            <p className="text-sm text-[var(--muted)] leading-relaxed">
              Use the web interface for quick checks or run the portable CLI tool for local project folders.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl space-y-3">
            <div className="w-10 h-10 rounded-xl accent-bg flex items-center justify-center font-bold">
              <FileCode2 className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold">PDF Audit Reports</h3>
            <p className="text-sm text-[var(--muted)] leading-relaxed">
              Generate and download detailed, professionally formatted security audit summaries in PDF format.
            </p>
          </div>
        </motion.div>

        {/* Quick Overview Section */}
        <motion.section {...fadeUp(0.15)} className="glass-panel p-8 sm:p-12 rounded-2xl space-y-6">
          <div className="max-w-xl space-y-2">
            <h3 className="text-xs font-mono font-bold text-[var(--accent-ink)] dark:text-[var(--accent)] tracking-wider uppercase">DEVELOPER READY</h3>
            <h2 className="text-xl sm:text-2xl font-bold">Built for speed, accuracy, and ease of use.</h2>
            <p className="text-sm text-[var(--muted)] leading-relaxed">
              Whether checking individual scripts or running scans across entire repositories, SecureCode provides structured feedback categorized by severity levels.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 gap-4 pt-2">
            {[
              'Critical hardcoded credentials & secret keys',
              'High-risk injection risks (SQL, Command, XSS)',
              'Insecure deserialization & weak cryptography',
              'Configuration oversights & quality warnings',
            ].map((text, i) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-[var(--surface-raised)] border border-[var(--line)]">
                <CheckCircle2 className="w-4 h-4 text-[var(--accent-ink)] dark:text-[var(--accent)] shrink-0" />
                <span className="text-sm font-medium">{text}</span>
              </div>
            ))}
          </div>
        </motion.section>
      </main>

      <Footer />
    </div>
  );
}