import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldCheck, Upload, Play, Download, FileCode, AlertTriangle,
  CheckCircle, RotateCcw, Zap, Lock, Bug, AlertCircle, ChevronRight
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import './index.css';
import Documentation from './Documentation';
import About from './About';
import Layout from './components/Layout';

const API_BASE = 'http://127.0.0.1:8000/api';

function SeverityBadge({ level }) {
  const map = {
    critical: 'badge-critical',
    high:     'badge-high',
    medium:   'badge-medium',
    low:      'badge-low',
  };
  const cls = map[level?.toLowerCase()] || 'badge-low';
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wide ${cls}`}>
      {level || 'LOW'}
    </span>
  );
}

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [code, setCode] = useState('');
  const [file, setFile] = useState(null);
  const [activeTab, setActiveTab] = useState('paste');
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState(null);
  const [reportId, setReportId] = useState(null);
  const [showAlert, setShowAlert] = useState(false);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'text/x-python': ['.py'] },
    maxFiles: 1,
    onDrop: (files) => files.length > 0 && setFile(files[0]),
  });

  if (currentPage === 'docs')  return <Documentation onNavigate={setCurrentPage} />;
  if (currentPage === 'about') return <About onNavigate={setCurrentPage} />;

  const resetForm = () => { setCode(''); setFile(null); setReport(null); setReportId(null); };

  const analyzeCode = async () => {
    if (!code && !file) {
      setShowAlert(true);
      setTimeout(() => setShowAlert(false), 3000);
      return;
    }
    setAnalyzing(true);
    setReport(null);
    setReportId(null);
    try {
      let response;
      if (file) {
        const fd = new FormData();
        fd.append('file', file);
        response = await fetch(`${API_BASE}/analyze/`, { method: 'POST', body: fd });
      } else {
        response = await fetch(`${API_BASE}/analyze/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code, filename: 'web_code' }),
        });
      }
      const result = await response.json();
      setReport(result);
      setReportId(result.report_id);
    } catch (err) {
      setReport({
        status: 'error', has_errors: true,
        report: `Connection failed. Make sure the server is running:\npython3 manage.py runserver 127.0.0.1:8000\n\nError: ${err.message}`,
      });
    } finally {
      setAnalyzing(false);
    }
  };

  const downloadReport = () => {
    if (reportId) window.location.href = `${API_BASE}/report/${reportId}/?download=true`;
  };

  const getSeverityStats = () => {
    if (!report?.errors) return { critical: 0, high: 0, medium: 0, low: 0 };
    return report.errors.reduce((acc, e) => {
      const s = e.severity?.toLowerCase() || 'low';
      if (s === 'critical') acc.critical++;
      else if (s === 'high') acc.high++;
      else if (s === 'medium') acc.medium++;
      else acc.low++;
      return acc;
    }, { critical: 0, high: 0, medium: 0, low: 0 });
  };

  const stats = getSeverityStats();

  return (
    <Layout currentPage={currentPage} onNavigate={setCurrentPage}>

      {/* Alert toast */}
      <AnimatePresence>
        {showAlert && (
          <motion.div
            initial={{ opacity: 0, y: -16, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -16, scale: 0.95 }}
            className="fixed top-20 left-1/2 -translate-x-1/2 z-50"
          >
            <div className="flex items-center gap-3 bg-red-600 text-white px-5 py-3 rounded-xl shadow-2xl text-sm font-medium">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              Please paste code or upload a Python file
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Hero ── */}
      <motion.section
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="analyzer-intro mb-10"
      >
        <div className="intro-layout flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div className="intro-copy">
            <div className="flex items-center gap-2 mb-2">
              <span className="feature-pill text-xs font-semibold px-2.5 py-1 rounded-full flex items-center gap-1.5">
                <Zap size={11} /> Static Analysis Engine
              </span>
            </div>
            <h1 className="text-4xl sm:text-5xl font-extrabold hero-title tracking-tight leading-none mb-3">
              SecureCode
            </h1>
            <p className="text-slate-600 dark:text-slate-400 text-base sm:text-lg max-w-lg">
              Run local checks for recognizable security patterns, syntax problems, and code-quality issues in Python.
            </p>
          </div>
          <div className="intro-facts flex flex-col gap-2 text-sm">
            {[
              { icon: Lock, label: 'Selected Security Checks' },
              { icon: Bug, label: 'Heuristic Severity Levels' },
              { icon: ShieldCheck, label: 'PDF Report Export' },
            ].map(({ icon: Icon, label }) => (
              <div key={label} className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                <Icon size={14} className="text-teal-600 dark:text-teal-400 flex-shrink-0" />
                <span>{label}</span>
              </div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* ── Input Panel ── */}
      <motion.section
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="glass-panel analysis-workbench rounded-2xl p-5 sm:p-7 mb-6"
      >
        {/* Tabs */}
        <div className="mode-tabs flex gap-1 mb-5 bg-slate-100 dark:bg-slate-800/60 rounded-xl p-1 w-fit" role="tablist" aria-label="Code input method">
          {[
            { id: 'paste', icon: FileCode, label: 'Paste Code' },
            { id: 'upload', icon: Upload, label: 'Upload File' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              role="tab"
              aria-selected={activeTab === tab.id}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-white dark:bg-slate-700 text-teal-700 dark:text-teal-300 shadow-sm'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
              }`}
            >
              <tab.icon size={14} />
              {tab.label}
            </button>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {activeTab === 'paste' ? (
            <motion.div key="paste" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  Python Source
                </label>
                {code && (
                  <span className="text-xs text-slate-400 dark:text-slate-500">
                    {code.split('\n').length} lines
                  </span>
                )}
              </div>
              <textarea
                value={code}
                onChange={e => setCode(e.target.value)}
                placeholder={"def hello_world():\n    print('Hello, World!')"}
                className="code-input w-full h-52 sm:h-64 rounded-xl p-4 text-sm resize-none leading-relaxed"
              />
            </motion.div>
          ) : (
            <motion.div key="upload" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <label className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider block mb-2">
                Python File
              </label>
              <div
                {...getRootProps()}
                className={`drop-zone rounded-xl p-10 sm:p-14 text-center cursor-pointer ${isDragActive ? 'drop-zone-active' : ''}`}
              >
                <input {...getInputProps()} />
                <div className={`w-12 h-12 rounded-xl mx-auto mb-4 flex items-center justify-center ${isDragActive ? 'btn-primary' : 'bg-slate-100 dark:bg-slate-800'}`}>
                  <Upload size={22} className={isDragActive ? 'text-white' : 'text-slate-400 dark:text-slate-500'} />
                </div>
                {file ? (
                  <div>
                    <p className="font-semibold text-teal-700 dark:text-teal-300 text-sm break-all">{file.name}</p>
                    <p className="text-xs text-slate-400 mt-1">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                ) : (
                  <div>
                    <p className="text-slate-600 dark:text-slate-400 text-sm font-medium mb-1">
                      {isDragActive ? 'Drop it here' : 'Drag & drop your .py file'}
                    </p>
                    <p className="text-xs text-slate-400 dark:text-slate-500">or click to browse</p>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Action buttons */}
        <div className="analysis-actions flex gap-3 mt-5">
          <motion.button
            whileHover={{ scale: analyzing ? 1 : 1.01 }}
            whileTap={{ scale: analyzing ? 1 : 0.98 }}
            onClick={analyzeCode}
            disabled={analyzing}
            className="flex-1 btn-primary py-3 rounded-xl font-semibold text-sm flex items-center justify-center gap-2.5 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {analyzing ? (
              <>
                <motion.div animate={{ rotate: 360 }} transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}>
                  <Play size={16} />
                </motion.div>
                Analyzing...
              </>
            ) : (
              <>
                <Play size={16} />
                Run Analysis
                <ChevronRight size={14} className="opacity-70" />
              </>
            )}
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.98 }}
            onClick={resetForm}
            className="btn-secondary py-3 px-5 rounded-xl font-medium text-sm flex items-center gap-2"
          >
            <RotateCcw size={14} />
            <span className="hidden sm:inline">Reset</span>
          </motion.button>
        </div>
      </motion.section>

      {/* ── Report ── */}
      <AnimatePresence>
        {report && (
          <motion.section
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -24 }}
            transition={{ type: 'spring', damping: 22, stiffness: 200 }}
            className="glass-panel analysis-report rounded-2xl p-5 sm:p-7"
          >
            {/* Report header */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
              <div className="flex items-center gap-3">
                {report.has_errors ? (
                  <div className="w-10 h-10 rounded-xl bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                    <AlertTriangle size={20} className="text-red-600 dark:text-red-400" />
                  </div>
                ) : (
                  <div className="w-10 h-10 rounded-xl bg-teal-100 dark:bg-teal-900/30 flex items-center justify-center">
                    <CheckCircle size={20} className="text-teal-600 dark:text-teal-400" />
                  </div>
                )}
                <div>
                    <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">
                    {report.has_errors ? 'Issues Detected' : 'No Findings Detected'}
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {report.has_errors
                      ? `${report.error_count} issue${report.error_count !== 1 ? 's' : ''} found`
                      : 'The current checks did not flag any issues'}
                  </p>
                </div>
              </div>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.97 }}
                onClick={downloadReport}
                disabled={!reportId}
                className="btn-success px-5 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download size={15} />
                Download PDF
              </motion.button>
            </div>

            {/* Severity stats */}
            {report.has_errors && report.errors && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
                {[
                  { label: 'Critical', value: stats.critical, cls: 'stat-card-red', textCls: 'text-red-600 dark:text-red-400' },
                  { label: 'High',     value: stats.high,     cls: 'stat-card-red', textCls: 'text-orange-600 dark:text-orange-400' },
                  { label: 'Medium',   value: stats.medium,   cls: 'stat-card-amber', textCls: 'text-amber-600 dark:text-amber-400' },
                  { label: 'Low',      value: stats.low,      cls: 'stat-card-teal', textCls: 'text-teal-600 dark:text-teal-400' },
                ].map((s, i) => (
                  <motion.div
                    key={s.label}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.07 }}
                    className={`${s.cls} rounded-xl p-4`}
                  >
                    <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">{s.label}</p>
                    <p className={`text-3xl font-extrabold ${s.textCls}`}>{s.value}</p>
                  </motion.div>
                ))}
              </div>
            )}

            {/* Issues list */}
            {report.has_errors && report.errors && (
              <div className="mb-6 space-y-2">
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">
                  Issue Breakdown
                </p>
                {report.errors.slice(0, 8).map((err, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.04 }}
                    className="info-card rounded-lg px-4 py-3 flex items-start gap-3"
                  >
                    <span className="text-xs text-slate-400 dark:text-slate-500 font-mono mt-0.5 w-6 flex-shrink-0">
                      L{err.line}
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-0.5">
                        <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 truncate">{err.type}</span>
                        <SeverityBadge level={err.severity} />
                      </div>
                      <p className="text-xs text-slate-500 dark:text-slate-400 truncate">{err.message}</p>
                    </div>
                  </motion.div>
                ))}
                {report.errors.length > 8 && (
                  <p className="text-xs text-slate-400 dark:text-slate-500 text-center pt-1">
                    + {report.errors.length - 8} more issues in the full report
                  </p>
                )}
              </div>
            )}

            {/* Raw report */}
            <div>
              <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
                Full Report
              </p>
              <div className="report-output rounded-xl p-4 sm:p-5 overflow-auto max-h-80">
                <pre className="text-xs leading-relaxed whitespace-pre-wrap break-words font-mono">
                  {report.report}
                </pre>
              </div>
            </div>
          </motion.section>
        )}
      </AnimatePresence>
    </Layout>
  );
}

export default App;
