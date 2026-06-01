import React, { useEffect, useState } from 'react';

const PreviewSection = ({ previewHtml, pdfBlob, tailoredResume, onGeneratePDF, onReset }) => {
  const [pdfUrl, setPdfUrl] = useState('');
  const [jsonUrl, setJsonUrl] = useState('');

  useEffect(() => {
    if (!pdfBlob) {
      setPdfUrl('');
      return undefined;
    }

    const url = URL.createObjectURL(pdfBlob);
    setPdfUrl(url);

    return () => {
      URL.revokeObjectURL(url);
    };
  }, [pdfBlob]);

  useEffect(() => {
    if (!tailoredResume) {
      setJsonUrl('');
      return undefined;
    }

    const blob = new Blob([JSON.stringify(tailoredResume, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    setJsonUrl(url);

    return () => {
      URL.revokeObjectURL(url);
    };
  }, [tailoredResume]);

  return (
    <section className="panel preview-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Step 6</p>
          <h2>Preview and export</h2>
        </div>
        <div className="preview-actions">
          <button className="secondary-button" onClick={onReset} type="button">Reset</button>
          <button className="primary-button" onClick={onGeneratePDF} type="button">Generate PDF</button>
        </div>
      </div>

      <div className="preview-frame">
        {previewHtml ? (
          <iframe title="Resume preview" srcDoc={previewHtml} className="preview-iframe" />
        ) : (
          <div className="preview-empty">
            <h3>No preview yet</h3>
            <p>Your layout preview will appear here after tailoring.</p>
          </div>
        )}
      </div>

      {(pdfUrl || jsonUrl) && (
        <div className="download-row">
          {pdfUrl && <a className="download-button" href={pdfUrl} download="tailored_resume.pdf">Download PDF</a>}
          {jsonUrl && <a className="download-button secondary-download" href={jsonUrl} download="tailored_resume.json">Download JSON</a>}
        </div>
      )}
    </section>
  );
};

export default PreviewSection;
