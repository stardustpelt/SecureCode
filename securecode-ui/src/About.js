import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, Target, Code2, CheckCircle, Users, Zap, GitBranch, Cpu } from 'lucide-react';
import Layout from './components/Layout';

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.45, delay },
});

function About({ onNavigate }) {
  return (
    <Layout currentPage="about" onNavigate={onNavigate}>
      <div className="max-w-4xl mx-auto">

        {/* Page title */}
        <motion.div {...fadeUp(0)} className="mb-8">
          <div className="flex items-center gap-2 mb-2">
            <span className="feature-pill text-xs font-semibold px-2.5 py-1 rounded-full">About</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold hero-title tracking-tight mb-2">About SecureCode</h1>
          <p className="text-slate-600 dark:text-slate-400 text-base">
            A free, open-source Python security analysis tool built for developers.
          </p>
        </motion.div>

        {/* Mission */}
        <motion.div {...fadeUp(0.05)} className="glass-panel rounded-2xl p-6 sm:p-8 mb-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-9 h-9 rounded-xl btn-primary flex items-center justify-center flex-shrink-0">
              <Target size={17} className="text-white" />
            </div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Mission</h2>
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-3">
            SecureCode was built to make security analysis accessible to every Python developer — not just security engineers.
            The web interface is for quick checks of a pasted snippet or one Python file; use the full CLI for project-folder scans.
          </p>
          <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
            By combining security and quality patterns with AST parsing, SecureCode reports findings and recommendations
            without executing submitted code.
          </p>
        </motion.div>

        {/* Philosophy */}
        <motion.div {...fadeUp(0.075)} className="glass-panel rounded-2xl p-6 sm:p-8 mb-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-9 h-9 rounded-xl btn-primary flex items-center justify-center flex-shrink-0">
              <ShieldCheck size={17} className="text-white" />
            </div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Philosophy</h2>
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-5">
            SecureCode is built on a local-first, education-focused philosophy that prioritizes developer privacy and learning over comprehensive coverage.
          </p>

          <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200 mb-3">Core Principles</h3>
          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3 mb-6">
            {[
              ['🏠', 'Local-first', 'Analysis runs on your machine at 127.0.0.1:8000; source is not uploaded by the local setup.'],
              ['🔒', 'No execution', 'The full analysis APIs and CLI inspect code without running it.'],
              ['📚', 'Educational', 'Findings include explanations and recommendations to support learning.'],
              ['🔓', 'Transparent', 'Open-source rules can be inspected and reviewed.'],
              ['🆓', 'Free for all', 'Available to students, independent developers, educators, and teams.'],
            ].map(([emoji, title, description]) => (
              <li key={title} className="flex items-start gap-3 text-sm text-slate-600 dark:text-slate-400">
                <span className="text-lg leading-none" aria-hidden="true">{emoji}</span>
                <span><strong className="font-semibold text-slate-800 dark:text-slate-200">{title}</strong> — {description}</span>
              </li>
            ))}
          </ul>

          <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200 mb-3">How It Differs from Enterprise SAST</h3>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[520px] border-collapse text-left text-xs sm:text-sm">
              <thead>
                <tr className="border-b border-slate-300 dark:border-slate-700">
                  <th className="py-2 pr-3 font-semibold text-slate-700 dark:text-slate-300">Aspect</th>
                  <th className="py-2 px-3 font-semibold text-slate-700 dark:text-slate-300">Typical enterprise tools</th>
                  <th className="py-2 pl-3 font-semibold text-slate-700 dark:text-slate-300">SecureCode</th>
                </tr>
              </thead>
              <tbody className="text-slate-600 dark:text-slate-400">
                {[
                  ['Analysis location', 'Cloud service or larger self-hosted setup', 'Runs locally'],
                  ['Code privacy', 'Depends on product and configuration', 'Local setup keeps code on your machine'],
                  ['Code execution', 'Depends on product and configuration', 'Not executed'],
                  ['Primary audience', 'Security teams and organizations', 'Individual developers, students, and educators'],
                  ['Focus', 'Broad coverage, workflows, and compliance', 'Privacy, learning, and quick local checks'],
                  ['Pricing', 'Varies by product and plan', 'Free and open source'],
                ].map(([aspect, enterprise, secureCode]) => (
                  <tr key={aspect} className="border-b border-slate-200 dark:border-slate-800 last:border-0">
                    <th scope="row" className="py-2 pr-3 font-medium text-slate-700 dark:text-slate-300">{aspect}</th>
                    <td className="py-2 px-3">{enterprise}</td>
                    <td className="py-2 pl-3">{secureCode}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200 mt-6 mb-3">Why Local-first Matters</h3>
          <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-3">
            Developers increasingly value keeping proprietary code private, avoiding upload latency, working offline, and using tools whose rules they can audit.
          </p>
          <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-2">SecureCode is designed for:</p>
          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-slate-600 dark:text-slate-400">
            <li>🎓 Students learning security</li>
            <li>👨‍💻 Independent developers with side projects</li>
            <li>🔒 Privacy-conscious teams</li>
            <li>🏫 Educators teaching secure coding</li>
          </ul>
        </motion.div>

        {/* Why */}
        <motion.div {...fadeUp(0.1)} className="glass-panel rounded-2xl p-6 sm:p-8 mb-5">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-9 h-9 rounded-xl btn-primary flex items-center justify-center flex-shrink-0">
              <ShieldCheck size={17} className="text-white" />
            </div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Why We Built This</h2>
          </div>
          <div className="space-y-4">
            {[
              {
                icon: CheckCircle,
                title: 'Security is Non-Negotiable',
                desc: 'Most vulnerabilities — SQL injection, hardcoded secrets, command injection — are preventable with early detection.',
              },
              {
                icon: Users,
                title: 'Free for Everyone',
                desc: 'Enterprise security tools are expensive. SecureCode gives every developer access to the same quality of analysis.',
              },
              {
                icon: Zap,
                title: 'Instant Feedback',
                desc: 'Manual code reviews take hours. SecureCode gives you results in seconds, keeping your workflow fast.',
              },
            ].map(({ icon: Icon, title, desc }) => (
              <div key={title} className="flex items-start gap-4">
                <div className="w-8 h-8 rounded-lg bg-teal-50 dark:bg-teal-900/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Icon size={15} className="text-teal-600 dark:text-teal-400" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200 mb-0.5">{title}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Tech Stack */}
        <motion.div {...fadeUp(0.15)} className="glass-panel rounded-2xl p-6 sm:p-8 mb-5">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-9 h-9 rounded-xl btn-primary flex items-center justify-center flex-shrink-0">
              <Code2 size={17} className="text-white" />
            </div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Tech Stack</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {[
              {
                icon: Cpu,
                title: 'Backend',
                items: ['Python 3.x', 'Django', 'AST Parser', 'Regex Pattern Engine', 'ReportLab (PDF)'],
              },
              {
                icon: GitBranch,
                title: 'Frontend',
                items: ['React 19', 'Tailwind CSS', 'Framer Motion', 'Lucide Icons', 'React Dropzone'],
              },
            ].map(({ icon: Icon, title, items }) => (
              <div key={title} className="info-card rounded-xl p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Icon size={14} className="text-teal-600 dark:text-teal-400" />
                  <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">{title}</h3>
                </div>
                <ul className="space-y-1.5">
                  {items.map(item => (
                    <li key={item} className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400">
                      <span className="w-1 h-1 rounded-full bg-teal-500 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Process */}
        <motion.div {...fadeUp(0.2)} className="glass-panel rounded-2xl p-6 sm:p-8 mb-5">
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 mb-5">How It Works</h2>
          <div className="space-y-4">
            {[
              { n: '01', title: 'Submit Code', desc: 'Paste a snippet or upload one .py file in the web UI; use the CLI to scan folders.' },
              { n: '02', title: 'No Code Execution', desc: 'Submitted source is parsed and checked; it is never run by the full analysis APIs.' },
              { n: '03', title: 'Pattern Matching', desc: 'Security and code-quality patterns check for secrets, injection risks, weak crypto, and more.' },
              { n: '04', title: 'PDF Report', desc: 'A structured PDF report is generated with severity levels, line numbers, and fix recommendations.' },
            ].map(({ n, title, desc }) => (
              <div key={n} className="flex gap-4 items-start">
                <div className="step-num w-9 h-9 rounded-xl flex items-center justify-center text-xs font-bold flex-shrink-0">
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

        {/* Objectives */}
        <motion.div {...fadeUp(0.25)} className="glass-panel rounded-2xl p-6 sm:p-8">
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 mb-5">Project Objectives</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              { emoji: '🎯', title: 'Accessibility', desc: 'Free security analysis for every developer.' },
              { emoji: '🚀', title: 'Integration', desc: 'Web UI, REST API, and CLI for any workflow.' },
              { emoji: '📚', title: 'Education', desc: 'Learn why each issue is dangerous and how to fix it.' },
              { emoji: '⚡', title: 'Performance', desc: 'Fast, accurate results with minimal false positives.' },
            ].map(({ emoji, title, desc }) => (
              <div key={title} className="info-card rounded-xl p-4 flex items-start gap-3">
                <span className="text-xl flex-shrink-0">{emoji}</span>
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-0.5">{title}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

      </div>
    </Layout>
  );
}

export default About;
