import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Terminal, ChevronDown, ChevronUp, AlertTriangle, AlertCircle, Info, CheckCircle } from 'lucide-react';
import Layout from './components/Layout';

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.45, delay },
});

function CodeBlock({ children }) {
  return (
    <div className="code-block rounded-xl p-4 overflow-x-auto">
      <pre className="text-xs sm:text-sm font-mono text-emerald-400 leading-relaxed whitespace-pre">{children}</pre>
    </div>
  );
}

function SeveritySection({ icon: Icon, color, bgClass, borderClass, textClass, title, items }) {
  const [open, setOpen] = useState(true);
  return (
    <div className={`rounded-xl border ${borderClass} ${bgClass} overflow-hidden`}>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3"
      >
        <div className="flex items-center gap-2">
          <Icon size={15} className={textClass} />
          <span className={`text-sm font-semibold ${textClass}`}>{title}</span>
        </div>
        {open ? <ChevronUp size={14} className={textClass} /> : <ChevronDown size={14} className={textClass} />}
      </button>
      {open && (
        <ul className="px-4 pb-3 space-y-1.5">
          {items.map(item => (
            <li key={item} className="flex items-start gap-2 text-xs text-slate-600 dark:text-slate-400">
              <span className={`w-1 h-1 rounded-full mt-1.5 flex-shrink-0 ${color}`} />
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function Documentation({ onNavigate }) {
  return (
    <Layout currentPage="docs" onNavigate={onNavigate}>
      <div className="max-w-4xl mx-auto">

        {/* Page title */}
        <motion.div {...fadeUp(0)} className="mb-8">
          <div className="flex items-center gap-2 mb-2">
            <span className="feature-pill text-xs font-semibold px-2.5 py-1 rounded-full">Docs</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold hero-title tracking-tight mb-2">Documentation</h1>
          <p className="text-slate-600 dark:text-slate-400 text-base">
            Check a pasted snippet or one Python file in the web UI, or scan files and folders with the full CLI.
          </p>
        </motion.div>

        {/* CLI entry point */}
        <motion.div {...fadeUp(0.05)} className="glass-panel rounded-2xl p-5 sm:p-7 mb-5">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Terminal size={16} className="text-teal-600 dark:text-teal-400" />
                <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">CLI Tool</h2>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                The full CLI is included in the repository. Run it from the repository root to scan individual files or folders with the same security and quality checks used by the local API.
              </p>
            </div>
            <div className="flex gap-2 flex-shrink-0">
              <motion.a
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.97 }}
                href="https://github.com/stardustpelt/secure-code/blob/main/docs/CLI_DOCUMENTATION.md"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary px-4 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 no-underline"
              >
                <Terminal size={14} />
                CLI Guide
              </motion.a>

            </div>
          </div>
        </motion.div>

        {/* CLI Usage */}
        <motion.div {...fadeUp(0.1)} className="glass-panel rounded-2xl p-6 sm:p-8 mb-5">
          <h2 className="section-header text-lg font-bold mb-4">CLI Usage</h2>
          <div className="space-y-4">
            <div>
              <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Full scanner — from the repository root</p>
              <CodeBlock>{`# Scan one file or recursively scan a project folder
python3 cli.py yourfile.py
python3 cli.py ./your-project

# Read Python source from stdin
cat yourfile.py | python3 cli.py -`}</CodeBlock>
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Report formats</p>
              <CodeBlock>{`# Save report to file
python3 cli.py ./your-project -o findings.txt
python3 cli.py ./your-project -o findings.json
python3 cli.py ./your-project -o findings.pdf

python3 cli.py ./your-project --format json`}</CodeBlock>
            </div>
          </div>
        </motion.div>

        {/* API Reference */}
        <motion.div {...fadeUp(0.15)} className="glass-panel rounded-2xl p-6 sm:p-8 mb-5">
          <h2 className="section-header text-lg font-bold mb-4">REST API</h2>
          <div className="space-y-4">
            {[
              {
                method: 'GET', path: '/api/health/', desc: 'Health check',
                response: `{ "status": "ok", "service": "SecureCode API" }`,
              },
              {
                method: 'POST', path: '/api/analyze/', desc: 'Analyze Python code',
                body: `# JSON body\n{ "code": "def hello():\\n    print('hi')", "filename": "test" }\n\n# Or multipart/form-data\nform.append('file', yourFile)`,
              },
              {
                method: 'GET', path: '/api/report/<filename>/?download=true', desc: 'Download PDF report',
              },
            ].map(({ method, path, desc, body, response }) => (
              <div key={path} className="info-card rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded font-mono ${
                    method === 'GET'
                      ? 'bg-teal-100 dark:bg-teal-900/40 text-teal-700 dark:text-teal-300'
                      : 'bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300'
                  }`}>{method}</span>
                  <code className="text-xs font-mono text-slate-700 dark:text-slate-300">{path}</code>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">{desc}</p>
                {(body || response) && (
                  <CodeBlock>{body || response}</CodeBlock>
                )}
              </div>
            ))}
          </div>
        </motion.div>

        {/* What it detects */}
        <motion.div {...fadeUp(0.2)} className="glass-panel rounded-2xl p-6 sm:p-8 mb-5">
          <h2 className="section-header text-lg font-bold mb-4">What SecureCode Detects</h2>
          <div className="space-y-3">
            <SeveritySection
              icon={AlertCircle}
              color="bg-red-500"
              bgClass="bg-red-50 dark:bg-red-900/10"
              borderClass="border-red-200 dark:border-red-800/30"
              textClass="text-red-600 dark:text-red-400"
              title="Critical"
              items={[
                'Hardcoded passwords & credentials',
                'eval() / exec() / compile() usage',
                'AWS credentials in source code',
              ]}
            />
            <SeveritySection
              icon={AlertTriangle}
              color="bg-orange-500"
              bgClass="bg-orange-50 dark:bg-orange-900/10"
              borderClass="border-orange-200 dark:border-orange-800/30"
              textClass="text-orange-600 dark:text-orange-400"
              title="High"
              items={[
                'SQL injection (string formatting in queries)',
                'Command injection (os.system, shell=True)',
                'XSS (mark_safe, render_template_string)',
                'Insecure deserialization (pickle, yaml.load)',
                'Weak cryptography (MD5, SHA1)',
                'Path traversal vulnerabilities',
                'Hardcoded API keys & tokens',
              ]}
            />
            <SeveritySection
              icon={Info}
              color="bg-amber-500"
              bgClass="bg-amber-50 dark:bg-amber-900/10"
              borderClass="border-amber-200 dark:border-amber-800/30"
              textClass="text-amber-600 dark:text-amber-400"
              title="Medium"
              items={[
                'DEBUG = True in production',
                'Wildcard ALLOWED_HOSTS',
                '@csrf_exempt decorator',
                'SSL verification disabled (verify=False)',
              ]}
            />
            <SeveritySection
              icon={CheckCircle}
              color="bg-teal-500"
              bgClass="bg-teal-50 dark:bg-teal-900/10"
              borderClass="border-teal-200 dark:border-teal-800/30"
              textClass="text-teal-600 dark:text-teal-400"
              title="Low / Code Quality"
              items={[
                'Syntax & indentation errors',
                'Bare except clauses',
                'Missing docstrings',
                'Mutable default arguments',
                'Deprecated APIs (Python 2 print, urllib.urlopen)',
                'Long lines (> 120 chars)',
                'Unresolved TODO/FIXME comments',
                'Insecure file upload (missing size/type validation)',
              ]}
            />
          </div>
        </motion.div>

        {/* How it works */}
        <motion.div {...fadeUp(0.25)} className="glass-panel rounded-2xl p-6 sm:p-8">
          <h2 className="section-header text-lg font-bold mb-5">How It Works</h2>
          <div className="space-y-4">
            {[
              { n: '01', title: 'No Code Execution', desc: 'Submitted code is checked with AST parsing and security and quality patterns; it is not run.' },
              { n: '02', title: 'Three-Layer Scan', desc: 'Indentation checker → Security vulnerability scanner → Code quality checker. All results merged.' },
              { n: '03', title: 'Severity Classification', desc: 'Findings are classified as CRITICAL, HIGH, MEDIUM, or LOW.' },
              { n: '04', title: 'PDF Report', desc: 'A structured PDF with summary table, issues overview, and detailed findings per issue.' },
            ].map(({ n, title, desc }) => (
              <div key={n} className="flex gap-4 items-start">
                <div className="step-num w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0">
                  {n}
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200 mb-0.5">{title}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

      </div>
    </Layout>
  );
}

export default Documentation;
