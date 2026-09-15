/**
 * ATS Job Optimization & Analysis Controller
 */

function openAtsModal() {
  const modal = document.getElementById("atsModal");
  if (!modal) return;
  modal.classList.add("active");
}

function closeAtsModal() {
  const modal = document.getElementById("atsModal");
  if (!modal) return;
  modal.classList.remove("active");
}

async function analyzeJobDescription() {
  const input = document.getElementById("jobDescInput");
  const jobText = input ? input.value.trim() : "";
  if (!jobText) {
    showToast("Please paste a job description first.", "error");
    return;
  }

  const btn = document.getElementById("atsAnalyzeBtn");
  const resultsContainer = document.getElementById("atsResultsContainer");

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner spinner-purple"></span> ✨ AI is analyzing keywords...`;
  }

  try {
    const res = await fetch("/api/ai/analyze-job", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume: window.resumeState,
        job_description: jobText
      })
    });
    const data = await res.json();
    if (data.success) {
      renderAtsResults(data);
      resultsContainer.style.display = "block";
      showToast("✓ ATS Analysis complete!", "success");
    } else {
      showToast(data.error || "Analysis failed. Please try again.", "error");
    }
  } catch (err) {
    showToast("Network error performing ATS analysis.", "error");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `Analyze Resume`;
    }
  }
}

function renderAtsResults(results) {
  const container = document.getElementById("atsResultsContainer");
  if (!container) return;

  const score = results.ats_score || 75;
  const kwMatch = results.keyword_match || 80;
  const skMatch = results.skills_match || 75;
  const expMatch = results.experience_match || 70;
  const structMatch = results.structure_score || 90;

  // Render suggestions
  const suggestionsHtml = (results.suggestions || []).map(s => {
    const icon = s.type === "positive" ? "✓" : "⚠";
    const className = s.type === "positive" ? "positive" : "warning";
    return `
      <div class="ats-suggestion-item ${className}">
        <span style="font-weight:bold; font-size:1rem;">${icon}</span>
        <div>${escapeHtml(s.text)}</div>
      </div>
    `;
  }).join("");

  container.innerHTML = `
    <div class="ats-score-display">
      <div class="ats-score-circle" style="--score-pct: ${score}%;">
        <div class="ats-score-inner">
          <div class="ats-score-num">${score}</div>
          <div class="ats-score-denom">/ 100</div>
        </div>
      </div>
      <div class="ats-metrics-grid">
        <div class="ats-metric-item">
          <span class="ats-metric-label">Keyword Match</span>
          <span class="ats-metric-val">${kwMatch}%</span>
        </div>
        <div class="ats-metric-item">
          <span class="ats-metric-label">Skills Match</span>
          <span class="ats-metric-val">${skMatch}%</span>
        </div>
        <div class="ats-metric-item">
          <span class="ats-metric-label">Experience Match</span>
          <span class="ats-metric-val">${expMatch}%</span>
        </div>
        <div class="ats-metric-item">
          <span class="ats-metric-label">Resume Structure</span>
          <span class="ats-metric-val">${structMatch}%</span>
        </div>
      </div>
    </div>

    <h4 style="font-size:0.95rem; font-weight:700; margin-bottom:0.75rem; color:var(--text-main);">ATS Suggestions & Insights:</h4>
    <div style="display:flex; flex-direction:column; gap:0.4rem;">
      ${suggestionsHtml}
    </div>
  `;
}
