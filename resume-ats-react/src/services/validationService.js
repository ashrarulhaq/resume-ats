import { requestJson } from './http';

/**
 * Service for validation/truth guardrails functionality
 * Wraps the validator.py functions from the original Python backend
 */

export const validationService = {
  /**
   * Validate tailored resume against original for truthfulness
   * @param {string} originalText - Original resume text
   * @param {Object} tailoredResume - Tailored resume data (structured)
   * @returns {Promise<{
   *   isValid: boolean,
   *   validationReport: {
   *     skillsValid: boolean,
   *     invalidSkills: string[],
   *     datesValid: boolean,
   *     companiesValid: boolean,
   *     warnings: string[]
   *   },
   *   cleanedResume: Object
   * }>} Validation results
   */
  validateTailoredResume: async (originalText, tailoredResume) => {
    const data = await requestJson('/api/validate-resume', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        original_text: originalText,
        tailored_resume: tailoredResume,
      }),
    });

    const result = data.result ?? data;
    return {
      ...result,
      validationReport: result.validationReport ?? result.validation_report,
      cleanedResume: result.cleanedResume ?? result.cleaned_resume,
    };
  }
};

export default validationService;
