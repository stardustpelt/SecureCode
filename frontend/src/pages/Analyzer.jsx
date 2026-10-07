// src/pages/Analyzer.jsx
import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, Upload, FileCode, AlertTriangle, ShieldCheck, Download, RefreshCw, CheckCircle2, XCircle, Info } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { scanCode, scanFile, getReportDownloadUrl } from '../services/api';

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.45, delay },
});

export default function Analyzer({ onNavigate }) {
  const [activeTab, setActiveTab] = useState('snippet'); // 'snippet' or 'file'
  const [codeSnippet, setCodeSnippet] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [report, setReport] = useState(null);

  const fileInputRef = useRef(null);

  const handleSnippetScan = async (e) => {
    e.preventDefault();
    if (!codeSnippet.trim()) {
      setError('Please provide a Python code snippet to analyze.');
      return;
    }

    setLoading(true);
    setError(null);
    setReport(null);

    try {
      const result = await scanCode({ code: codeSnippet, filename: 'snippet.py' });
      setReport(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileScan = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select or drop a Python file (.py) to analyze.');
      return;
    }

    setLoading(true);
    setError(null);
    setReport(null);

    try {
      const result = await scanFile(selectedFile);
      setReport(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
    }
  };

  const getSeverityBadge = (severity) => {
    const s = severity?.toLowerCase();
    if (s === 'critical') return 'bg-rose-500/10 text-rose-600 border border-rose-500/20';
    if (s === 'high') return 'bg-amber-500/10 text-amber-600 border border-amber-500/20';
    if (s === 'medium') return 'bg-sky-500/10 text-sky-600 border border-sky-500/20';
    return 'bg-emerald-500/10 text-emerald-600 border border-emerald-500/20';
  };

  return (
    <div className="page-bg flex flex-col min-h-screen">
      <Navbar currentPage="app" onNavigate={onNavigate} />

      <main className="page-container flex-1 space-y-10 py-12">
        {/* Header Section */}
        <motion.section {...fadeUp(0)} className="space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-semibold feature-pill">
            <Terminal className="w-3.5 h-3.5 text-[var(--accent-ink)] dark:text-[var(--accent)]" />
            STATIC CODE ANALYZER
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">Security & Quality Scanner</h1>
          <p className="text-sm text-[var(--muted)] leading-relaxed max-w-2xl">
            Inspect Python source code for security vulnerabilities, rule violations, and syntax concerns in real time using Abstract Syntax Tree parsing.
          </p>
        </motion.section>

        {/* Workbench Card */}
        <motion.div {...fadeUp(0.05)} className="analysis-workbench p-6 sm:p-8 space-y-6">
          {/* Mode Switcher Tabs */}
          <div className="flex border-b border-[var(--line)]">
            <button
              onClick={() => { setActiveTab('snippet'); setError(null); }}
              className={`px-4 py-2.5 text-xs font-mono font-bold transition-all border-b-2 -mb-px ${
                activeTab === 'snippet'
                  ? 'border-[var(--accent)] text-[var(--ink)] bg-[var(--surface-raised)] rounded-t-lg'
                  : 'border-transparent text-[var(--muted)] hover:text-[var(--ink)]'
              }`}
            >
              Code Snippet
            </button>
            <button
              onClick={() => { setActiveTab('file'); setError(null); }}
              className={`px-4 py-2.5 text-xs font-mono font-bold transition-all border-b-2 -mb-px ${
                activeTab === 'file'
                  ? 'border-[var(--accent)] text-[var(--ink)] bg-[var(--surface-raised)] rounded-t-lg'
                  : 'border-transparent text-[var(--muted)] hover:text-[var(--ink)]'
              }`}
            >
              File Upload (.py)
            </button>
          </div>

          {error && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs flex items-center gap-2 font-mono">
              <XCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Snippet Form */}
          {activeTab === 'snippet' ? (
            <form onSubmit={handleSnippetScan} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-mono font-bold uppercase tracking-wider text-[var(--muted)] block">
                  Python Source Code
                </label>
                <textarea
                  value={codeSnippet}
                  onChange={(e) => setCodeSnippet(e.target.value)}
                  placeholder="def authenticate(user_password):&#10;    query = f&quot;SELECT * FROM users WHERE password = '{user_password}'&quot;&#10;    cursor.execute(query)"
                  className="code-input w-full p-4 text-xs font-mono rounded-xl focus:outline-none"
                  rows={8}
                />
              </div>

              <div className="flex items-center justify-between pt-2">
                <span className="text-xs font-mono text-[var(--muted)]">
                  {codeSnippet.split('\n').length} lines | {codeSnippet.length} characters
                </span>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-3 rounded-full text-sm font-bold btn-primary shadow-lg transition-all inline-flex items-center gap-2 disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Terminal className="w-4 h-4" />
                      Run Analysis
                    </>
                  )}
                </button>
              </div>
            </form>
          ) : (
            /* File Upload Form */
            <form onSubmit={handleFileScan} className="space-y-4">
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`drop-zone p-8 sm:p-12 text-center cursor-pointer flex flex-col items-center justify-center space-y-3 ${
                  dragActive ? 'drop-zone-active' : ''
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".py"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="hidden"
                />
                <div className="w-12 h-12 rounded-full accent-bg flex items-center justify-center">
                  <Upload className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-sm font-bold">
                    {selectedFile ? selectedFile.name : 'Click to select Python file or drag & drop'}
                  </p>
                  <p className="text-xs text-[var(--muted)] mt-1 font-mono">Supports .py files up to 2MB</p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2">
                <span className="text-xs font-mono text-[var(--muted)]">
                  {selectedFile ? `Selected: ${selectedFile.name} (${(selectedFile.size / 1024).toFixed(1)} KB)` : 'No file chosen'}
                </span>
                <button
                  type="submit"
                  disabled={loading || !selectedFile}
                  className="px-6 py-3 rounded-full text-sm font-bold btn-primary shadow-lg transition-all inline-flex items-center gap-2 disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Scanning File...
                    </>
                  ) : (
                    <>
                      <FileCode className="w-4 h-4" />
                      Scan File
                    </>
                  )}
                </button>
              </div>
            </form>
          )}
        </motion.div>

        {/* Results Report Section */}
        <AnimatePresence>
          {report && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="analysis-report p-6 sm:p-8 space-y-6"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[var(--line)]">
                <div>
                  <div className="flex items-center gap-2 font-mono text-xs text-[var(--muted)] mb-1">
                    <span>Report ID: {report.report_id || report.id || 'SEC-SCAN-01'}</span>
                    <span>•</span>
                    <span>{report.filename || 'source.py'}</span>
                  </div>
                  <h2 className="text-xl sm:text-2xl font-bold">Analysis Results</h2>
                </div>

                {report.report_id && (
                  <a
                    href={getReportDownloadUrl(report.report_id)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2.5 rounded-full text-xs font-bold btn-secondary inline-flex items-center gap-2 self-start sm:self-auto"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Download PDF Report
                  </a>
                )}
              </div>

              {/* Summary Stats Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl stat-card-red space-y-1">
                  <span className="text-[10px] font-mono font-bold uppercase text-[var(--muted)]">Critical / High</span>
                  <p className="text-2xl font-black">{report.summary?.critical || report.critical_count || 0}</p>
                </div>
                <div className="p-4 rounded-xl stat-card-amber space-y-1">
                  <span className="text-[10px] font-mono font-bold uppercase text-[var(--muted)]">Medium Risk</span>
                  <p className="text-2xl font-black">{report.summary?.medium || report.medium_count || 0}</p>
                </div>
                <div className="p-4 rounded-xl stat-card-teal space-y-1">
                  <span className="text-[10px] font-mono font-bold uppercase text-[var(--muted)]">Low / Quality</span>
                  <p className="text-2xl font-black">{report.summary?.low || report.low_count || 0}</p>
                </div>
                <div className="p-4 rounded-xl glass-panel space-y-1">
                  <span className="text-[10px] font-mono font-bold uppercase text-[var(--muted)]">Total Issues</span>
                  <p className="text-2xl font-black">{report.issues?.length || report.total_issues || 0}</p>
                </div>
              </div>

              {/* Issues List */}
              <div className="space-y-3 pt-2">
                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[var(--muted)]">Detailed Findings</h3>
                {report.issues && report.issues.length > 0 ? (
                  <div className="space-y-3">
                    {report.issues.map((issue, idx) => (
                      <div key={idx} className="p-4 rounded-xl bg-[var(--surface-raised)] border border-[var(--line)] space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${getSeverityBadge(issue.severity)}`}>
                              {issue.severity || 'Warning'}
                            </span>
                            <span className="font-mono text-xs font-bold">Line {issue.line || 'N/A'}: {issue.title || issue.rule_id}</span>
                          </div>
                          <span className="text-xs font-mono text-[var(--muted)]">{issue.category || 'Security'}</span>
                        </div>
                        <p className="text-xs text-[var(--muted)] leading-relaxed">{issue.description || issue.message}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-8 rounded-xl bg-[var(--surface-raised)] border border-[var(--line)] text-center space-y-2">
                    <ShieldCheck className="w-8 h-8 text-emerald-500 mx-auto" />
                    <p className="text-sm font-bold">No security vulnerabilities or quality issues detected!</p>
                    <p className="text-xs text-[var(--muted)]">Your code passed all AST static analysis checks cleanly.</p>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <Footer />
    </div>
  );
}