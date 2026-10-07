// src/pages/Documentation.jsx
import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Terminal, ShieldAlert, Cpu, ArrowRight, Download } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.45, delay },
});

export default function Documentation({ onNavigate }) {
  return (
    <div className="page-bg flex flex-col min-h-screen">
      <Navbar currentPage="docs" onNavigate={onNavigate} />

      <main className="page-container flex-1 space-y-12 py-12">
        {/* Header Section */}
        <motion.section {...fadeUp(0)} className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-semibold feature-pill">
              <BookOpen className="w-3.5 h-3.5 text-[var(--accent-ink)] dark:text-[var(--accent)]" />
              USER GUIDE & REFERENCE
            </div>

            {/* Direct Download CLI Release Button */}
            <a
              href="https://github.com/stardustpelt/SecureCode/releases/latest"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-mono font-bold btn-primary no-underline"
            >
              <Download className="w-3.5 h-3.5" />
              Download CLI (.zip)
            </a>
          </div>

          <h1 className="text-3xl sm:text-4xl font-black tracking-tight">Documentation</h1>
          <p className="text-sm sm:text-base text-[var(--muted)] leading-relaxed max-w-2xl">
            Learn how to use the web analyzer for quick checks, run the local CLI for project-wide directory scans, and integrate with the REST API.
          </p>
        </motion.section>

        {/* Quick Navigation Cards */}
        <motion.div {...fadeUp(0.05)} className="grid sm:grid-cols-3 gap-4">
          <a href="#cli-guide" className="glass-panel p-5 rounded-2xl flex flex-col justify-between hover:border-[var(--line-strong)] transition-all">
            <div>
              <Terminal className="w-5 h-5 text-[var(--accent-ink)] dark:text-[var(--accent)] mb-3" />
              <h3 className="font-bold text-base mb-1">CLI Reference</h3>
              <p className="text-xs text-[var(--muted)]">Commands, flags, and file output options.</p>
            </div>
            <span className="text-xs font-mono font-bold text-[var(--accent-ink)] dark:text-[var(--accent)] mt-4 inline-flex items-center gap-1">
              Jump to section <ArrowRight className="w-3 h-3" />
            </span>
          </a>

          <a href="#rest-api" className="glass-panel p-5 rounded-2xl flex flex-col justify-between hover:border-[var(--line-strong)] transition-all">
            <div>
              <Cpu className="w-5 h-5 text-[var(--accent-ink)] dark:text-[var(--accent)] mb-3" />
              <h3 className="font-bold text-base mb-1">REST API</h3>
              <p className="text-xs text-[var(--muted)]">Endpoints, health checks, and scan requests.</p>
            </div>
            <span className="text-xs font-mono font-bold text-[var(--accent-ink)] dark:text-[var(--accent)] mt-4 inline-flex items-center gap-1">
              Jump to section <ArrowRight className="w-3 h-3" />
            </span>
          </a>

          <a href="#detections" className="glass-panel p-5 rounded-2xl flex flex-col justify-between hover:border-[var(--line-strong)] transition-all">
            <div>
              <ShieldAlert className="w-5 h-5 text-[var(--accent-ink)] dark:text-[var(--accent)] mb-3" />
              <h3 className="font-bold text-base mb-1">Security Detections</h3>
              <p className="text-xs text-[var(--muted)]">Severity levels and rule breakdowns.</p>
            </div>
            <span className="text-xs font-mono font-bold text-[var(--accent-ink)] dark:text-[var(--accent)] mt-4 inline-flex items-center gap-1">
              Jump to section <ArrowRight className="w-3 h-3" />
            </span>
          </a>
        </motion.div>

        {/* CLI Guide Section */}
        <motion.section {...fadeUp(0.1)} id="cli-guide" className="glass-panel p-6 sm:p-8 rounded-2xl space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-[var(--line)]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl accent-bg flex items-center justify-center font-bold">
                <Terminal className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-xl sm:text-2xl font-bold">CLI Usage & Commands</h2>
                <p className="text-xs text-[var(--muted)] font-mono">standalone python package & scripts</p>
              </div>
            </div>
            <a
              href="https://github.com/stardustpelt/SecureCode/releases/latest"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden sm:inline-flex items-center gap-1.5 text-xs font-mono font-semibold text-[var(--muted)] hover:text-[var(--ink)]"
            >
              <Download className="w-3.5 h-3.5" /> Releases
            </a>
          </div>

          <div className="space-y-4 text-sm">
            <p className="text-[var(--muted)] leading-relaxed">
              The full CLI is included in the repository or available as a standalone release zip. Run it locally to scan individual files or folders with the exact same security and quality checks used by the API.
            </p>

            <div className="space-y-2">
              <h4 className="font-bold text-xs uppercase tracking-wider text-[var(--muted)] font-mono">Scan one file or recursively scan a project folder</h4>
              <pre className="code-block p-4 text-xs font-mono overflow-x-auto leading-relaxed">
                <code>{`python3 cli.py yourfile.py\npython3 cli.py ./your-project`}</code>
              </pre>
            </div>

            <div className="space-y-2">
              <h4 className="font-bold text-xs uppercase tracking-wider text-[var(--muted)] font-mono">Read Python source from standard input</h4>
              <pre className="code-block p-4 text-xs font-mono overflow-x-auto leading-relaxed">
                <code>{`cat yourfile.py | python3 cli.py -`}</code>
              </pre>
            </div>

            <div className="space-y-2">
              <h4 className="font-bold text-xs uppercase tracking-wider text-[var(--muted)] font-mono">Export and report format options</h4>
              <pre className="code-block p-4 text-xs font-mono overflow-x-auto leading-relaxed">
                <code>{`# Save reports to specific file formats\npython3 cli.py ./your-project -o findings.txt\npython3 cli.py ./your-project -o findings.json\npython3 cli.py ./your-project -o findings.pdf\n\n# Output format flag\npython3 cli.py ./your-project --format json`}</code>
              </pre>
            </div>
          </div>
        </motion.section>

        {/* REST API Section */}
        <motion.section {...fadeUp(0.15)} id="rest-api" className="glass-panel p-6 sm:p-8 rounded-2xl space-y-6">
          <div className="flex items-center gap-3 pb-4 border-b border-[var(--line)]">
            <div className="w-10 h-10 rounded-xl accent-bg flex items-center justify-center font-bold">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl sm:text-2xl font-bold">REST API Reference</h2>
              <p className="text-xs text-[var(--muted)] font-mono">backend service endpoints</p>
            </div>
          </div>

          <div className="space-y-6 text-sm">
            <div className="space-y-3 p-4 rounded-xl bg-[var(--surface-raised)] border border-[var(--line)]">
              <div className="flex items-center gap-2 font-mono text-xs">
                <span className="px-2 py-0.5 rounded font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">GET</span>
                <span className="font-bold">/api/health/</span>
                <span className="text-[var(--muted)] ml-auto">Health check</span>
              </div>
              <pre className="code-block p-3 text-xs font-mono overflow-x-auto">
                <code>{`{ "status": "ok", "service": "SecureCode API" }`}</code>
              </pre>
            </div>

            <div className="space-y-3 p-4 rounded-xl bg-[var(--surface-raised)] border border-[var(--line)]">
              <div className="flex items-center gap-2 font-mono text-xs">
                <span className="px-2 py-0.5 rounded font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">POST</span>
                <span className="font-bold">/api/analyze/</span>
                <span className="text-[var(--muted)] ml-auto">Analyze Python code</span>
              </div>
              <pre className="code-block p-3 text-xs font-mono overflow-x-auto">
                <code>{`# JSON body\n{ "code": "def hello():\\n    print('hi')", "filename": "test" }\n\n# Or multipart/form-data\nform.append('file', yourFile)`}</code>
              </pre>
            </div>

            <div className="space-y-3 p-4 rounded-xl bg-[var(--surface-raised)] border border-[var(--line)]">
              <div className="flex items-center gap-2 font-mono text-xs">
                <span className="px-2 py-0.5 rounded font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">GET</span>
                <span className="font-bold">/api/report/&lt;report_id&gt;/?download=true</span>
                <span className="text-[var(--muted)] ml-auto">Download PDF report</span>
              </div>
              <p className="text-xs text-[var(--muted)]">Retrieves the generated PDF audit report using the unique <code className="font-mono">report_id</code> returned by the analysis payload.</p>
            </div>
          </div>
        </motion.section>

        {/* Security Detections Section */}
        <motion.section {...fadeUp(0.2)} id="detections" className="glass-panel p-6 sm:p-8 rounded-2xl space-y-6">
          <div className="flex items-center gap-3 pb-4 border-b border-[var(--line)]">
            <div className="w-10 h-10 rounded-xl accent-bg flex items-center justify-center font-bold">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl sm:text-2xl font-bold">What SecureCode Detects</h2>
              <p className="text-xs text-[var(--muted)] font-mono">severity classifications & heuristic rules</p>
            </div>
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl stat-card-red space-y-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-rose-500/10 text-rose-600 border border-rose-500/20">Critical</span>
              <ul className="text-xs space-y-1.5 text-[var(--muted)] list-disc list-inside">
                <li>Hardcoded passwords & credentials</li>
                <li>eval() / exec() / compile() usage</li>
                <li>AWS credentials or secret keys in source</li>
              </ul>
            </div>

            <div className="p-4 rounded-xl stat-card-red space-y-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-amber-500/10 text-amber-600 border border-amber-500/20">High</span>
              <ul className="text-xs space-y-1.5 text-[var(--muted)] list-disc list-inside">
                <li>SQL injection (string formatting in queries)</li>
                <li>Command injection (os.system, shell=True)</li>
                <li>XSS (mark_safe, render_template_string)</li>
                <li>Insecure deserialization (pickle, yaml.load)</li>
                <li>Weak cryptography (MD5, SHA1 hashes)</li>
                <li>Path traversal vulnerabilities</li>
              </ul>
            </div>

            <div className="p-4 rounded-xl stat-card-amber space-y-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-sky-500/10 text-sky-600 border border-sky-500/20">Medium</span>
              <ul className="text-xs space-y-1.5 text-[var(--muted)] list-disc list-inside">
                <li>DEBUG = True left enabled in production</li>
                <li>Wildcard ALLOWED_HOSTS settings</li>
                <li>@csrf_exempt decorators</li>
                <li>SSL verification disabled (verify=False)</li>
              </ul>
            </div>

            <div className="p-4 rounded-xl stat-card-teal space-y-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">Low / Quality</span>
              <ul className="text-xs space-y-1.5 text-[var(--muted)] list-disc list-inside">
                <li>Syntax & indentation errors</li>
                <li>Bare except clauses</li>
                <li>Missing function docstrings</li>
                <li>Mutable default arguments</li>
                <li>Long lines (&gt; 120 chars) & TODO comments</li>
              </ul>
            </div>
          </div>
        </motion.section>
      </main>

      <Footer />
    </div>
  );
}