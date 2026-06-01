import React from 'react';

const ProcessingSection = ({ onTailorResume, processing, hasInputs }) => {
  return (
    <section className="panel processing-panel">
      <div>
        <p className="eyebrow">Step 3</p>
        <h2>Tailor the resume</h2>
        <p className="panel-copy">
          The backend will rewrite and validate the resume against the job description.
        </p>
      </div>

      <div className="processing-actions">
        <button
          className="primary-button"
          onClick={onTailorResume}
          disabled={!hasInputs || processing}
        >
          {processing ? 'Tailoring...' : 'Tailor Resume'}
        </button>
        {!hasInputs && <span className="helper-text">Upload a resume and add a job description first.</span>}
      </div>
    </section>
  );
};

export default ProcessingSection;
