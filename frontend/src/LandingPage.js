import React from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css';

const features = [
  ['01', 'Security checks', 'Look for patterns such as hardcoded credentials, dynamic execution, weak hashes, and injection-prone code.', 'PATTERN MATCHING', '⌕'],
  ['02', 'AST and code quality', 'Parse Python syntax and surface maintainability concerns such as mutable defaults and bare exception handlers.', 'PYTHON SOURCE', '{ }'],
  ['03', 'Safe analysis', 'Inspect source as text and parse its syntax. Submitted Python is not imported or executed by the scanner.', 'NO CODE EXECUTION', '◉'],
  ['04', 'Useful reports', 'Review results in text or JSON, and create a professional PDF report with findings and recommendations.', 'TEXT · JSON · PDF', '⌤'],
  ['05', 'Cloud Web Platform', 'Access SecureCode instantly via the browser to scan code snippets or uploaded files on the fly.', 'SAAS PLATFORM', '☁'],
  ['06', 'Portable CLI Tool', 'Download the standalone CLI package to recursively scan entire local projects and directories.', 'CLI PACKAGE', '$'],
];

const samples = [
  ['CRITICAL', 'dynamic execution', 'result = eval(user_input)', 'Dynamic evaluation can execute an unintended expression.'],
  ['HIGH', 'command injection', 'os.system(command)', 'Passing untrusted values to a system command can be dangerous.'],
  ['MEDIUM', 'debug configuration', 'DEBUG = True', 'Debug mode should not be enabled in a production deployment.'],
  ['LOW', 'quality signal', 'except:', 'A bare exception handler can hide unexpected failures.'],
];

function LandingPage() {
  return (
    <div id="landing-page" className="landing-page">
      <a className="skip-link" href="#main">Skip to content</a>
      <header className="landing-header">
        <a className="brand" href="#top" aria-label="SecureCode home">
          <span className="brand-mark" aria-hidden="true">S</span>
          <span>SecureCode<small>PYTHON STATIC ANALYSIS</small></span>
        </a>
        <nav aria-label="Main navigation">
          <a href="#features">Features</a>
          <a href="#how-it-works">How it works</a>
          <a href="#samples">Sample scans</a>
          <a href="#docs">Docs</a>
          <a href="#security">Security</a>
        </nav>
        <Link className="header-link" to="/app">Launch App <span aria-hidden="true">↗</span></Link>
      </header>

      <main id="main">
        <section className="hero" id="top" aria-labelledby="hero-title">
          <div className="hero-copy">
            <p className="eyebrow"><span className="pulse-dot" aria-hidden="true" />CLOUD SAAS & PORTABLE CLI ANALYZER</p>
            <h1 id="hero-title">SecureCode</h1>
            <p className="hero-subtitle">Python Static Security & Quality Scanner</p>
            <p className="hero-lede">Make risky code easier to spot. SecureCode checks Python source for security patterns, syntax problems, and code-quality issues. Use the web platform instantly or download the standalone CLI for local project scans.</p>
            <div className="hero-actions">
              <Link className="button button-primary" to="/app">Launch App <span aria-hidden="true">↗</span></Link>
              <a className="button button-secondary" href="https://github.com/stardustpelt/secure-code/releases/latest/download/securecode-cli.zip">Download CLI <span aria-hidden="true">↓</span></a>
            </div>
            <div className="hero-facts" aria-label="Project characteristics">
              <span>Python source</span><span>Web & CLI</span><span>No code execution</span>
            </div>
          </div>
          <div className="hero-panel" aria-label="Illustrative SecureCode finding">
            <div className="panel-top"><span className="window-lights" aria-hidden="true"><i /><i /><i /></span><span>example_scan.py</span><span className="panel-state">STATIC CHECK</span></div>
            <div className="code-preview" aria-label="Example code displaying a possible SQL injection pattern">
              <span className="line-numbers" aria-hidden="true">08<br />09</span>
              <pre><span className="code-keyword">def</span> lookup_user(user_id):{'\n'}    cursor.execute(<span className="code-string">"SELECT * FROM users WHERE id = "</span> <span className="code-risk">+ user_id</span>)</pre>
            </div>
            <div className="sample-finding"><span className="severity severity-high">HIGH</span><span>Possible SQL injection</span><span className="finding-location">L09</span></div>
            <div className="panel-bottom"><span><i aria-hidden="true" /> Example output</span><span>Source is read, not run</span></div>
            <div className="panel-stamp" aria-hidden="true">READ<br />DON&apos;T RUN</div>
          </div>
          <a className="hero-scroll" href="#features"><span>01</span> Explore SecureCode <span aria-hidden="true">↓</span></a>
        </section>

        <section className="section features" id="features" aria-labelledby="features-title">
          <div className="section-heading">
            <p className="eyebrow">01 / FEATURES</p>
            <h2 id="features-title">A practical first pass<br />for Python projects.</h2>
            <p>Flexible tooling that makes common security and quality issues visible across web and CLI workflows.</p>
          </div>
          <div className="feature-grid">
            {features.map(([number, title, description, label, icon]) => (
              <article className="feature-card" key={number}>
                <span className="feature-index">{number}</span><span className="feature-icon" aria-hidden="true">{icon}</span>
                <h3>{title}</h3><p>{description}</p><span className="feature-label">{label}</span>
              </article>
            ))}
          </div>
          <p className="fine-print"><strong>Scope note:</strong> Security checks are heuristic. A clean scan is not proof that code is secure, and findings may include false positives.</p>
        </section>

        <section className="how-section" id="how-it-works" aria-labelledby="how-title">
          <div className="how-inner">
            <div className="section-heading section-heading-dark">
              <p className="eyebrow">02 / HOW IT WORKS</p>
              <h2 id="how-title">Choose your workflow.<br />Web SaaS or CLI.</h2>
              <p>Analyze code instantly on the web platform or run recursive scans locally using the standalone CLI package.</p>
            </div>
            <div className="steps">
              <article className="step">
                <span className="step-number">01</span>
                <div className="step-symbol" aria-hidden="true">☁</div>
                <h3>Use the Web Platform</h3>
                <p>Paste snippets or upload files for instant AST analysis and immediate PDF report generation.</p>
                <pre><code># Launch web app{'\n'}/app</code></pre>
              </article>
              <span className="step-arrow" aria-hidden="true">→</span>
              <article className="step">
                <span className="step-number">02</span>
                <div className="step-symbol" aria-hidden="true">↓</div>
                <h3>Download the CLI</h3>
                <p>Grab the portable bundle from GitHub Releases for recursive offline project scanning.</p>
                <pre><code># Unzip and install reqs{'\n'}pip install -r requirements.txt</code></pre>
              </article>
              <span className="step-arrow" aria-hidden="true">→</span>
              <article className="step">
                <span className="step-number">03</span>
                <div className="step-symbol" aria-hidden="true">⌤</div>
                <h3>Export Reports</h3>
                <p>Generate professional PDF, JSON, or text audit reports for your codebase.</p>
                <pre><code>python3 cli.py ./project -o report.pdf</code></pre>
              </article>
            </div>
            <p className="platform-note">The standalone CLI requires Python 3 and ReportLab. Visit the docs or GitHub for complete usage guidelines.</p>
          </div>
        </section>

        <section className="section samples" id="samples" aria-labelledby="samples-title">
          <div className="section-heading">
            <p className="eyebrow">03 / SAMPLE SCANS</p>
            <h2 id="samples-title">Patterns worth a closer look.</h2>
            <p>Illustrative snippets based on scanner rules and repository samples. These cards are examples, not live scans.</p>
          </div>
          <div className="sample-grid">
            {samples.map(([severity, label, code, description]) => (
              <article className="sample-card" key={label}>
                <div className="sample-card-head"><span className={`severity severity-${severity.toLowerCase()}`}>{severity}</span><span>{label}</span></div>
                <pre><code>{code}</code></pre><p>{description}</p>
              </article>
            ))}
          </div>
          <p className="sample-disclaimer">These snippets are displayed as text only. They are not executed by this website.</p>
        </section>

        <section className="section docs-section" id="docs" aria-labelledby="docs-title">
          <div className="section-heading">
            <p className="eyebrow">04 / DOCUMENTATION</p>
            <h2 id="docs-title">Keep exploring.</h2>
            <p>Project guides, API references, and CLI instructions live alongside the source on GitHub.</p>
          </div>
          <div className="docs-links">
            <a href="https://github.com/stardustpelt/secure-code/releases/latest/download/securecode-cli.zip"><span>01</span><strong>CLI Package</strong><small>Download standalone zip</small><b aria-hidden="true">↓</b></a>
            <a href="https://github.com/stardustpelt/secure-code" target="_blank" rel="noopener noreferrer"><span>02</span><strong>Repository</strong><small>View source code & rules</small><b aria-hidden="true">↗</b></a>
            <a href="https://github.com/stardustpelt/secure-code/tree/main/docs" target="_blank" rel="noopener noreferrer"><span>03</span><strong>Guides</strong><small>Scan files and folders</small><b aria-hidden="true">↗</b></a>
          </div>
        </section>

        <section className="security-section" id="security" aria-labelledby="security-title">
          <div className="security-icon" aria-hidden="true">!</div>
          <div><p className="eyebrow">05 / SECURITY NOTICE</p><h2 id="security-title">Use responsibly. Review every result.</h2><p>SecureCode is an educational project for authorized use. Scan only code you own or have permission to analyze. Static analysis can miss vulnerabilities and report false positives; it is not a substitute for a professional security review.</p></div>
        </section>

        <section className="closing-cta" aria-labelledby="launch-title">
          <div><p className="eyebrow">READY TO TAKE A LOOK?</p><h2 id="launch-title">Start scanning your Python code.</h2><p>Launch the web application or download the CLI toolkit to get started.</p></div>
          <Link className="button button-dark" to="/app">Launch the scanner <span aria-hidden="true">↗</span></Link>
        </section>
      </main>

      <footer className="landing-footer">
        <a className="brand" href="#top"><span className="brand-mark" aria-hidden="true">S</span><span>SecureCode<small>PYTHON STATIC ANALYSIS</small></span></a>
        <p>Final Year Project · Cyber Security</p>
        <a href="https://github.com/stardustpelt/secure-code" target="_blank" rel="noopener noreferrer">GitHub <span aria-hidden="true">↗</span></a>
      </footer>
    </div>
  );
}

export default LandingPage;