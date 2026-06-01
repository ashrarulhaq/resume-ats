import React from 'react';
import './Sidebar.css';

const Sidebar = ({ apiConfig, onApiConfigChange, hasApiKey }) => {
  const handleApiKeyChange = (e) => {
    onApiConfigChange({ ...apiConfig, apiKey: e.target.value });
  };

  const handleModelChange = (e) => {
    onApiConfigChange({ ...apiConfig, model: e.target.value });
  };

  return (
    <div className="sidebar">
      <h2>🔧 OpenRouter Configuration</h2>
      
      <div className="form-group">
        <label htmlFor="api-key">OpenRouter API Key</label>
        <input
          type="password"
          id="api-key"
          value={apiConfig.apiKey}
          onChange={handleApiKeyChange}
          placeholder="Get your API key from https://openrouter.ai/keys"
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="model">Model Name</label>
        <input
          type="text"
          id="model"
          value={apiConfig.model}
          onChange={handleModelChange}
          placeholder="e.g., openrouter/gpt-3.5-turbo"
        />
      </div>
      
      {!hasApiKey && (
        <div className="warning">
          ⚠️ Please enter your OpenRouter API key to continue
        </div>
      )}
      
      {hasApiKey && (
        <div className="success">
          ✅ API Key configured
        </div>
      )}
      
      <div className="hint">
        💡 Get your API key from https://openrouter.ai/keys
      </div>
    </div>
  );
};

export default Sidebar;
