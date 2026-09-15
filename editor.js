/**
 * Form Controller and State Manager for AI Resume Builder
 */

// Global State
window.resumeState = window.initialResumeData || {
  personal: { name: "", title: "", email: "", phone: "", location: "", linkedin: "", github: "", portfolio: "" },
  summary: "",
  education: [],
  experience: [],
  projects: [],
  skills: { programming: [], frameworks: [], web: [], databases: [], tools: [], soft: [] },
  certifications: [],
  achievements: [],
  internships: [],
  languages: []
};

window.currentTemplate = window.initialTemplate || "classic";
window.resumeId = window.activeResumeId || 1;

// Toast Helper
function showToast(message, type = "success") {
  let container = document.getElementById("toastContainer");
  if (!container) {
    container = document.createElement("div");
    container.id = "toastContainer";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  const icon = type === "success" ? "✓" : (type === "ai" ? "✨" : "⚠");
  toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.3s";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  initAccordions();
  initTemplateSelector();
  initMobileTabs();
  populateFormFromState();
  bindStaticInputs();
  renderPreview(window.resumeState, window.currentTemplate);
});

// Accordions Expand / Collapse
function initAccordions() {
  document.querySelectorAll(".accordion-header").forEach(header => {
    header.addEventListener("click", () => {
      const section = header.closest(".accordion-section");
      section.classList.toggle("expanded");
    });
  });
}

// Template Switching
function initTemplateSelector() {
  document.querySelectorAll(".template-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".template-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      window.currentTemplate = btn.getAttribute("data-template");
      renderPreview(window.resumeState, window.currentTemplate);
    });
  });
}

// Mobile Tab Toggle
function initMobileTabs() {
  const editTab = document.getElementById("mobileTabEdit");
  const prevTab = document.getElementById("mobileTabPrev");
  const layout = document.querySelector(".editor-layout");

  if (editTab && prevTab && layout) {
    editTab.addEventListener("click", () => {
      editTab.classList.add("active");
      prevTab.classList.remove("active");
      layout.classList.remove("show-preview");
    });
    prevTab.addEventListener("click", () => {
      prevTab.classList.add("active");
      editTab.classList.remove("active");
      layout.classList.add("show-preview");
    });
  }
}

// Bind Static Inputs (Personal Info & Summary)
function bindStaticInputs() {
  const fields = ["name", "title", "email", "phone", "location", "linkedin", "github", "portfolio"];
  fields.forEach(field => {
    const el = document.getElementById(`personal_${field}`);
    if (el) {
      el.addEventListener("input", (e) => {
        if (!window.resumeState.personal) window.resumeState.personal = {};
        window.resumeState.personal[field] = e.target.value;
        renderPreview(window.resumeState, window.currentTemplate);
      });
    }
  });

  const summaryEl = document.getElementById("summary_text");
  if (summaryEl) {
    summaryEl.addEventListener("input", (e) => {
      window.resumeState.summary = e.target.value;
      renderPreview(window.resumeState, window.currentTemplate);
    });
  }

  const titleInput = document.getElementById("resumeTitleInput");
  if (titleInput) {
    titleInput.addEventListener("change", (e) => {
      saveResumeTitle(e.target.value);
    });
  }
}

// Populate entire form from window.resumeState
function populateFormFromState() {
  const p = window.resumeState.personal || {};
  ["name", "title", "email", "phone", "location", "linkedin", "github", "portfolio"].forEach(f => {
    const el = document.getElementById(`personal_${f}`);
    if (el) el.value = p[f] || "";
  });

  const summaryEl = document.getElementById("summary_text");
  if (summaryEl) summaryEl.value = window.resumeState.summary || "";

  renderEducationCards();
  renderExperienceCards();
  renderProjectCards();
  renderSkillsUI();
  renderCertificationCards();
  renderAchievementCards();
  renderInternshipCards();
  renderLanguageInputs();
}

// EDUCATION
function renderEducationCards() {
  const container = document.getElementById("educationContainer");
  if (!container) return;
  container.innerHTML = "";

  (window.resumeState.education || []).forEach((item, index) => {
    const card = document.createElement("div");
    card.className = "dynamic-card";
    card.innerHTML = `
      <div class="dynamic-card-header">
        <span class="dynamic-card-title">#${index + 1} Degree & School</span>
        <button type="button" class="btn-icon-danger" onclick="removeEducationEntry(${index})">✕ Remove</button>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Degree</label>
          <input type="text" class="form-input" value="${escapeHtml(item.degree || '')}" oninput="updateEdu(${index}, 'degree', this.value)" placeholder="e.g. B.Tech Computer Science">
        </div>
        <div class="form-group">
          <label class="form-label">College / University</label>
          <input type="text" class="form-input" value="${escapeHtml(item.university || '')}" oninput="updateEdu(${index}, 'university', this.value)" placeholder="e.g. ABC University">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Location</label>
          <input type="text" class="form-input" value="${escapeHtml(item.location || '')}" oninput="updateEdu(${index}, 'location', this.value)" placeholder="e.g. San Jose, CA">
        </div>
        <div class="form-group">
          <label class="form-label">Start Year</label>
          <input type="text" class="form-input" value="${escapeHtml(item.startYear || '')}" oninput="updateEdu(${index}, 'startYear', this.value)" placeholder="2020">
        </div>
        <div class="form-group">
          <label class="form-label">End Year</label>
          <input type="text" class="form-input" value="${escapeHtml(item.endYear || '')}" oninput="updateEdu(${index}, 'endYear', this.value)" placeholder="2024">
        </div>
        <div class="form-group">
          <label class="form-label">GPA / Percentage</label>
          <input type="text" class="form-input" value="${escapeHtml(item.gpa || '')}" oninput="updateEdu(${index}, 'gpa', this.value)" placeholder="3.8 / 4.0">
        </div>
      </div>
      <div class="form-group">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.3rem;">
          <label class="form-label" style="margin-bottom:0;">Description / Academic Highlights</label>
          <button type="button" class="ai-btn-pill" onclick="triggerEduAIDescription(${index})">✨ Generate Description</button>
        </div>
        <textarea class="form-textarea" rows="2" oninput="updateEdu(${index}, 'description', this.value)" placeholder="Key coursework, honors, or academic focus...">${escapeHtml(item.description || '')}</textarea>
      </div>
    `;
    container.appendChild(card);
  });
}

function addEducationEntry() {
  if (!window.resumeState.education) window.resumeState.education = [];
  window.resumeState.education.push({ degree: "", university: "", location: "", startYear: "", endYear: "", gpa: "", description: "" });
  renderEducationCards();
  renderPreview(window.resumeState, window.currentTemplate);
}

function removeEducationEntry(idx) {
  window.resumeState.education.splice(idx, 1);
  renderEducationCards();
  renderPreview(window.resumeState, window.currentTemplate);
}

function updateEdu(idx, field, val) {
  window.resumeState.education[idx][field] = val;
  renderPreview(window.resumeState, window.currentTemplate);
}

// EXPERIENCE
function renderExperienceCards() {
  const container = document.getElementById("experienceContainer");
  if (!container) return;
  container.innerHTML = "";

  (window.resumeState.experience || []).forEach((item, index) => {
    const card = document.createElement("div");
    card.className = "dynamic-card";
    card.innerHTML = `
      <div class="dynamic-card-header">
        <span class="dynamic-card-title">#${index + 1} Professional Experience</span>
        <button type="button" class="btn-icon-danger" onclick="removeExperienceEntry(${index})">✕ Remove</button>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Job Title</label>
          <input type="text" class="form-input" value="${escapeHtml(item.jobTitle || '')}" oninput="updateExp(${index}, 'jobTitle', this.value)" placeholder="e.g. Software Developer Intern">
        </div>
        <div class="form-group">
          <label class="form-label">Company</label>
          <input type="text" class="form-input" value="${escapeHtml(item.company || '')}" oninput="updateExp(${index}, 'company', this.value)" placeholder="e.g. ABC Technologies">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Location</label>
          <input type="text" class="form-input" value="${escapeHtml(item.location || '')}" oninput="updateExp(${index}, 'location', this.value)" placeholder="e.g. San Francisco, CA">
        </div>
        <div class="form-group">
          <label class="form-label">Start Date</label>
          <input type="text" class="form-input" value="${escapeHtml(item.startDate || '')}" oninput="updateExp(${index}, 'startDate', this.value)" placeholder="e.g. Jun 2023">
        </div>
        <div class="form-group">
          <label class="form-label">End Date</label>
          <input type="text" class="form-input" value="${escapeHtml(item.endDate || '')}" ${item.currentlyWorking ? 'disabled' : ''} oninput="updateExp(${index}, 'endDate', this.value)" placeholder="e.g. Dec 2023">
        </div>
      </div>
      <div class="form-group" style="margin-top:-0.3rem;">
        <label style="font-size:0.8rem; display:inline-flex; align-items:center; gap:0.4rem; cursor:pointer;">
          <input type="checkbox" ${item.currentlyWorking ? 'checked' : ''} onchange="updateExp(${index}, 'currentlyWorking', this.checked); renderExperienceCards();">
          Currently Working Here
        </label>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Raw Responsibilities</label>
          <textarea class="form-textarea" rows="2" oninput="updateExp(${index}, 'responsibilities', this.value)" placeholder="e.g. Worked on website, used Python, fixed bugs...">${escapeHtml(item.responsibilities || '')}</textarea>
        </div>
        <div class="form-group">
          <label class="form-label">Raw Achievements</label>
          <textarea class="form-textarea" rows="2" oninput="updateExp(${index}, 'achievements', this.value)" placeholder="e.g. Improved query response times...">${escapeHtml(item.achievements || '')}</textarea>
        </div>
      </div>
      <div class="form-group">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.3rem; flex-wrap:wrap; gap:0.4rem;">
          <label class="form-label" style="margin-bottom:0;">Formatted Description (Bullet Points)</label>
          <div class="ai-actions-row" style="margin:0;">
            <button type="button" class="ai-btn-pill" onclick="triggerExpAIDescription(${index})">✨ Generate Description</button>
            <button type="button" class="ai-btn-pill" onclick="triggerExpStyle(${index}, 'improve')">✨ Improve</button>
            <button type="button" class="ai-btn-pill" onclick="triggerExpStyle(${index}, 'ats')">✨ ATS Friendly</button>
            <button type="button" class="ai-btn-pill" onclick="triggerExpStyle(${index}, 'shorten')">✨ Shorten</button>
          </div>
        </div>
        <textarea id="exp_desc_${index}" class="form-textarea" rows="3" oninput="updateExp(${index}, 'description', this.value)" placeholder="• Bullet 1&#10;• Bullet 2...">${escapeHtml(item.description || '')}</textarea>
      </div>
    `;
    container.appendChild(card);
  });
}

function addExperienceEntry() {
  if (!window.resumeState.experience) window.resumeState.experience = [];
  window.resumeState.experience.push({ jobTitle: "", company: "", location: "", startDate: "", endDate: "", currentlyWorking: false, responsibilities: "", achievements: "", description: "" });
  renderExperienceCards();
  renderPreview(window.resumeState, window.currentTemplate);
}

function removeExperienceEntry(idx) {
  window.resumeState.experience.splice(idx, 1);
  renderExperienceCards();
  renderPreview(window.resumeState, window.currentTemplate);
}

function updateExp(idx, field, val) {
  window.resumeState.experience[idx][field] = val;
  renderPreview(window.resumeState, window.currentTemplate);
}

// PROJECTS
function renderProjectCards() {
  const container = document.getElementById("projectsContainer");
  if (!container) return;
  container.innerHTML = "";

  (window.resumeState.projects || []).forEach((item, index) => {
    const card = document.createElement("div");
    card.className = "dynamic-card";
    card.innerHTML = `
      <div class="dynamic-card-header">
        <span class="dynamic-card-title">#${index + 1} Project</span>
        <button type="button" class="btn-icon-danger" onclick="removeProjectEntry(${index})">✕ Remove</button>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Project Name</label>
          <input type="text" class="form-input" value="${escapeHtml(item.name || '')}" oninput="updateProj(${index}, 'name', this.value)" placeholder="e.g. Travel Buddy">
        </div>
        <div class="form-group">
          <label class="form-label">Technologies</label>
          <input type="text" class="form-input" value="${escapeHtml(item.technologies || '')}" oninput="updateProj(${index}, 'technologies', this.value)" placeholder="e.g. Python, Flask, HTML, CSS">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Live Project URL</label>
          <input type="text" class="form-input" value="${escapeHtml(item.projectUrl || '')}" oninput="updateProj(${index}, 'projectUrl', this.value)" placeholder="https://myproject.com">
        </div>
        <div class="form-group">
          <label class="form-label">GitHub URL</label>
          <input type="text" class="form-input" value="${escapeHtml(item.githubUrl || '')}" oninput="updateProj(${index}, 'githubUrl', this.value)" placeholder="https://github.com/user/project">
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Raw Project Notes</label>
        <textarea class="form-textarea" rows="2" oninput="updateProj(${index}, 'rawDescription', this.value)" placeholder="Website to help users find hotels and restaurants...">${escapeHtml(item.rawDescription || '')}</textarea>
      </div>
      <div class="form-group">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.3rem; flex-wrap:wrap; gap:0.4rem;">
          <label class="form-label" style="margin-bottom:0;">Professional Description</label>
          <div class="ai-actions-row" style="margin:0;">
            <button type="button" class="ai-btn-pill" onclick="triggerProjAIDescription(${index})">✨ Generate Description</button>
            <button type="button" class="ai-btn-pill" onclick="triggerProjStyle(${index}, 'professional')">✨ Professional</button>
            <button type="button" class="ai-btn-pill" onclick="triggerProjStyle(${index}, 'shorten')">✨ Shorten</button>
          </div>
        </div>
        <textarea id="proj_desc_${index}" class="form-textarea" rows="3" oninput="updateProj(${index}, 'description', this.value)" placeholder="Developed a travel planning web application...">${escapeHtml(item.description || '')}</textarea>
      </div>
    `;
    container.appendChild(card);
  });
}

function addProjectEntry() {
  if (!window.resumeState.projects) window.resumeState.projects = [];
  window.resumeState.projects.push({ name: "", projectUrl: "", githubUrl: "", technologies: "", rawDescription: "", description: "" });
  renderProjectCards();
  renderPreview(window.resumeState, window.currentTemplate);
}

function removeProjectEntry(idx) {
  window.resumeState.projects.splice(idx, 1);
  renderProjectCards();
  renderPreview(window.resumeState, window.currentTemplate);
}

function updateProj(idx, field, val) {
  window.resumeState.projects[idx][field] = val;
  renderPreview(window.resumeState, window.currentTemplate);
}

// SKILLS
const SKILL_CATEGORIES = [
  { key: "programming", title: "Programming Languages", placeholder: "e.g. Python" },
  { key: "frameworks", title: "Frameworks & Libraries", placeholder: "e.g. Flask, React" },
  { key: "web", title: "Web Technologies", placeholder: "e.g. HTML5, REST APIs" },
  { key: "databases", title: "Databases", placeholder: "e.g. PostgreSQL, SQLite" },
  { key: "tools", title: "Tools & Platforms", placeholder: "e.g. Git, Docker" },
  { key: "soft", title: "Soft Skills", placeholder: "e.g. Problem Solving" }
];

function renderSkillsUI() {
  const container = document.getElementById("skillsCategoryContainer");
  if (!container) return;
  container.innerHTML = "";

  if (!window.resumeState.skills) {
    window.resumeState.skills = { programming: [], frameworks: [], web: [], databases: [], tools: [], soft: [] };
  }

  SKILL_CATEGORIES.forEach(cat => {
    const list = window.resumeState.skills[cat.key] || [];
    const block = document.createElement("div");
    block.className = "skill-category-block";
    
    const chipsHtml = list.map((skill, sIdx) => `
      <span class="skill-chip">
        ${escapeHtml(skill)}
        <span class="skill-chip-remove" onclick="removeSkillChip('${cat.key}', ${sIdx})">&times;</span>
      </span>
    `).join("");

    block.innerHTML = `
      <div class="skill-cat-title">${cat.title}</div>
      <div class="skill-chips-wrap" id="chips_${cat.key}">
        ${chipsHtml}
        <div class="skill-add-input-wrap">
          <input type="text" id="input_skill_${cat.key}" class="skill-input-sm" placeholder="${cat.placeholder}" onkeydown="handleSkillKey(event, '${cat.key}')">
          <button type="button" class="btn btn-secondary btn-sm" onclick="addSkillFromInput('${cat.key}')">+ Add</button>
        </div>
      </div>
    `;
    container.appendChild(block);
  });
}

function handleSkillKey(e, catKey) {
  if (e.key === "Enter") {
    e.preventDefault();
    addSkillFromInput(catKey);
  }
}

function addSkillFromInput(catKey) {
  const input = document.getElementById(`input_skill_${catKey}`);
  if (!input) return;
  const val = input.value.trim();
  if (val) {
    if (!window.resumeState.skills[catKey]) window.resumeState.skills[catKey] = [];
    if (!window.resumeState.skills[catKey].includes(val)) {
      window.resumeState.skills[catKey].push(val);
      renderSkillsUI();
      renderPreview(window.resumeState, window.currentTemplate);
    }
    input.value = "";
  }
}

function removeSkillChip(catKey, idx) {
  window.resumeState.skills[catKey].splice(idx, 1);
  renderSkillsUI();
  renderPreview(window.resumeState, window.currentTemplate);
}

// CERTIFICATIONS
function renderCertificationCards() {
  const container = document.getElementById("certificationsContainer");
  if (!container) return;
  container.innerHTML = "";

  (window.resumeState.certifications || []).forEach((item, index) => {
    const card = document.createElement("div");
    card.className = "dynamic-card";
    card.innerHTML = `
      <div class="dynamic-card-header">
        <span class="dynamic-card-title">#${index + 1} Certification</span>
        <button type="button" class="btn-icon-danger" onclick="removeCertEntry(${index})">✕ Remove</button>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Certification Name</label>
          <input type="text" class="form-input" value="${escapeHtml(item.name || '')}" oninput="updateCert(${index}, 'name', this.value)" placeholder="e.g. AWS Certified Developer">
        </div>
        <div class="form-group">
          <label class="form-label">Issuing Organization</label>
          <input type="text" class="form-input" value="${escapeHtml(item.issuer || '')}" oninput="updateCert(${index}, 'issuer', this.value)" placeholder="e.g. Amazon Web Services">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Date</label>
          <input type="text" class="form-input" value="${escapeHtml(item.date || '')}" oninput="updateCert(${index}, 'date', this.value)" placeholder="2023">
        </div>
        <div class="form-group">
          <label class="form-label">Credential URL</label>
          <input type="text" class="form-input" value="${escapeHtml(item.credentialUrl || '')}" oninput="updateCert(${index}, 'credentialUrl', this.value)" placeholder="https://verify...">
        </div>
      </div>
      <div class="form-group">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.3rem;">
          <label class="form-label" style="margin-bottom:0;">Description (Optional)</label>
          <button type="button" class="ai-btn-pill" onclick="triggerCertAIDescription(${index})">✨ Generate Description</button>
        </div>
        <textarea class="form-textarea" rows="2" oninput="updateCert(${index}, 'description', this.value)" placeholder="Validated competency in...">${escapeHtml(item.description || '')}</textarea>
      </div>
    `;
    container.appendChild(card);
  });
}

function addCertificationEntry() {
  if (!window.resumeState.certifications) window.resumeState.certifications = [];
  window.resumeState.certifications.push({ name: "", issuer: "", date: "", credentialUrl: "", description: "" });
  renderCertificationCards();
  renderPreview(window.resumeState, window.currentTemplate);
}

function removeCertEntry(idx) {
  window.resumeState.certifications.splice(idx, 1);
  renderCertificationCards();
  renderPreview(window.resumeState, window.currentTemplate);
}

function updateCert(idx, field, val) {
  window.resumeState.certifications[idx][field] = val;
  renderPreview(window.resumeState, window.currentTemplate);
}

// ACHIEVEMENTS
function renderAchievementCards() {
  const container = document.getElementById("achievementsContainer");
  if (!container) return;
  container.innerHTML = "";

  (window.resumeState.achievements || []).forEach((item, index) => {
    const card = document.createElement("div");
    card.className = "dynamic-card";
    card.innerHTML = `
      <div class="dynamic-card-header">
        <span class="dynamic-card-title">#${index + 1} Achievement</span>
        <button type="button" class="btn-icon-danger" onclick="removeAchEntry(${index})">✕ Remove</button>
      </div>
      <div class="form-row">
        <div class="form-group" style="flex:2;">
          <label class="form-label">Achievement Title</label>
          <input type="text" class="form-input" value="${escapeHtml(item.title || '')}" oninput="updateAch(${index}, 'title', this.value)" placeholder="e.g. 1st Place Hackathon">
        </div>
        <div class="form-group" style="flex:1;">
          <label class="form-label">Date</label>
          <input type="text" class="form-input" value="${escapeHtml(item.date || '')}" oninput="updateAch(${index}, 'date', this.value)" placeholder="Nov 2023">
        </div>
      </div>
      <div class="form-group">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.3rem;">
          <label class="form-label" style="margin-bottom:0;">Description</label>
          <button type="button" class="ai-btn-pill" onclick="triggerAchAIDescription(${index})">✨ Improve Description</button>
        </div>
        <textarea class="form-textarea" rows="2" oninput="updateAch(${index}, 'description', this.value)" placeholder="Details of recognition or milestone...">${escapeHtml(item.description || '')}</textarea>
      </div>
    `;
    container.appendChild(card);
  });
}

function addAchievementEntry() {
  if (!window.resumeState.achievements) window.resumeState.achievements = [];
  window.resumeState.achievements.push({ title: "", date: "", description: "" });
  renderAchievementCards();
  renderPreview(window.resumeState, window.currentTemplate);
}

function removeAchEntry(idx) {
  window.resumeState.achievements.splice(idx, 1);
  renderAchievementCards();
  renderPreview(window.resumeState, window.currentTemplate);
}

function updateAch(idx, field, val) {
  window.resumeState.achievements[idx][field] = val;
  renderPreview(window.resumeState, window.currentTemplate);
}

// INTERNSHIPS
function renderInternshipCards() {
  const container = document.getElementById("internshipsContainer");
  if (!container) return;
  container.innerHTML = "";

  (window.resumeState.internships || []).forEach((item, index) => {
    const card = document.createElement("div");
    card.className = "dynamic-card";
    card.innerHTML = `
      <div class="dynamic-card-header">
        <span class="dynamic-card-title">#${index + 1} Internship</span>
        <button type="button" class="btn-icon-danger" onclick="removeInternEntry(${index})">✕ Remove</button>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Organization</label>
          <input type="text" class="form-input" value="${escapeHtml(item.organization || '')}" oninput="updateIntern(${index}, 'organization', this.value)" placeholder="Company / Org Name">
        </div>
        <div class="form-group">
          <label class="form-label">Role</label>
          <input type="text" class="form-input" value="${escapeHtml(item.role || '')}" oninput="updateIntern(${index}, 'role', this.value)" placeholder="e.g. Web Development Trainee">
        </div>
        <div class="form-group">
          <label class="form-label">Duration</label>
          <input type="text" class="form-input" value="${escapeHtml(item.duration || '')}" oninput="updateIntern(${index}, 'duration', this.value)" placeholder="Jan 2023 - May 2023">
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Responsibilities Notes</label>
        <textarea class="form-textarea" rows="2" oninput="updateIntern(${index}, 'responsibilities', this.value)" placeholder="Raw notes on tasks performed...">${escapeHtml(item.responsibilities || '')}</textarea>
      </div>
      <div class="form-group">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.3rem;">
          <label class="form-label" style="margin-bottom:0;">Professional Bullets</label>
          <button type="button" class="ai-btn-pill" onclick="triggerInternAIDescription(${index})">✨ Generate Description</button>
        </div>
        <textarea class="form-textarea" rows="2" oninput="updateIntern(${index}, 'description', this.value)" placeholder="• Bullet point...">${escapeHtml(item.description || '')}</textarea>
      </div>
    `;
    container.appendChild(card);
  });
}

function addInternshipEntry() {
  if (!window.resumeState.internships) window.resumeState.internships = [];
  window.resumeState.internships.push({ organization: "", role: "", duration: "", responsibilities: "", description: "" });
  renderInternshipCards();
  renderPreview(window.resumeState, window.currentTemplate);
}

function removeInternEntry(idx) {
  window.resumeState.internships.splice(idx, 1);
  renderInternshipCards();
  renderPreview(window.resumeState, window.currentTemplate);
}

function updateIntern(idx, field, val) {
  window.resumeState.internships[idx][field] = val;
  renderPreview(window.resumeState, window.currentTemplate);
}

// LANGUAGES
function renderLanguageInputs() {
  const container = document.getElementById("languagesContainer");
  if (!container) return;
  container.innerHTML = "";

  (window.resumeState.languages || []).forEach((item, index) => {
    const card = document.createElement("div");
    card.className = "dynamic-card";
    card.style.padding = "0.6rem 0.8rem";
    card.innerHTML = `
      <div style="display:flex; gap:0.5rem; align-items:center;">
        <input type="text" class="form-input" style="flex:2;" value="${escapeHtml(item.language || '')}" oninput="updateLang(${index}, 'language', this.value)" placeholder="e.g. English">
        <select class="form-select" style="flex:1.5;" onchange="updateLang(${index}, 'proficiency', this.value)">
          <option value="Professional" ${item.proficiency === 'Professional' ? 'selected' : ''}>Professional</option>
          <option value="Native" ${item.proficiency === 'Native' ? 'selected' : ''}>Native</option>
          <option value="Fluent" ${item.proficiency === 'Fluent' ? 'selected' : ''}>Fluent</option>
          <option value="Intermediate" ${item.proficiency === 'Intermediate' ? 'selected' : ''}>Intermediate</option>
          <option value="Conversational" ${item.proficiency === 'Conversational' ? 'selected' : ''}>Conversational</option>
        </select>
        <button type="button" class="btn-icon-danger" onclick="removeLanguageEntry(${index})">✕</button>
      </div>
    `;
    container.appendChild(card);
  });
}

function addLanguageEntry() {
  if (!window.resumeState.languages) window.resumeState.languages = [];
  window.resumeState.languages.push({ language: "", proficiency: "Professional" });
  renderLanguageInputs();
  renderPreview(window.resumeState, window.currentTemplate);
}

function removeLanguageEntry(idx) {
  window.resumeState.languages.splice(idx, 1);
  renderLanguageInputs();
  renderPreview(window.resumeState, window.currentTemplate);
}

function updateLang(idx, field, val) {
  window.resumeState.languages[idx][field] = val;
  renderPreview(window.resumeState, window.currentTemplate);
}

// ACTIONS
async function saveResume() {
  const saveBtn = document.getElementById("saveResumeBtn");
  if (saveBtn) {
    saveBtn.disabled = true;
    saveBtn.innerHTML = `<span class="spinner"></span> Saving...`;
  }

  try {
    const res = await fetch(`/api/resumes/${window.resumeId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        data: window.resumeState,
        template: window.currentTemplate
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast("Resume saved successfully!", "success");
    } else {
      showToast("Failed to save resume: " + (data.error || "Unknown error"), "error");
    }
  } catch (err) {
    showToast("Network error saving resume", "error");
  } finally {
    if (saveBtn) {
      saveBtn.disabled = false;
      saveBtn.innerHTML = `💾 Save Resume`;
    }
  }
}

async function saveResumeTitle(newTitle) {
  if (!newTitle.trim()) return;
  try {
    await fetch(`/api/resumes/${window.resumeId}/rename`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: newTitle.trim() })
    });
    showToast("Resume title updated", "success");
  } catch (err) {
    console.error(err);
  }
}

function downloadPdf() {
  window.location.href = `/api/resumes/${window.resumeId}/pdf?template=${window.currentTemplate}`;
}

function printResume() {
  window.print();
}

function loadSampleData() {
  if (!confirm("This will load comprehensive sample resume data into a new resume. Continue?")) return;
  fetch("/api/resumes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: "Sneha Sai - Software Developer", load_sample: true })
  })
  .then(res => res.json())
  .then(resp => {
    if (resp.success) {
      window.location.href = `/editor?id=${resp.resume.id}`;
    }
  });
}
