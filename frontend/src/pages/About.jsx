// src/pages/About.jsx
import React from 'react';
import { motion } from 'framer-motion';
import { Info, ShieldCheck, Terminal, Cpu, Code } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.45, delay },
});

export default function About({ onNavigate }) {
  return (
    <div className="page-bg flex flex-col min-h-screen">
      <Navbar currentPage="about" onNavigate={onNavigate} />

      <main className="page-container flex-1 space-y-12 py-12">
        {/* Header Section */}
        <motion.section {...fadeUp(0)} className="space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-semibold feature-pill">
            <Info className="w-3.5 h-3.5 text-[var(--accent-ink)] dark:text-[var(--accent)]" />
            PROJECT BACKGROUND
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">About SecureCode</h1>
          <p className="text-sm text-[var(--muted)] leading-relaxed max-w-2xl">
            Built as a robust static code analysis and security tool designed to surface Python vulnerabilities, code quality concerns, and syntax issues without executing untrusted source code.
          </p>
        </motion.section>

        {/* Mission & Philosophy */}
        <motion.div {...fadeUp(0.05)} className="grid md:grid-cols-2 gap-6">
          <div className="glass-panel p-6 sm:p-8 rounded-2xl space-y-4">
            <div className="w-10 h-10 rounded-xl accent-bg flex items-center justify-center font-bold">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h2 className="text-xl sm:text-2xl font-bold">Local-First & Safe</h2>
            <p className="text-sm text-[var(--muted)] leading-relaxed">
              SecureCode relies purely on Abstract Syntax Tree (AST) parsing and regex-based pattern matching. Submitted code snippets or files are inspected strictly as text, ensuring that malicious scripts or payloads are never imported or executed on the server.
            </p>
          </div>

          <div className="glass-panel p-6 sm:p-8 rounded-2xl space-y-4">
            <div className="w-10 h-10 rounded-xl accent-bg flex items-center justify-center font-bold">
              <Terminal className="w-5 h-5" />
            </div>
            <h2 className="text-xl sm:text-2xl font-bold">Dual Workflow</h2>
            <p className="text-sm text-[var(--muted)] leading-relaxed">
              Whether you need quick feedback on a snippet through the cloud-based web interface or want to recursively scan local directories offline using the portable CLI tool, SecureCode adapts seamlessly to your development pipeline.
            </p>
          </div>
        </motion.div>

        {/* Tech Stack */}
        <motion.section {...fadeUp(0.1)} className="glass-panel p-6 sm:p-8 rounded-2xl space-y-6">
          <h3 className="text-xs font-mono font-bold text-[var(--accent-ink)] dark:text-[var(--accent)] tracking-wider uppercase">TECHNOLOGY STACK</h3>
          <div className="grid sm:grid-cols-3 gap-4">
            {[
              { title: 'Frontend', desc: 'React, Tailwind CSS, Framer Motion, and Lucide Icons with fully responsive light/dark themes.', icon: Code },
              { title: 'Backend', desc: 'Python, Django REST framework, and ReportLab for programmatic PDF audit report generation.', icon: Cpu },
              { title: 'Analysis Engine', desc: 'Custom AST parser combined with multi-layer heuristic security and quality rule checkers.', icon: Terminal },
            ].map((tech) => {
              const Icon = tech.icon;
              return (
                <div key={tech.title} className="p-4 rounded-xl bg-[var(--surface-raised)] border border-[var(--line)] space-y-2">
                  <Icon className="w-5 h-5 text-[var(--accent-ink)] dark:text-[var(--accent)] mb-2" />
                  <h3 className="text-base font-bold">{tech.title}</h3>
                  <p className="text-sm text-[var(--muted)] leading-relaxed">{tech.desc}</p>
                </div>
              );
            })}
          </div>
        </motion.section>

        {/* Open Source CTA */}
        <motion.section {...fadeUp(0.15)} className="glass-panel p-8 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6 border-[var(--line)]">
          <div>
            <h3 className="text-xs font-mono font-bold text-[var(--accent-ink)] dark:text-[var(--accent)] tracking-wider uppercase mb-1">OPEN SOURCE</h3>
            <h2 className="text-xl sm:text-2xl font-bold">Contribute or inspect the codebase.</h2>
            <p className="text-sm text-[var(--muted)] mt-1">Explore the public repository on GitHub for contributions, issues, and CLI releases.</p>
          </div>
          <a
            href="https://github.com/stardustpelt/secure-code"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 rounded-full text-sm font-bold btn-primary shadow-lg transition-all whitespace-nowrap inline-flex items-center gap-2"
          >
            View on GitHub ↗
          </a>
        </motion.section>
      </main>

      <Footer />
    </div>
  );
}