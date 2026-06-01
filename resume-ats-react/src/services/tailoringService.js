import { requestJson } from './http';

/**
 * Service for resume tailoring functionality
 * Wraps the openrouter_backend.py functions from the original Python backend
 */

export const tailoringService = {
  /**
   * Tailor resume based on job description
   * @param {string} resumeText - Original resume text
   * @param {string} jobDescription - Job description text
   * @param {Object} apiConfig - API configuration { apiKey, model }
   * @returns {Promise<Object>} Tailored resume data (structured)
   */
  tailorResume: async (resumeText, jobDescription, apiConfig = {}) => {
    const headers = {
      'Content-Type': 'application/json',
    };
    if (apiConfig.apiKey) headers['X-API-Key'] = apiConfig.apiKey;
    if (apiConfig.model) headers['X-Model'] = apiConfig.model;

    const data = await requestJson('/api/tailor-resume', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        resume_text: resumeText,
        job_description: jobDescription,
      }),
    });

    return data.tailored_resume ?? data.tailoredResume;
  }
};

export default tailoringService;
