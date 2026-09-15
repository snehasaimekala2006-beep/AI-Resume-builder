/**
 * AI Operations Controller for AI Resume Builder
 * Enforces strict User Review Workflow: AI output is never auto-applied without approval.
 */

let pendingAIApplyCallback = null;

// Open Universal AI Review Modal
function openAIReviewModal(title, initialContent, onApply) {
  const modal = document.getElementById("aiReviewModal");
  const modalTitle = document.getElementById("aiReviewModalTitle");
  const modalContent = document.getElementById("aiReviewContent");
  const loadingBox = document.getElementById("aiReviewLoading");
  const contentBox = document.getElementById("aiReviewContentBox");
  const applyBtn = document.getElementById("aiReviewApplyBtn");

  if (!modal) return;

  modalTitle.textContent = title || "AI Generated Content";
  pendingAIApplyCallback = onApply;

  // If initialContent is null, show loading spinner
  if (initialContent === null) {
    loadingBox.style.display = "flex";
    contentBox.style.display = "none";
    applyBtn.disabled = true;
  } else {
    loadingBox.style.display = "none";
    contentBox.style.display = "block";
    modalContent.value = initialContent;
    applyBtn.disabled = false;
  }

  modal.classList.add("active");
}

function updateAIReviewModalContent(content) {
  const loadingBox = document.getElementById("aiReviewLoading");
  const contentBox = document.getElementById("aiReviewContentBox");
  const modalContent = document.getElementById("aiReviewContent");
  const applyBtn = document.getElementById("aiReviewApplyBtn");

  loadingBox.style.display = "none";
  contentBox.style.display = "block";
  modalContent.value = content || "";
  applyBtn.disabled = false;
}

function closeAIReviewModal() {
  const modal = document.getElementById("aiReviewModal");
  if (modal) modal.classList.remove("active");
  pendingAIApplyCallback = null;
}

function applyAIReviewContent() {
  const modalContent = document.getElementById("aiReviewContent");
  const text = modalContent ? modalContent.value : "";
  if (pendingAIApplyCallback) {
    pendingAIApplyCallback(text);
    showToast("✓ Applied to resume successfully!", "success");
  }
  closeAIReviewModal();
}

function editAIReviewContent() {
  const modalContent = document.getElementById("aiReviewContent");
  if (modalContent) {
    modalContent.focus();
    modalContent.select();
  }
}

// -------------------------------------------------------------
// Section AI Triggers
// -------------------------------------------------------------

// Summary
async function triggerSummaryGenerate() {
  openAIReviewModal("AI Generated Professional Summary", null, (finalText) => {
    window.resumeState.summary = finalText;
    const el = document.getElementById("summary_text");
    if (el) el.value = finalText;
    renderPreview(window.resumeState, window.currentTemplate);
  });

  try {
    const res = await fetch("/api/ai/generate-summary", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: window.resumeState })
    });
    const data = await res.json();
    if (data.success) {
      updateAIReviewModalContent(data.content);
    } else {
      updateAIReviewModalContent("Unable to generate content. Please try again.");
    }
  } catch (err) {
    updateAIReviewModalContent("Network error generating summary. Please check your connection.");
  }
}

async function triggerSummaryStyle(style) {
  const cur = (window.resumeState.summary || document.getElementById("summary_text")?.value || "").trim();
  if (!cur) {
    showToast("Please enter some summary notes first.", "error");
    return;
  }

  const styleTitles = {
    improve: "AI Improved Summary",
    professional: "AI Executive Summary",
    ats: "AI ATS-Friendly Summary",
    shorten: "AI Shortened Summary",
    expand: "AI Expanded Summary",
    rewrite: "AI Rewritten Summary"
  };

  openAIReviewModal(styleTitles[style] || "AI Enhanced Summary", null, (finalText) => {
    window.resumeState.summary = finalText;
    const el = document.getElementById("summary_text");
    if (el) el.value = finalText;
    renderPreview(window.resumeState, window.currentTemplate);
  });

  try {
    const res = await fetch("/api/ai/improve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: cur, style: style })
    });
    const data = await res.json();
    if (data.success) {
      updateAIReviewModalContent(data.content);
    } else {
      updateAIReviewModalContent("Unable to enhance text. Please try again.");
    }
  } catch (err) {
    updateAIReviewModalContent("Network error. Please try again.");
  }
}

// Experience
async function triggerExpAIDescription(idx) {
  const exp = window.resumeState.experience[idx] || {};
  openAIReviewModal("AI Generated Experience Description", null, (finalText) => {
    window.resumeState.experience[idx].description = finalText;
    const el = document.getElementById(`exp_desc_${idx}`);
    if (el) el.value = finalText;
    renderPreview(window.resumeState, window.currentTemplate);
  });

  try {
    const res = await fetch("/api/ai/generate-description", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ section: "experience", data: exp })
    });
    const data = await res.json();
    if (data.success) {
      updateAIReviewModalContent(data.content);
    } else {
      updateAIReviewModalContent("Unable to generate bullet points. Please try again.");
    }
  } catch (err) {
    updateAIReviewModalContent("Network error generating experience bullets.");
  }
}

async function triggerExpStyle(idx, style) {
  const cur = (window.resumeState.experience[idx]?.description || "").trim();
  if (!cur) {
    showToast("Please enter or generate a description first.", "error");
    return;
  }

  openAIReviewModal(`AI ${style.toUpperCase()} Experience Bullets`, null, (finalText) => {
    window.resumeState.experience[idx].description = finalText;
    const el = document.getElementById(`exp_desc_${idx}`);
    if (el) el.value = finalText;
    renderPreview(window.resumeState, window.currentTemplate);
  });

  try {
    const res = await fetch("/api/ai/improve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: cur, style: style })
    });
    const data = await res.json();
    if (data.success) {
      updateAIReviewModalContent(data.content);
    } else {
      updateAIReviewModalContent("Unable to transform text.");
    }
  } catch (err) {
    updateAIReviewModalContent("Network error.");
  }
}

// Projects
async function triggerProjAIDescription(idx) {
  const proj = window.resumeState.projects[idx] || {};
  openAIReviewModal("AI Generated Project Description", null, (finalText) => {
    window.resumeState.projects[idx].description = finalText;
    const el = document.getElementById(`proj_desc_${idx}`);
    if (el) el.value = finalText;
    renderPreview(window.resumeState, window.currentTemplate);
  });

  try {
    const res = await fetch("/api/ai/generate-description", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ section: "project", data: proj })
    });
    const data = await res.json();
    if (data.success) {
      updateAIReviewModalContent(data.content);
    } else {
      updateAIReviewModalContent("Unable to generate project description.");
    }
  } catch (err) {
    updateAIReviewModalContent("Network error generating project description.");
  }
}

async function triggerProjStyle(idx, style) {
  const cur = (window.resumeState.projects[idx]?.description || "").trim();
  if (!cur) {
    showToast("Please enter or generate a project description first.", "error");
    return;
  }

  openAIReviewModal(`AI ${style.toUpperCase()} Project Description`, null, (finalText) => {
    window.resumeState.projects[idx].description = finalText;
    const el = document.getElementById(`proj_desc_${idx}`);
    if (el) el.value = finalText;
    renderPreview(window.resumeState, window.currentTemplate);
  });

  try {
    const res = await fetch("/api/ai/improve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: cur, style: style })
    });
    const data = await res.json();
    if (data.success) {
      updateAIReviewModalContent(data.content);
    } else {
      updateAIReviewModalContent("Unable to transform text.");
    }
  } catch (err) {
    updateAIReviewModalContent("Network error.");
  }
}

// Education Description
async function triggerEduAIDescription(idx) {
  const edu = window.resumeState.education[idx] || {};
  openAIReviewModal("AI Generated Education Highlights", null, (finalText) => {
    window.resumeState.education[idx].description = finalText;
    renderEducationCards();
    renderPreview(window.resumeState, window.currentTemplate);
  });

  try {
    const res = await fetch("/api/ai/generate-description", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ section: "education", data: edu })
    });
    const data = await res.json();
    if (data.success) {
      updateAIReviewModalContent(data.content);
    } else {
      updateAIReviewModalContent("Unable to generate academic highlights.");
    }
  } catch (err) {
    updateAIReviewModalContent("Network error.");
  }
}

// Certifications Description
async function triggerCertAIDescription(idx) {
  const cert = window.resumeState.certifications[idx] || {};
  openAIReviewModal("AI Generated Certification Description", null, (finalText) => {
    window.resumeState.certifications[idx].description = finalText;
    renderCertificationCards();
    renderPreview(window.resumeState, window.currentTemplate);
  });

  try {
    const res = await fetch("/api/ai/generate-description", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ section: "certification", data: cert })
    });
    const data = await res.json();
    if (data.success) {
      updateAIReviewModalContent(data.content);
    } else {
      updateAIReviewModalContent("Unable to generate certification details.");
    }
  } catch (err) {
    updateAIReviewModalContent("Network error.");
  }
}

// Achievements Description
async function triggerAchAIDescription(idx) {
  const ach = window.resumeState.achievements[idx] || {};
  openAIReviewModal("AI Improved Achievement", null, (finalText) => {
    window.resumeState.achievements[idx].description = finalText;
    renderAchievementCards();
    renderPreview(window.resumeState, window.currentTemplate);
  });

  try {
    const res = await fetch("/api/ai/generate-description", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ section: "achievement", data: ach })
    });
    const data = await res.json();
    if (data.success) {
      updateAIReviewModalContent(data.content);
    } else {
      updateAIReviewModalContent("Unable to improve achievement.");
    }
  } catch (err) {
    updateAIReviewModalContent("Network error.");
  }
}

// Internships Description
async function triggerInternAIDescription(idx) {
  const intern = window.resumeState.internships[idx] || {};
  openAIReviewModal("AI Generated Internship Bullets", null, (finalText) => {
    window.resumeState.internships[idx].description = finalText;
    renderInternshipCards();
    renderPreview(window.resumeState, window.currentTemplate);
  });

  try {
    const res = await fetch("/api/ai/generate-description", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ section: "internship", data: intern })
    });
    const data = await res.json();
    if (data.success) {
      updateAIReviewModalContent(data.content);
    } else {
      updateAIReviewModalContent("Unable to generate internship bullets.");
    }
  } catch (err) {
    updateAIReviewModalContent("Network error.");
  }
}

// -------------------------------------------------------------
// Suggest Skills (Clearly Marked as Suggestions)
// -------------------------------------------------------------
async function triggerSuggestSkills() {
  const btn = document.getElementById("suggestSkillsBtn");
  const container = document.getElementById("skillSuggestionsContainer");
  if (!container) return;

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner spinner-purple"></span> Suggesting...`;
  }

  try {
    const res = await fetch("/api/ai/suggest-skills", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume: window.resumeState })
    });
    const data = await res.json();
    if (data.success && data.suggestions) {
      renderSkillSuggestions(data.suggestions);
      showToast("✨ AI suggested relevant skills for review", "ai");
    } else {
      showToast("Unable to suggest skills at this moment", "error");
    }
  } catch (err) {
    showToast("Network error suggesting skills", "error");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `✨ Suggest Skills`;
    }
  }
}

function renderSkillSuggestions(suggestions) {
  const container = document.getElementById("skillSuggestionsContainer");
  if (!container) return;

  let html = `
    <div class="skill-suggestion-box">
      <div class="skill-suggestion-title">
        <span>✨ AI Recommended Skills (Click '+' to add to your resume)</span>
      </div>
      <div style="display:flex; flex-wrap:wrap; gap:0.4rem;">
  `;

  let totalPills = 0;
  Object.keys(suggestions).forEach(catKey => {
    const list = suggestions[catKey] || [];
    list.forEach(skill => {
      // Check if user already has this skill
      const existing = window.resumeState.skills[catKey] || [];
      if (!existing.includes(skill)) {
        totalPills++;
        html += `
          <span class="suggestion-pill" onclick="acceptSkillSuggestion('${catKey}', '${escapeHtml(skill)}')">
            + ${escapeHtml(skill)} <small style="opacity:0.75;">(${catKey})</small>
          </span>
        `;
      }
    });
  });

  if (totalPills === 0) {
    html += `<span style="font-size:0.75rem; color:var(--text-muted);">No new skill suggestions at this time.</span>`;
  }

  html += `</div></div>`;
  container.innerHTML = html;
  container.style.display = "block";
}

function acceptSkillSuggestion(catKey, skillName) {
  if (!window.resumeState.skills[catKey]) window.resumeState.skills[catKey] = [];
  if (!window.resumeState.skills[catKey].includes(skillName)) {
    window.resumeState.skills[catKey].push(skillName);
    renderSkillsUI();
    renderPreview(window.resumeState, window.currentTemplate);
    showToast(`Added ${skillName} to ${catKey}`, "success");
  }
}

// -------------------------------------------------------------
// Complete Resume AI: "Build My Resume with AI"
// -------------------------------------------------------------
let parsedCandidateResume = null;

function openFullResumeModal() {
  const modal = document.getElementById("fullResumeModal");
  const rawInput = document.getElementById("fullResumeRawText");
  const reviewStage = document.getElementById("fullResumeReviewStage");
  const inputStage = document.getElementById("fullResumeInputStage");
  const applyBtn = document.getElementById("fullResumeApplyBtn");

  if (!modal) return;
  if (rawInput) rawInput.value = "";
  if (inputStage) inputStage.style.display = "block";
  if (reviewStage) reviewStage.style.display = "none";
  if (applyBtn) applyBtn.style.display = "none";

  parsedCandidateResume = null;
  modal.classList.add("active");
}

function closeFullResumeModal() {
  const modal = document.getElementById("fullResumeModal");
  if (modal) modal.classList.remove("active");
  parsedCandidateResume = null;
}

async function processFullResumeAI() {
  const rawInput = document.getElementById("fullResumeRawText");
  const rawText = rawInput ? rawInput.value.trim() : "";
  if (!rawText) {
    showToast("Please enter your career or educational details.", "error");
    return;
  }

  const btn = document.getElementById("fullResumeSubmitBtn");
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> ✨ AI is organizing your resume...`;
  }

  try {
    const res = await fetch("/api/ai/generate-resume", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw_text: rawText })
    });
    const data = await res.json();
    if (data.success && data.resume) {
      parsedCandidateResume = data.resume;
      displayFullResumeReview(data.resume);
    } else {
      showToast(data.error || "Unable to parse resume details.", "error");
    }
  } catch (err) {
    showToast("Network error parsing resume.", "error");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `✨ Process & Review Resume`;
    }
  }
}

function displayFullResumeReview(resume) {
  const inputStage = document.getElementById("fullResumeInputStage");
  const reviewStage = document.getElementById("fullResumeReviewStage");
  const applyBtn = document.getElementById("fullResumeApplyBtn");
  const checklist = document.getElementById("fullResumeChecklist");

  if (inputStage) inputStage.style.display = "none";
  if (reviewStage) reviewStage.style.display = "block";
  if (applyBtn) applyBtn.style.display = "inline-flex";

  const p = resume.personal || {};
  const eduCount = (resume.education || []).length;
  const expCount = (resume.experience || []).length;
  const projCount = (resume.projects || []).length;
  const certCount = (resume.certifications || []).length;
  const internCount = (resume.internships || []).length;

  let totalSkills = 0;
  if (resume.skills) {
    Object.values(resume.skills).forEach(list => {
      if (Array.isArray(list)) totalSkills += list.length;
    });
  }

  checklist.innerHTML = `
    <div style="background:#f8fafc; border:1px solid var(--border-color); border-radius:var(--radius-md); padding:1rem; margin-bottom:1rem;">
      <h4 style="font-size:0.95rem; font-weight:700; margin-bottom:0.6rem;">AI Extracted Structured Sections:</h4>
      <ul style="list-style:none; display:flex; flex-direction:column; gap:0.4rem; font-size:0.85rem;">
        <li><span style="color:var(--success); font-weight:bold;">✓</span> <strong>Personal Information:</strong> ${escapeHtml(p.name || 'Candidate')} (${escapeHtml(p.title || 'Developer')})</li>
        <li><span style="color:var(--success); font-weight:bold;">✓</span> <strong>Professional Summary:</strong> ${resume.summary ? 'Created' : 'Not detected'}</li>
        <li><span style="color:var(--success); font-weight:bold;">✓</span> <strong>Education:</strong> ${eduCount} degree(s) identified</li>
        <li><span style="color:var(--success); font-weight:bold;">✓</span> <strong>Skills:</strong> ${totalSkills} skill(s) categorized</li>
        <li><span style="color:var(--success); font-weight:bold;">✓</span> <strong>Projects:</strong> ${projCount} project(s) extracted</li>
        <li><span style="color:var(--success); font-weight:bold;">✓</span> <strong>Experience / Internships:</strong> ${expCount + internCount} item(s) found</li>
        <li><span style="color:var(--success); font-weight:bold;">✓</span> <strong>Certifications:</strong> ${certCount} certification(s)</li>
      </ul>
      <p style="font-size:0.78rem; color:var(--text-muted); margin-top:0.75rem;">
        Click <strong>Apply to Resume</strong> to populate the editor. You will still be able to review and fine-tune every field.
      </p>
    </div>
  `;
}

function applyFullResumeToState() {
  if (!parsedCandidateResume) return;

  // Apply parsed data to window.resumeState
  window.resumeState = parsedCandidateResume;
  populateFormFromState();
  renderPreview(window.resumeState, window.currentTemplate);

  closeFullResumeModal();
  showToast("✓ Complete resume parsed and applied successfully!", "success");
}
