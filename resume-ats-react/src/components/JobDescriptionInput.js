import React from 'react';

const JobDescriptionInput = ({ onJobDescriptionChange, jobDescription, originalText, initialKeywords = [] }) => {
  const charCount = jobDescription.length;
  const overLimit = charCount > 10000;

  return (
    <section className="panel jd-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Step 2</p>
          <h2>Paste the job description</h2>
        </div>
        <span className={`status-pill ${overLimit ? 'danger' : 'muted'}`}>
          {charCount.toLocaleString()}/10,000
        </span>
      </div>

      <textarea
        className="text-input jd-textarea"
        value={jobDescription}
        onChange={(e) => onJobDescriptionChange(e.target.value)}
        placeholder="Paste the full job description here..."
        aria-label="Job description"
      />

      <div className="panel-footer">
        <span className={overLimit ? 'danger-text' : 'helper-text'}>
          {overLimit
            ? 'Job description is too long.'
            : originalText
              ? 'Keep the full posting for the best keyword analysis.'
              : 'Upload a resume first to enable keyword comparison.'}
        </span>
      </div>

      {!!initialKeywords.length && (
        <div className="keyword-cloud">
          <div className="keyword-cloud-label">Extracted keywords</div>
          <div className="chip-row">
            {initialKeywords.slice(0, 12).map((keyword) => (
              <span className="chip" key={keyword}>{keyword}</span>
            ))}
          </div>
        </div>
      )}
    </section>
  );
};

export default JobDescriptionInput;
