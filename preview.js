/**
 * Live Preview Engine for AI Resume Builder
 * Dynamically renders state onto the A4 Resume Sheet.
 */

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatBullets(text) {
  if (!text) return "";
  const lines = text.split("\n").map(l => l.trim()).filter(l => l.length > 0);
  if (lines.length === 0) return "";
  
  const isBulletList = lines.some(l => l.startsWith("•") || l.startsWith("-") || l.startsWith("*"));
  if (isBulletList || lines.length > 1) {
    const items = lines.map(line => {
      const clean = escapeHtml(line.replace(/^[•\-\*\d\.]+\s*/, ""));
      return `<li>${clean}</li>`;
    }).join("");
    return `<ul class="resume-bullet-list">${items}</ul>`;
  }
  return `<p>${escapeHtml(text)}</p>`;
}

function renderPreview(data, templateName = "classic") {
  const container = document.getElementById("resumePreviewContainer");
  if (!container) return;

  // Apply template class
  container.className = `resume-sheet template-${templateName}`;

  const p = data.personal || {};
  const name = escapeHtml(p.name || "Your Name");
  const title = escapeHtml(p.title || "");

  // Contact list
  const contacts = [];
  if (p.email) contacts.push(`<span class="resume-contact-item">✉️ ${escapeHtml(p.email)}</span>`);
  if (p.phone) contacts.push(`<span class="resume-contact-item">📞 ${escapeHtml(p.phone)}</span>`);
  if (p.location) contacts.push(`<span class="resume-contact-item">📍 ${escapeHtml(p.location)}</span>`);
  if (p.linkedin) contacts.push(`<span class="resume-contact-item">🔗 <a href="${escapeHtml(p.linkedin)}" target="_blank">${escapeHtml(p.linkedin.replace(/^https?:\/\//, ''))}</a></span>`);
  if (p.github) contacts.push(`<span class="resume-contact-item">💻 <a href="${escapeHtml(p.github)}" target="_blank">${escapeHtml(p.github.replace(/^https?:\/\//, ''))}</a></span>`);
  if (p.portfolio) contacts.push(`<span class="resume-contact-item">🌐 <a href="${escapeHtml(p.portfolio)}" target="_blank">${escapeHtml(p.portfolio.replace(/^https?:\/\//, ''))}</a></span>`);

  let html = `
    <header class="resume-header">
      <h1 class="resume-name">${name}</h1>
      ${title ? `<div class="resume-title">${title}</div>` : ""}
      ${contacts.length > 0 ? `<div class="resume-contact-bar">${contacts.join("")}</div>` : ""}
    </header>
  `;

  // Summary
  if (data.summary && data.summary.trim()) {
    html += `
      <section class="resume-section">
        <h2 class="resume-section-title">Professional Summary</h2>
        <div class="resume-item-body">${escapeHtml(data.summary)}</div>
      </section>
    `;
  }

  // Experience
  if (data.experience && data.experience.length > 0) {
    const validExp = data.experience.filter(e => e.jobTitle || e.company);
    if (validExp.length > 0) {
      const expItems = validExp.map(e => {
        const eDate = e.currentlyWorking ? "Present" : escapeHtml(e.endDate || "");
        const dates = [escapeHtml(e.startDate || ""), eDate].filter(Boolean).join(" - ");
        const sub = [escapeHtml(e.company || ""), escapeHtml(e.location || "")].filter(Boolean).join(" | ");
        const bodyContent = e.description || e.responsibilities || "";
        return `
          <div class="resume-item">
            <div class="resume-item-header">
              <div>
                <span class="resume-item-title">${escapeHtml(e.jobTitle || "")}</span>
                ${sub ? `<span class="resume-item-subtitle"> — ${sub}</span>` : ""}
              </div>
              ${dates ? `<span class="resume-item-date">${dates}</span>` : ""}
            </div>
            ${bodyContent ? `<div class="resume-item-body">${formatBullets(bodyContent)}</div>` : ""}
          </div>
        `;
      }).join("");

      html += `
        <section class="resume-section">
          <h2 class="resume-section-title">Experience</h2>
          ${expItems}
        </section>
      `;
    }
  }

  // Education
  if (data.education && data.education.length > 0) {
    const validEdu = data.education.filter(e => e.degree || e.university);
    if (validEdu.length > 0) {
      const eduItems = validEdu.map(e => {
        const dates = [escapeHtml(e.startYear || ""), escapeHtml(e.endYear || "")].filter(Boolean).join(" - ");
        const sub = [escapeHtml(e.university || ""), escapeHtml(e.location || "")].filter(Boolean).join(" | ");
        return `
          <div class="resume-item">
            <div class="resume-item-header">
              <div>
                <span class="resume-item-title">${escapeHtml(e.degree || "")}</span>
                ${sub ? `<span class="resume-item-subtitle"> — ${sub}</span>` : ""}
              </div>
              ${dates ? `<span class="resume-item-date">${dates}</span>` : ""}
            </div>
            ${e.gpa ? `<div class="resume-item-subtitle" style="font-size:8.5pt;"><strong>GPA:</strong> ${escapeHtml(e.gpa)}</div>` : ""}
            ${e.description ? `<div class="resume-item-body" style="margin-top:2pt;">${escapeHtml(e.description)}</div>` : ""}
          </div>
        `;
      }).join("");

      html += `
        <section class="resume-section">
          <h2 class="resume-section-title">Education</h2>
          ${eduItems}
        </section>
      `;
    }
  }

  // Projects
  if (data.projects && data.projects.length > 0) {
    const validProj = data.projects.filter(p => p.name);
    if (validProj.length > 0) {
      const projItems = validProj.map(p => {
        const link = p.projectUrl || p.githubUrl || "";
        const bodyContent = p.description || p.rawDescription || "";
        return `
          <div class="resume-item">
            <div class="resume-item-header">
              <div>
                <span class="resume-item-title">${escapeHtml(p.name)}</span>
                ${p.technologies ? `<span class="resume-item-subtitle"> | <em>${escapeHtml(p.technologies)}</em></span>` : ""}
              </div>
              ${link ? `<span class="resume-item-date"><a href="${escapeHtml(link)}" target="_blank" style="color:inherit;text-decoration:none;">🔗 Link</a></span>` : ""}
            </div>
            ${bodyContent ? `<div class="resume-item-body">${formatBullets(bodyContent)}</div>` : ""}
          </div>
        `;
      }).join("");

      html += `
        <section class="resume-section">
          <h2 class="resume-section-title">Projects</h2>
          ${projItems}
        </section>
      `;
    }
  }

  // Skills
  const s = data.skills || {};
  const skillCategories = [
    { label: "Programming Languages", list: s.programming },
    { label: "Frameworks & Libraries", list: s.frameworks },
    { label: "Web Technologies", list: s.web },
    { label: "Databases", list: s.databases },
    { label: "Tools & Platforms", list: s.tools },
    { label: "Soft Skills", list: s.soft }
  ].filter(c => c.list && c.list.length > 0);

  if (skillCategories.length > 0) {
    const skillRows = skillCategories.map(c => `
      <div class="resume-skill-row">
        <span class="resume-skill-label">${escapeHtml(c.label)}:</span>
        <span class="resume-skill-list">${escapeHtml(c.list.join(", "))}</span>
      </div>
    `).join("");

    html += `
      <section class="resume-section">
        <h2 class="resume-section-title">Skills</h2>
        <div class="resume-skills-grid">
          ${skillRows}
        </div>
      </section>
    `;
  }

  // Internships
  if (data.internships && data.internships.length > 0) {
    const validIntern = data.internships.filter(i => i.organization || i.role);
    if (validIntern.length > 0) {
      const internItems = validIntern.map(i => {
        const bodyContent = i.description || i.responsibilities || "";
        return `
          <div class="resume-item">
            <div class="resume-item-header">
              <div>
                <span class="resume-item-title">${escapeHtml(i.role || "Intern")}</span>
                ${i.organization ? `<span class="resume-item-subtitle"> — ${escapeHtml(i.organization)}</span>` : ""}
              </div>
              ${i.duration ? `<span class="resume-item-date">${escapeHtml(i.duration)}</span>` : ""}
            </div>
            ${bodyContent ? `<div class="resume-item-body">${formatBullets(bodyContent)}</div>` : ""}
          </div>
        `;
      }).join("");

      html += `
        <section class="resume-section">
          <h2 class="resume-section-title">Internships</h2>
          ${internItems}
        </section>
      `;
    }
  }

  // Certifications
  if (data.certifications && data.certifications.length > 0) {
    const validCert = data.certifications.filter(c => c.name);
    if (validCert.length > 0) {
      const certItems = validCert.map(c => `
        <div class="resume-item">
          <div class="resume-item-header">
            <div>
              <span class="resume-item-title">${escapeHtml(c.name)}</span>
              ${c.issuer ? `<span class="resume-item-subtitle"> — ${escapeHtml(c.issuer)}</span>` : ""}
            </div>
            ${c.date ? `<span class="resume-item-date">${escapeHtml(c.date)}</span>` : ""}
          </div>
          ${c.description ? `<div class="resume-item-body">${escapeHtml(c.description)}</div>` : ""}
        </div>
      `).join("");

      html += `
        <section class="resume-section">
          <h2 class="resume-section-title">Certifications</h2>
          ${certItems}
        </section>
      `;
    }
  }

  // Achievements
  if (data.achievements && data.achievements.length > 0) {
    const validAch = data.achievements.filter(a => a.title);
    if (validAch.length > 0) {
      const achItems = validAch.map(a => `
        <div class="resume-item">
          <div class="resume-item-header">
            <span class="resume-item-title">${escapeHtml(a.title)}</span>
            ${a.date ? `<span class="resume-item-date">${escapeHtml(a.date)}</span>` : ""}
          </div>
          ${a.description ? `<div class="resume-item-body">${escapeHtml(a.description)}</div>` : ""}
        </div>
      `).join("");

      html += `
        <section class="resume-section">
          <h2 class="resume-section-title">Achievements</h2>
          ${achItems}
        </section>
      `;
    }
  }

  // Languages
  if (data.languages && data.languages.length > 0) {
    const validLang = data.languages.filter(l => l.language);
    if (validLang.length > 0) {
      const langItems = validLang.map(l => {
        return l.proficiency ? `<strong>${escapeHtml(l.language)}</strong> (${escapeHtml(l.proficiency)})` : `<strong>${escapeHtml(l.language)}</strong>`;
      }).join(" &nbsp;|&nbsp; ");

      html += `
        <section class="resume-section">
          <h2 class="resume-section-title">Languages</h2>
          <div class="resume-item-body">${langItems}</div>
        </section>
      `;
    }
  }

  container.innerHTML = html;
}
