import { requestBlob, requestJson } from './http';

/**
 * Service for PDF/HTML preview generation functionality
 * Wraps the pdf_engine.py functions from the original Python backend
 */

export const pdfService = {
  /**
   * Generate HTML preview for a given resume data and layout
   * @param {Object} resumeData - Structured resume data
   * @param {number} layoutNumber - Layout number (1-5)
   * @returns {Promise<string>} HTML string for preview
   */
  getHTMLPreview: async (resumeData, layoutNumber) => {
    const data = await requestJson('/api/get-preview-html', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        resume_data: resumeData,
        layout_number: layoutNumber,
      }),
    });

    return data.html;
  },

  /**
   * Generate PDF resume for given resume data and layout
   * @param {Object} resumeData - Structured resume data
   * @param {number} layoutNumber - Layout number (1-5)
   * @returns {Promise<Blob>} PDF file as Blob
   */
  generatePDF: async (resumeData, layoutNumber) => {
    return requestBlob('/api/generate-pdf', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        resume_data: resumeData,
        layout_number: layoutNumber,
      }),
    });
  }
};

export default pdfService;
