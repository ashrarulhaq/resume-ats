import React, { useState } from 'react';
import './ResumeUploader.css';

const ResumeUploader = ({ onFileUpload, originalText }) => {
  const [expanded, setExpanded] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onFileUpload(file);
    }
  };

  return (
    <div className="resume-uploader">
      <h2>Step 1: Upload Resume</h2>
      
      <div className="upload-section">
        <input
          type="file"
          id="resume-upload"
          accept=".pdf,.docx,.txt"
          onChange={handleFileChange}
        />
        <label htmlFor="resume-upload">
          Choose your resume file
          <span className="file-info">(PDF, DOCX, or TXT, max 10MB)</span>
        </label>
      </div>
      
      {originalText && (
        <>
          <div className="success">
            ✅ Extracted {originalText.length} characters from resume
          </div>
          
          <div className="expandable-section">
            <button className="toggle-btn" onClick={() => setExpanded(!expanded)}>
              {expanded ? 'Hide extracted text' : 'View extracted text'}
            </button>
            <div className={`expander-content ${expanded ? 'expanded' : ''}`}>
              <textarea
                readOnly
                value={originalText}
                aria-label="Extracted resume text"
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ResumeUploader;
