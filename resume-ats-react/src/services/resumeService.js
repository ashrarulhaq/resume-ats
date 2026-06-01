import { requestJson } from './http';

/**
 * Service for resume file parsing functionality
 * Wraps the parser.py functions from the original Python backend
 */

export const resumeService = {
  /**
   * Extract text from PDF file
   * @param {File} file - PDF file to parse
   * @returns {Promise<string>} Extracted text
   */
  extractTextFromPDF: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('fileType', 'pdf');

    const data = await requestJson('/api/parse-resume', {
      method: 'POST',
      body: formData,
    });

    return data.text;
  },

  /**
   * Extract text from DOCX file
   * @param {File} file - DOCX file to parse
   * @returns {Promise<string>} Extracted text
   */
  extractTextFromDOCX: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('fileType', 'docx');

    const data = await requestJson('/api/parse-resume', {
      method: 'POST',
      body: formData,
    });

    return data.text;
  },

  /**
   * Extract text from TXT file
   * @param {File} file - TXT file to parse
   * @returns {Promise<string>} Extracted text
   */
  extractTextFromTXT: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('fileType', 'txt');

    const data = await requestJson('/api/parse-resume', {
      method: 'POST',
      body: formData,
    });

    return data.text;
  },

  /**
   * Parse resume based on file type
   * @param {File} file - Resume file to parse
   @param {string} fileType - File extension (pdf, docx, txt)
   * @returns {Promise<string>} Extracted text
   */
  parseResume: async (file, fileType) => {
    switch (fileType.toLowerCase()) {
      case 'pdf':
        return await resumeService.extractTextFromPDF(file);
      case 'docx':
      case 'doc':
        return await resumeService.extractTextFromDOCX(file);
      case 'txt':
        return await resumeService.extractTextFromTXT(file);
      default:
        throw new Error(`Unsupported file type: ${fileType}`);
    }
  }
};

export default resumeService;
