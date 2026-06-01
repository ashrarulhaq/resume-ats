import { requestJson } from './http';

/**
 * Service for keyword matching functionality
 * Wraps the keyword_matcher.py functions from the original Python backend
 */

export const keywordService = {
  /**
   * Extract keywords from job description
   * @param {string} jobDescription - Job description text
   * @returns {Promise<string[]>} Extracted keywords
   */
  extractKeywordsFromJD: async (jobDescription) => {
    const data = await requestJson('/api/extract-keywords', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_description: jobDescription }),
    });

    return data.keywords;
  },

  /**
   * Calculate match score between resume text and keywords
   * @param {string} resumeText - Resume text
   * @param {string[]} keywords - Keywords to match against
   * @returns {Promise<{score: number, matched: string[], missing: string[]}>} Match results
   */
  calculateMatchScore: async (resumeText, keywords) => {
    const data = await requestJson('/api/calculate-match', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resume_text: resumeText,
        keywords,
      }),
    });

    return data.result;
  }
};

export default keywordService;
