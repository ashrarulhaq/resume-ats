import React from 'react';

const renderStatus = (value) => (value ? 'Pass' : 'Review');

const ResultsSection = ({
  keywordScore,
  validationReport,
  originalText,
  tailoredResume,
  tailoredResumeText,
  initialKeywords = [],
  finalKeywords = [],
}) => {
  const score = keywordScore?.score ?? 0;
  const matched = keywordScore?.matched ?? [];
  const missing = keywordScore?.missing ?? [];
  const warnings = validationReport?.warnings ?? [];

  return (
    <section className="results-grid">
      <div className="panel results-panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Step 4</p>
            <h2>Results</h2>
          </div>
          <div className="score-badge">{score}%</div>
        </div>

        <div className="metric-grid">
          <div className="metric-card">
            <span className="metric-label">Skills</span>
            <strong>{renderStatus(validationReport?.skillsValid)}</strong>
          </div>
          <div className="metric-card">
            <span className="metric-label">Dates</span>
            <strong>{renderStatus(validationReport?.datesValid)}</strong>
          </div>
          <div className="metric-card">
            <span className="metric-label">Companies</span>
            <strong>{renderStatus(validationReport?.companiesValid)}</strong>
          </div>
        </div>

        <div className="keyword-section">
          <div>
            <h3>Matched keywords</h3>
            <div className="chip-row">
              {matched.length ? matched.map((item) => <span className="chip success-chip" key={item}>{item}</span>) : <span className="helper-text">None yet.</span>}
            </div>
          </div>
          <div>
            <h3>Missing keywords</h3>
            <div className="chip-row">
              {missing.length ? missing.map((item) => <span className="chip warning-chip" key={item}>{item}</span>) : <span className="helper-text">None.</span>}
            </div>
          </div>
        </div>

        {warnings.length > 0 && (
          <div className="warnings-box">
            <h3>Validation notes</h3>
            <ul>
              {warnings.map((warning) => <li key={warning}>{warning}</li>)}
            </ul>
          </div>
        )}

        <div className="keyword-summary">
          <span>JD keywords extracted: {initialKeywords.length}</span>
          <span>Final keywords: {finalKeywords.length}</span>
        </div>
      </div>

      <div className="panel comparison-panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Review</p>
            <h2>Before and after</h2>
          </div>
        </div>

        <div className="comparison-grid">
          <div>
            <h3>Original</h3>
            <pre className="compare-block">{originalText || 'No resume loaded.'}</pre>
          </div>
          <div>
            <h3>Tailored</h3>
            <pre className="compare-block">{tailoredResumeText || 'No tailored resume yet.'}</pre>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ResultsSection;
