# 🚀 AI Resume Builder Web Application

A modern, production-grade AI Resume Builder featuring a real-time **Two-Panel Interface**:
**User Input (Left Panel) → AI Processing → Live Professional Resume (Right Panel)**.

Designed for job seekers, software developers, students, and executives to build ATS-compliant, recruiter-ready resumes in minutes.

---

## 🌟 Key Highlights & Capabilities

### 1. Two-Panel Live Desktop Layout (50% / 50%)
- **Left Panel**: Expandable/collapsible accordion forms for Personal Information, Professional Summary, Education, Experience, Projects, Skills, Certifications, Achievements, Internships, and Languages.
- **Right Panel**: A4 resume document rendered with standard dimensions (`210mm x 297mm`), margins, and print-ready typography.
- **Instant Two-Way Synchronization**: Keystrokes instantly update the right-side preview without reloading the page.
- **Empty Section Auto-Hiding**: Inactive or unpopulated sections are automatically excluded from the final resume.
- **Mobile Responsive**: Includes dedicated `[✏️ Edit]` and `[👁️ Preview]` toggle tabs for seamless smartphone editing.

### 2. Dual AI Operations & Review Workflow
- **Section-Level AI**:
  - **Summary**: Generate, Improve, Rewrite, Shorten, and Make ATS-Friendly.
  - **Experience**: Automatically transforms raw task notes into impactful, action-driven bullet points (e.g. `• Spearheaded...`).
  - **Projects**: Formats technical descriptions, tech stacks, and live links.
  - **Skills**: Suggests relevant modern skills based on your profile, clearly marked as suggestions.
  - **Writing Options**: `Improve`, `Professional`, `ATS Friendly`, `Shorten`, `Expand`, `Rewrite`.
- **Complete Resume AI ("Build My Resume with AI")**:
  - Enter raw, unstructured notes or biography.
  - AI parses and organizes it into structured JSON matching the candidate's career data.
  - Presents a verification checklist before applying.
- **Strict User Review Workflow (Safety Rule)**:
  - AI suggestions are **NEVER** injected directly into user data.
  - Every AI output opens in a dedicated review modal with `[Use This]`, `[Edit]`, and `[Cancel / Discard]` actions.
- **Anti-Fabrication Guardrails**:
  - Strictly preserves facts. Never hallucinates companies, degrees, dates, metrics, or percentages unless provided by the user.

### 3. Dual Engine Strategy (OpenAI + Intelligent Local NLP)
- **OpenAI Cloud Engine**: Configure `OPENAI_API_KEY` in `.env` to leverage `gpt-4o-mini` or your preferred OpenAI model.
- **Intelligent Local NLP Engine**: If an OpenAI key is not provided, the built-in heuristic NLP engine executes action-verb transformations, formatting, shortening, expanding, and unstructured text parsing **100% out of the box** without external API costs or setup hurdles.

### 4. 5 Professional Resume Templates
Seamlessly switch between 5 distinct design archetypes without losing any data:
1. **Classic ATS**: High-contrast, clean lines, single-column layout optimized for automated ATS parsers.
2. **Modern Professional**: Contemporary typography, visual role accents, and balanced whitespace.
3. **Minimal**: Swiss minimalist design with refined hairline dividers and elegant header hierarchy.
4. **Fresher / Student**: Prioritizes Education and Projects over work history for new graduates.
5. **Executive**: Authoritative corporate design emphasizing leadership, executive summaries, and milestone honors.

### 5. ATS Job Optimization Analyzer
- Paste any target job description.
- Computes an **Overall ATS Compatibility Score (0-100)**, Keyword Match %, Skills Match %, Experience Match %, and Structure Completeness.
- Highlights:
  - Matched keywords (`✓ Your resume matches Python`).
  - Missing keywords with cautionary advice (`⚠ The job description mentions REST APIs. Add this only if you actually possess relevant experience.`).
  - Metric enhancement guidance.

### 6. Persistence & Export
- SQLite database backing CRUD operations: Create, Edit, Save, Duplicate, Rename, and Delete resumes.
- Download native A4 PDF via **ReportLab**.
- Native browser print preview (`Ctrl+P` / `Print`) with dedicated print styles.

---

## 📁 Project Directory Structure

```
ai-resume-builder/
├── app.py                      # Flask application factory and server entry point
├── config.py                   # App configuration and environment variables
├── requirements.txt            # Python dependencies
├── .env.example                # Sample environment template
├── .env                        # Local environment configuration
│
├── models/
│   ├── __init__.py             # SQLAlchemy instance
│   └── resume.py               # Resume data model, JSON serialization, and sample data
│
├── routes/
│   ├── __init__.py
│   ├── resume_routes.py        # Web routes (/, /dashboard, /editor) and CRUD REST API
│   ├── ai_routes.py            # AI endpoints (summary, description, improve, rewrite, ats)
│   └── export_routes.py        # PDF stream download and print view routes
│
├── services/
│   ├── __init__.py
│   ├── ai_service.py           # Core AI processing (OpenAI API + Local NLP fallback engine)
│   ├── ats_service.py          # ATS matching algorithm, scoring, and keyword analyzer
│   └── pdf_service.py          # ReportLab A4 PDF generator with multi-template styling
│
├── templates/
│   ├── base.html               # Shared layout, typography, navigation, and toast container
│   ├── dashboard.html          # Resume management dashboard
│   ├── editor.html             # The 2-Panel desktop and mobile split editor
│   └── resume/
│       ├── print_view.html     # Dedicated print layout
│       ├── classic.html        # Classic ATS template partial
│       ├── modern.html         # Modern Professional template partial
│       ├── minimal.html        # Minimal template partial
│       ├── fresher.html        # Fresher / Student template partial
│       └── executive.html      # Executive template partial
│
├── static/
│   ├── css/
│   │   ├── style.css           # Global tokens, modals, toasts, cards, and buttons
│   │   ├── editor.css          # Two-panel split layout, accordions, skill badges
│   │   └── resume.css          # A4 dimensions, print media rules, and template themes
│   │
│   └── js/
│       ├── preview.js          # Client-side instant live preview renderer
│       ├── editor.js           # Two-way data binding, dynamic cards, state management
│       ├── ai.js               # Universal review modal, section AI, full resume builder
│       └── ats.js              # ATS analyzer modal, circular score, recommendations
│
└── tests/
    └── test_app.py             # Complete automated test suite (13 tests)
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- Python 3.9+ installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure OpenAI API Key
Copy `.env.example` to `.env` and set your key:
```ini
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
```
*(Note: If left blank, the application automatically runs using the built-in Intelligent NLP Engine).*

### 4. Run the Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running Automated Tests

To execute the test suite covering models, REST API, AI endpoints, ATS analyzer, and PDF generation:

```bash
python -m pytest -v tests/test_app.py
```

Expected output:
```
tests/test_app.py::test_homepage_redirect PASSED                         [  7%]
tests/test_app.py::test_dashboard_renders PASSED                         [ 15%]
tests/test_app.py::test_editor_renders PASSED                            [ 23%]
tests/test_app.py::test_resume_crud_api PASSED                           [ 30%]
tests/test_app.py::test_ai_status PASSED                                 [ 38%]
tests/test_app.py::test_ai_generate_summary PASSED                       [ 46%]
tests/test_app.py::test_ai_generate_experience_description PASSED        [ 53%]
tests/test_app.py::test_ai_generate_project_description PASSED           [ 61%]
tests/test_app.py::test_ai_writing_options PASSED                        [ 69%]
tests/test_app.py::test_ai_suggest_skills PASSED                         [ 76%]
tests/test_app.py::test_ai_complete_resume_generator PASSED              [ 84%]
tests/test_app.py::test_ats_analyzer PASSED                              [ 92%]
tests/test_app.py::test_pdf_export PASSED                                [100%]

============================= 13 passed in 0.81s ==============================
```

---

## 🛡️ Non-Fabrication & Safety Architecture

The AI Resume Builder follows an uncompromising rule:
> **AI must elevate wording, structure, and professional clarity without inventing unverified facts.**

- **No Hallucinated Statistics**: It never invents percentage increases or revenue metrics unless explicitly given in the user's raw notes.
- **No Inverted Qualifications**: Degrees, institutions, certifications, and companies are strictly derived from user input.
- **Transparent Suggestions**: Skills and ATS recommendations are flagged with clear cautionary warnings:
  *"Add this only if you actually possess relevant experience."*
