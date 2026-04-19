import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [status, setStatus] = useState('running');
  const [buildInfo] = useState({
    version: process.env.REACT_APP_VERSION || '1.0.0',
    env: process.env.REACT_APP_ENV || 'development',
    buildTime: new Date().toISOString(),
  });

  useEffect(() => {
    const timer = setTimeout(() => setStatus('healthy'), 1000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>CI/CD Showcase Pipeline</h1>
        <p>Enterprise-grade DevOps demonstration project</p>
        <div className="status-badge" data-testid="status-badge">
          System Status: <span className={`status-${status}`}>{status.toUpperCase()}</span>
        </div>
        <div className="build-info">
          <div className="info-row">
            <span className="label">Version</span>
            <span className="value" data-testid="version">{buildInfo.version}</span>
          </div>
          <div className="info-row">
            <span className="label">Environment</span>
            <span className="value" data-testid="env">{buildInfo.env}</span>
          </div>
          <div className="info-row">
            <span className="label">Build Time</span>
            <span className="value">{buildInfo.buildTime}</span>
          </div>
        </div>
        <div className="pipeline-stages">
          <h2>Pipeline Stages</h2>
          <div className="stages-grid">
            {['Build', 'Test', 'SonarCloud', 'Docker', 'Terraform', 'Deploy'].map((stage) => (
              <div key={stage} className="stage-card">
                <div className="stage-icon">✓</div>
                <div className="stage-name">{stage}</div>
              </div>
            ))}
          </div>
        </div>
      </header>
    </div>
  );
}

export default App;
