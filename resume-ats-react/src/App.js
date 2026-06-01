import React, { useState, useCallback } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import ResumeUploader from './components/ResumeUploader';
import JobDescriptionInput from './components/JobDescriptionInput';
import ProcessingSection from './components/ProcessingSection';
import ResultsSection from './components/ResultsSection';
import LayoutSelector from './components/LayoutSelector';
import PreviewSection from './components/PreviewSection';
import { resumeService, keywordService, tailoringService, validationService, pdfService } from './services';

function resumeToText(resume) {
  if (!resume || typeof resume !== 'object') return '';

  const parts = [];
  const add = (value) => {
    if (value) parts.push(String(value));
  };

  add(resume.name);
  add(resume.summary);

  if (resume.contact && typeof resume.contact === 'object') {
    add(Object.values(resume.contact).filter(Boolean).join(' '));
  }

  if (Array.isArray(resume.skills)) add(resume.skills.join(' '));
  if (Array.isArray(resume.certifications)) add(resume.certifications.join(' '));

  if (Array.isArray(resume.experience)) {
    resume.experience.forEach((experience) => {
      add([
        experience.company,
        experience.title,
        experience.dates,
        experience.location,
        ...(Array.isArray(experience.bullets) ? experience.bullets : []),
      ].filter(Boolean).join(' '));
    });
  }

  if (Array.isArray(resume.education)) {
    resume.education.forEach((education) => {
      add([
        education.school,
        education.degree,
        education.dates,
        education.location,
        education.cgpa,
        education.percentage,
      ].filter(Boolean).join(' '));
    });
  }

  if (Array.isArray(resume.projects)) {
    resume.projects.forEach((project) => {
      add([
        project.name,
        project.description,
        ...(Array.isArray(project.technologies) ? project.technologies : []),
      ].filter(Boolean).join(' '));
    });
  }

  return parts.join('\n');
}

function App() {
  // State variables matching the original Streamlit app
  const [originalText, setOriginalText] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [tailoredResume, setTailoredResume] = useState(null);
  const [validationReport, setValidationReport] = useState(null);
  const [keywordScore, setKeywordScore] = useState(null);
  const [selectedLayout, setSelectedLayout] = useState(1); // Single classic layout
  const [previewHtml, setPreviewHtml] = useState('');
  const [pdfBlob, setPdfBlob] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [apiConfig, setApiConfig] = useState({ apiKey: '', model: 'openrouter/gpt-3.5-turbo' });
  const [initialKeywords, setInitialKeywords] = useState([]);
  const [finalKeywords, setFinalKeywords] = useState([]);

  // File upload handlers
  const handleFileUpload = useCallback(async (file) => {
    if (!file) return;

    // Check file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      alert('File exceeds 10MB limit. Please compress or use a smaller file.');
      return;
    }

    const fileExtension = file.name.split('.').pop().toLowerCase();
    try {
      const extractedText = await resumeService.parseResume(file, fileExtension);
      setOriginalText(extractedText);
      setTailoredResume(null);
      setValidationReport(null);
      setKeywordScore(null);
      setPreviewHtml('');
      setPdfBlob(null);
      setFinalKeywords([]);

      // Also extract initial keywords from the original resume for comparison
      if (jobDescription) {
        const keywords = await keywordService.extractKeywordsFromJD(jobDescription);
        setInitialKeywords(keywords);

        // Calculate initial match score
        const matchScore = await keywordService.calculateMatchScore(extractedText, keywords);
        setKeywordScore(matchScore); // This will be updated later with final score
      }
    } catch (error) {
      alert(`Failed to extract text from the file: ${error.message}`);
    }
  }, [jobDescription]);

  // Job description change handler
  const handleJobDescriptionChange = useCallback(async (text) => {
    setJobDescription(text);
    setInitialKeywords([]); // Reset initial keywords
    setTailoredResume(null);
    setValidationReport(null);
    setKeywordScore(null);
    setPreviewHtml('');
    setPdfBlob(null);
    setFinalKeywords([]);

    if (originalText && text) {
      try {
        const keywords = await keywordService.extractKeywordsFromJD(text);
        setInitialKeywords(keywords);

        // Calculate initial match score
        const matchScore = await keywordService.calculateMatchScore(originalText, keywords);
        setKeywordScore(matchScore); // Will be replaced with final score after tailoring
      } catch (error) {
        console.error('Failed to extract keywords:', error);
      }
    }
  }, [originalText]);

  // Tailor resume handler
  const handleTailorResume = useCallback(async () => {
    if (!originalText || !jobDescription) return;

    setProcessing(true);
    try {
      // Call AI tailoring service
      const tailoredData = await tailoringService.tailorResume(originalText, jobDescription, apiConfig);
      setTailoredResume(tailoredData);

      // Validate against truth guardrails
      const validationResult = await validationService.validateTailoredResume(originalText, tailoredData);
      setValidationReport(validationResult.validationReport);
      const cleanedResume = validationResult.cleanedResume;
      setTailoredResume(cleanedResume);

      // Calculate final keyword match score
      if (cleanedResume) {
        const finalKeywords = await keywordService.extractKeywordsFromJD(jobDescription);
        setFinalKeywords(finalKeywords);

        const finalMatchScore = await keywordService.calculateMatchScore(
          resumeToText(cleanedResume),
          finalKeywords
        );
        setKeywordScore(finalMatchScore);
      }

      // Generate preview HTML
      if (cleanedResume) {
        const previewHtml = await pdfService.getHTMLPreview(cleanedResume, selectedLayout);
        setPreviewHtml(previewHtml);
      }

    } catch (error) {
      alert(`Error tailoring resume: ${error.message}`);
    } finally {
      setProcessing(false);
    }
  }, [originalText, jobDescription, selectedLayout, apiConfig]);

  // Layout change handler
  const handleLayoutChange = useCallback(async () => {
    const nextLayout = 1;
    setSelectedLayout(nextLayout);
    if (tailoredResume) {
      try {
        const previewHtml = await pdfService.getHTMLPreview(tailoredResume, nextLayout);
        setPreviewHtml(previewHtml);
      } catch (error) {
        alert(`Failed to generate preview: ${error.message}`);
      }
    }
  }, [tailoredResume]);

  // PDF generation handler
  const handleGeneratePDF = useCallback(async () => {
    if (!tailoredResume) return;

    try {
      const pdfBlob = await pdfService.generatePDF(tailoredResume, selectedLayout);
      setPdfBlob(pdfBlob);
    } catch (error) {
      alert(`Failed to generate PDF: ${error.message}`);
    }
  }, [tailoredResume, selectedLayout]);

  // Reset form handler
  const handleReset = useCallback(() => {
    setOriginalText('');
    setJobDescription('');
    setTailoredResume(null);
    setValidationReport(null);
    setKeywordScore(null);
    setSelectedLayout(1);
    setPreviewHtml('');
    setPdfBlob(null);
    setProcessing(false);
    setApiConfig({ apiKey: '', model: 'openrouter/gpt-3.5-turbo' });
    setInitialKeywords([]);
    setFinalKeywords([]);
  }, []);

  const tailoredResumeText = tailoredResume ? resumeToText(tailoredResume) : '';

  return (
    <div className="App">
      <header className="App-header">
        <h1>📄 Resume Tailor</h1>
        <p>Tailor your resume to match job descriptions while staying 100% truthful</p>
      </header>

      <Sidebar
        apiConfig={apiConfig}
        onApiConfigChange={setApiConfig}
        hasApiKey={!!apiConfig.apiKey}
      />

      {!apiConfig.apiKey && (
        <div className="warning">
          ⚠️ Please enter your OpenRouter API key in the sidebar to continue
        </div>
      )}

      {apiConfig.apiKey && (
        <>
          <div className="main-content">
            <ResumeUploader
              onFileUpload={handleFileUpload}
              originalText={originalText}
            />

            <JobDescriptionInput
              onJobDescriptionChange={handleJobDescriptionChange}
              jobDescription={jobDescription}
              originalText={originalText}
              initialKeywords={initialKeywords}
            />

            <ProcessingSection
              onTailorResume={handleTailorResume}
              processing={processing}
              hasInputs={!!(originalText && jobDescription)}
            />

            {tailoredResume && (
              <>
                <ResultsSection
                  keywordScore={keywordScore}
                  validationReport={validationReport}
                  originalText={originalText}
                  tailoredResume={tailoredResume}
                  tailoredResumeText={tailoredResumeText}
                  initialKeywords={initialKeywords}
                  finalKeywords={finalKeywords}
                />

                <LayoutSelector
                  selectedLayout={selectedLayout}
                  onLayoutChange={handleLayoutChange}
                />

                <PreviewSection
                  previewHtml={previewHtml}
                  pdfBlob={pdfBlob}
                  tailoredResume={tailoredResume}
                  onGeneratePDF={handleGeneratePDF}
                  onReset={handleReset}
                />
              </>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default App;
