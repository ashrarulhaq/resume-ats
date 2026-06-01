# Resume Tailor — UI/UX Design Specification

## 1. Design Principles

- **Clarity over beauty:** Every element serves the job-tailoring workflow
- **Progressive disclosure:** Show advanced options only when needed
- **Confidence building:** Always show the user what changed and why
- **Mobile-friendly:** Streamlit handles responsiveness, but design for desktop primary

## 2. Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#2563EB` | Buttons, active states, links |
| Primary Hover | `#1D4ED8` | Button hover |
| Success | `#10B981` | Keyword match indicators, success messages |
| Warning | `#F59E0B` | Validation warnings, missing keywords |
| Danger | `#EF4444` | Errors, fake skill removal alerts |
| Background | `#F9FAFB` | Page background |
| Card | `#FFFFFF` | Content cards |
| Text Primary | `#111827` | Headings, body text |
| Text Secondary | `#6B7280` | Labels, captions |
| Border | `#E5E7EB` | Dividers, card borders |

## 3. Typography

- **Headings:** System sans-serif (Streamlit default), semibold
- **Body:** System sans-serif, regular
- **Monospace:** For code/JSON preview only

## 4. Layout Structure

### 4.1 Page Header

```
+-------------------------------------------------------------+
|  📄  Resume Tailor                                          |
|  AI-powered resume optimization. 100% truthful. ATS-ready.  |
|  [Gemini Status: ✅ Connected]                              |
+-------------------------------------------------------------+
```

- App title with emoji icon
- Subtitle explaining value prop
- Gemini CLI connection status badge (green if `gemini --version` succeeds, red with setup link if not)

### 4.2 Step Indicator

Horizontal stepper at top of main content:

```
[ 1. Upload  ] ---- [ 2. Job Description ] ---- [ 3. Review ] ---- [ 4. Export ]
   ✅ Done              ✅ Done                 ○ Active          ○ Pending
```

- Steps 1-2 are always visible
- Steps 3-4 appear after tailoring completes
- Use Streamlit `st.tabs()` or custom HTML progress bar

### 4.3 Step 1: Upload Resume

```
+-------------------------------------------------------------+
|  Step 1: Upload Your Resume                                  |
|  +-----------------------------------------------------+    |
|  |                                                     |    |
|  |              📎 Drag & drop file here               |    |
|  |         or click to browse (PDF, DOCX, TXT)         |    |
|  |                                                     |    |
|  +-----------------------------------------------------+    |
|                                                              |
|  [Optional] Paste resume text directly:                     |
|  +-----------------------------------------------------+    |
|  |                                                     |    |
|  |                                                     |    |
|  +-----------------------------------------------------+    |
|                                                              |
|  Extracted text preview (first 500 chars):                |
|  "John Doe... Senior Developer at..."                       |
|  ✅ 2,400 characters extracted from PDF                     |
+-------------------------------------------------------------+
```

**Interactions:**
- File upload triggers immediate parsing
- Show spinner while parsing
- Display character count and file type badge
- Show truncated preview with "Show full text" expander
- If PDF has no text layer (image-based), show warning: "This PDF appears to be scanned. Text extraction may be limited."

### 4.4 Step 2: Job Description

```
+-------------------------------------------------------------+
|  Step 2: Paste Job Description                               |
|  +-----------------------------------------------------+    |
|  |                                                     |    |
|  |  [Paste job description here...                     |    |
|  |   3,200 / 10,000 characters                         |    |
|  |                                                     |    |
|  +-----------------------------------------------------+    |
|                                                              |
|  [🎯 Tailor My Resume]  (Primary button, large)             |
|                                                              |
|  ℹ️ Tip: Include the full job posting for best results      |
+-------------------------------------------------------------+
```

**Interactions:**
- Character counter updates live
- Button disabled until both resume and JD are present
- On click: show full-screen spinner with status messages:
  - "Analyzing job description..."
  - "Optimizing resume content with Gemini..."
  - "Validating changes..."
  - "Preparing your tailored resume..."

### 4.5 Step 3: Review Results

Appears after tailoring completes. Two-column layout on desktop:

```
+-------------------------------------------------------------+
|  Step 3: Review Your Tailored Resume                         |
+-------------------------------------------------------------+
|  +------------------------+  +---------------------------+  |
|  | KEYWORD MATCH SCORE    |  | CHANGES SUMMARY           |  |
|  |                        |  |                           |  |
|  |    ┌─────────┐        |  | ✅ Restructured bullets   |  |
|  |    │   87%   │        |  |    to lead with impact    |  |
|  |    │  ██████ │        |  |                           |  |
|  |    └─────────┘        |  | ✅ Added "Kubernetes"     |  |
|  |                        |  |    (from your Docker exp)   |  |
|  | Matched: 26/30 keywords|  | ✅ Reordered experience   |  |
|  |                        |  |    (most relevant first)  |  |
|  | Missing: Kubernetes,   |  |                           |  |
|  | Terraform (not in      |  | ⚠️  Removed: "JQuery"     |  |
|  | resume)               |  |    (not relevant to JD)     |  |
|  |                        |  |                           |  |
|  +------------------------+  +---------------------------+  |
|                                                              |
|  TRUTH VERIFICATION:                                         |
|  ✅ All skills verified against original resume             |
|  ✅ All dates and companies preserved exactly               |
|  ✅ No fake experience added                                |
|                                                              |
|  [View Before/After Comparison]                              |
+-------------------------------------------------------------+
```

**Keyword Match Score Component:**
- Circular progress indicator or horizontal bar
- Green for matched, amber for missing
- Show top 10 keywords with check/X icons

**Changes Summary Component:**
- Green checkmarks for positive changes
- Amber warnings for removals
- Each item has tooltip explaining the reasoning

**Truth Verification Component:**
- Always visible, green banner if passed
- Red banner with details if issues found (e.g., "Removed 2 hallucinated skills")

### 4.6 Before/After Comparison

Expandable section (Streamlit `st.expander`):

```
+-------------------------------------------------------------+
|  Before / After Comparison                                   |
|  +------------------------+  +---------------------------+  |
|  | ORIGINAL               |  | TAILORED                  |  |
|  |                        |  |                           |  |
|  | Used Docker for        |  | Led container orchestration|  |
|  | deployment            |  | (Docker) for microservices |  |
|  |                        |  | deployment, improving     |  |
|  |                        |  | efficiency by 40%         |  |
|  +------------------------+  +---------------------------+  |
|                                                              |
|  [Show all changes] [Download comparison as text]           |
+-------------------------------------------------------------+
```

### 4.7 Step 4: Layout Selection & Export

```
+-------------------------------------------------------------+
|  Step 4: Choose Layout & Export                              |
+-------------------------------------------------------------+
|  Select a professional layout:                               |
|                                                              |
|  +--------+  +--------+  +--------+  +--------+  +--------+ |
|  │ Classic│  │ Modern │  │Minimal │  │   Pro  │  │Compact │ |
|  │  [📄]  │  │  [📄]  │  │  [📄]  │  │  [📄]  │  │  [📄]  │ |
|  │        │  │        │  │        │  │        │  │        │ |
|  │Traditional│ │Clean & │  │Ultra- │  │Two-tone│  │Single │ |
|  │ B&W     │  │Fresh   │  │sparse  │  │header  │  │page   │ |
|  +--------+  +--------+  +--------+  +--------+  +--------+ |
|     ○           ●            ○           ○           ○       |
|                                                              |
|  [Preview Selected Layout]  [Generate PDF & Download]     |
+-------------------------------------------------------------+
```

**Layout Selector:**
- 5 thumbnail cards in horizontal row
- Each thumbnail shows a mini preview image or ASCII art representation
- Click to select (radio button behavior)
- Selected card gets blue border highlight

**Preview Section:**
- After clicking "Preview": show live HTML render in iframe or Streamlit HTML component
- Show actual resume content in selected layout
- "Generate PDF" button becomes active

**Download Section:**
- Primary button: "Download PDF"
- Secondary button: "Download as JSON" (for manual editing)
- Show file size and page count if possible

### 4.8 Sidebar (Optional)

```
+-------------+
| Settings    |
|             |
| Gemini Model│
| [Default ▼] │
|             |
| Output      │
| [ ] Include │
|     projects│
| [ ] Include │
|     certs   │
|             |
| ATS Check   │
| [Run ATS    │
|  Scan]      │
+-------------+
```

- Collapsed by default
- Advanced users can tweak settings

## 5. Component Specifications

### 5.1 Loading States

**Tailoring in progress:**
```
+-------------------------------------------------------------+
|  ⏳ Optimizing your resume...                                |
|                                                              |
|  [████████████░░░░░░░░] 60%                                 |
|                                                              |
|  Current step: Validating truth guardrails...               |
+-------------------------------------------------------------+
```

Use Streamlit `st.spinner()` with custom status messages updated via `st.status()`.

### 5.2 Toast Notifications

| Trigger | Message | Duration |
|---------|---------|----------|
| File uploaded | "Resume parsed: 2,400 characters" | 3s |
| Tailoring complete | "Resume tailored successfully!" | 5s |
| PDF generated | "PDF ready for download" | 3s |
| Validation warning | "2 skills removed (not in original)" | 5s |
| Error | "Gemini CLI not found. [Setup Guide]" | Persistent |

### 5.3 Empty States

**Before upload:**
```
+-------------------------------------------------------------+
|  📎 Upload your resume to get started                        |
|  Supported: PDF, DOCX, TXT                                  |
+-------------------------------------------------------------+
```

**Before tailoring:**
```
+-------------------------------------------------------------+
|  🎯 Paste a job description and click "Tailor"             |
|  to see your optimized resume                                 |
+-------------------------------------------------------------+
```

## 6. Responsive Behavior

| Breakpoint | Layout |
|------------|--------|
| > 1024px | Two-column (sidebar + main, or main content side-by-side) |
| 768-1024px | Single column, layout thumbnails in 3+2 grid |
| < 768px | Single column, layout thumbnails in vertical stack |

## 7. Accessibility

- All buttons have descriptive labels
- Color is not the only indicator (icons + text for status)
- Keyboard navigable (Streamlit default)
- PDF outputs use high contrast for readability

## 8. Error State Designs

### 8.1 Gemini Not Installed

```
+-------------------------------------------------------------+
|  ❌ Gemini CLI Not Found                                     |
|                                                              |
|  This app requires Google's Gemini CLI to run locally.       |
|                                                              |
|  [Install Gemini CLI]  [I've already installed it - Refresh] |
|                                                              |
|  Installation:                                               |
|  1. npm install -g @google/gemini-cli                        |
|  2. gemini auth login                                        |
|  3. Restart this app                                         |
+-------------------------------------------------------------+
```

### 8.2 PDF Generation Error

```
+-------------------------------------------------------------+
|  ⚠️ PDF Generation Failed                                    |
|                                                              |
|  Error: WeasyPrint missing system dependencies               |
|                                                              |
|  [macOS] brew install pango cairo gdk-pixbuf libffi        |
|  [Ubuntu] sudo apt-get install libpango-1.0-0 ...          |
|                                                              |
|  [Try Again]  [Export as HTML Instead]                      |
+-------------------------------------------------------------+
```

## 9. Streamlit-Specific Implementation Notes

- Use `st.columns()` for side-by-side layouts
- Use `st.container()` with borders for card-like sections
- Use `st.metric()` for keyword score display
- Use `st.json()` for raw JSON preview (debug mode)
- Use `st.download_button()` for PDF export
- Use `st.session_state` to persist data between interactions
- Use `st.rerun()` to refresh UI after async operations
