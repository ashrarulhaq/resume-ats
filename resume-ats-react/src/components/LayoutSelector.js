import React from 'react';

const layouts = [
  { id: 1, name: 'Classic', note: 'Single-column and ATS friendly.' },
];

const LayoutSelector = ({ selectedLayout, onLayoutChange }) => {
  return (
    <section className="panel layout-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Step 5</p>
          <h2>Choose a layout</h2>
        </div>
      </div>

      <div className="layout-grid">
        {layouts.map((layout) => (
          <button
            key={layout.id}
            className={`layout-card ${selectedLayout === layout.id ? 'active' : ''}`}
            onClick={() => onLayoutChange(layout.id)}
            type="button"
          >
            <span className="layout-number">0{layout.id}</span>
            <strong>{layout.name}</strong>
            <span className="layout-note">{layout.note}</span>
          </button>
        ))}
      </div>
    </section>
  );
};

export default LayoutSelector;
