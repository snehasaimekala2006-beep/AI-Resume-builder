import io
import html
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether

TEMPLATE_PALETTES = {
    "classic": {"primary": colors.HexColor("#1e293b"), "accent": colors.HexColor("#475569"), "line": colors.HexColor("#cbd5e1")},
    "modern": {"primary": colors.HexColor("#1e40af"), "accent": colors.HexColor("#3b82f6"), "line": colors.HexColor("#93c5fd")},
    "minimal": {"primary": colors.HexColor("#111827"), "accent": colors.HexColor("#6b7280"), "line": colors.HexColor("#e5e7eb")},
    "fresher": {"primary": colors.HexColor("#0f766e"), "accent": colors.HexColor("#0d9488"), "line": colors.HexColor("#99f6e4")},
    "executive": {"primary": colors.HexColor("#1e1b4b"), "accent": colors.HexColor("#4338ca"), "line": colors.HexColor("#c7d2fe")},
}

def clean_txt(text):
    if not text:
        return ""
    # Escape XML entities for ReportLab Paragraphs
    t = html.escape(str(text).strip())
    # replace newlines with linebreaks
    t = t.replace("\n", "<br/>")
    return t

def generate_pdf(resume_data, template_name="classic"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    palette = TEMPLATE_PALETTES.get(template_name, TEMPLATE_PALETTES["classic"])
    styles = getSampleStyleSheet()

    # Custom typography styles
    style_name = ParagraphStyle(
        "ResumeName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=palette["primary"],
        alignment=0 if template_name != "minimal" else 1
    )
    style_title = ParagraphStyle(
        "ResumeTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=15,
        textColor=palette["accent"],
        alignment=0 if template_name != "minimal" else 1
    )
    style_contact = ParagraphStyle(
        "ResumeContact",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#4b5563"),
        alignment=0 if template_name != "minimal" else 1
    )
    style_heading = ParagraphStyle(
        "ResumeHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=palette["primary"],
        spaceBefore=8,
        spaceAfter=4
    )
    style_subheading = ParagraphStyle(
        "ResumeSubHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor("#1f2937")
    )
    style_date = ParagraphStyle(
        "ResumeDate",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#6b7280"),
        alignment=2 # Right
    )
    style_body = ParagraphStyle(
        "ResumeBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#374151")
    )
    style_bullet = ParagraphStyle(
        "ResumeBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#374151"),
        leftIndent=12
    )

    story = []

    # 1. Header (Personal Info)
    p = resume_data.get("personal", {})
    name = clean_txt(p.get("name") or "Your Name")
    title = clean_txt(p.get("title") or "")
    
    contact_parts = []
    if p.get("email"): contact_parts.append(clean_txt(p["email"]))
    if p.get("phone"): contact_parts.append(clean_txt(p["phone"]))
    if p.get("location"): contact_parts.append(clean_txt(p["location"]))
    if p.get("linkedin"): contact_parts.append(clean_txt(p["linkedin"]))
    if p.get("github"): contact_parts.append(clean_txt(p["github"]))
    if p.get("portfolio"): contact_parts.append(clean_txt(p["portfolio"]))
    contact_line = " &nbsp;|&nbsp; ".join(contact_parts)

    story.append(Paragraph(name, style_name))
    if title:
        story.append(Spacer(1, 2))
        story.append(Paragraph(title, style_title))
    if contact_line:
        story.append(Spacer(1, 4))
        story.append(Paragraph(contact_line, style_contact))

    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=palette["line"], spaceBefore=2, spaceAfter=8))

    def add_section_header(title_text):
        story.append(Paragraph(title_text.upper(), style_heading))
        story.append(HRFlowable(width="100%", thickness=0.8, color=palette["line"], spaceBefore=1, spaceAfter=5))

    # 2. Summary
    summary = clean_txt(resume_data.get("summary", ""))
    if summary:
        add_section_header("Professional Summary")
        story.append(Paragraph(summary, style_body))
        story.append(Spacer(1, 6))

    # 3. Experience
    experiences = resume_data.get("experience", [])
    if experiences:
        add_section_header("Experience")
        for exp in experiences:
            job_title = clean_txt(exp.get("jobTitle", ""))
            company = clean_txt(exp.get("company", ""))
            loc = clean_txt(exp.get("location", ""))
            s_date = clean_txt(exp.get("startDate", ""))
            e_date = "Present" if exp.get("currentlyWorking") else clean_txt(exp.get("endDate", ""))
            date_range = f"{s_date} - {e_date}" if s_date or e_date else ""
            
            left_text = f"<b>{job_title}</b>" + (f" — {company}" if company else "") + (f" ({loc})" if loc else "")
            header_table = Table(
                [[Paragraph(left_text, style_subheading), Paragraph(date_range, style_date)]],
                colWidths=[380, 140]
            )
            header_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
            ]))
            story.append(header_table)

            desc = exp.get("description") or exp.get("responsibilities") or ""
            if desc:
                for line in desc.split("\n"):
                    line_c = clean_txt(line)
                    if line_c:
                        bullet_clean = line_c.lstrip("•-* ")
                        story.append(Paragraph(f"• {bullet_clean}", style_bullet))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 4))

    # 4. Education
    education = resume_data.get("education", [])
    if education:
        add_section_header("Education")
        for edu in education:
            degree = clean_txt(edu.get("degree", ""))
            univ = clean_txt(edu.get("university", ""))
            loc = clean_txt(edu.get("location", ""))
            s_yr = clean_txt(edu.get("startYear", ""))
            e_yr = clean_txt(edu.get("endYear", ""))
            yr_str = f"{s_yr} - {e_yr}" if s_yr and e_yr else (s_yr or e_yr)
            gpa = clean_txt(edu.get("gpa", ""))
            
            left_text = f"<b>{degree}</b>" + (f", {univ}" if univ else "") + (f" ({loc})" if loc else "")
            header_table = Table(
                [[Paragraph(left_text, style_subheading), Paragraph(yr_str, style_date)]],
                colWidths=[380, 140]
            )
            header_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
            ]))
            story.append(header_table)
            if gpa:
                story.append(Paragraph(f"<b>GPA:</b> {gpa}", style_body))
            if edu.get("description"):
                story.append(Paragraph(clean_txt(edu["description"]), style_body))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 4))

    # 5. Projects
    projects = resume_data.get("projects", [])
    if projects:
        add_section_header("Projects")
        for proj in projects:
            p_name = clean_txt(proj.get("name", ""))
            tech = clean_txt(proj.get("technologies", ""))
            url = clean_txt(proj.get("projectUrl") or proj.get("githubUrl") or "")
            
            left_text = f"<b>{p_name}</b>" + (f" | <i>{tech}</i>" if tech else "")
            header_table = Table(
                [[Paragraph(left_text, style_subheading), Paragraph(url, style_date)]],
                colWidths=[380, 140]
            )
            header_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
            ]))
            story.append(header_table)
            desc = clean_txt(proj.get("description") or proj.get("rawDescription") or "")
            if desc:
                for line in desc.split("<br/>"):
                    line_c = line.strip()
                    if line_c:
                        bullet_c = line_c.lstrip("•-* ")
                        story.append(Paragraph(f"• {bullet_c}", style_bullet))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 4))

    # 6. Skills
    skills_obj = resume_data.get("skills", {})
    categories = [
        ("Programming Languages", skills_obj.get("programming", [])),
        ("Frameworks & Libraries", skills_obj.get("frameworks", [])),
        ("Web Technologies", skills_obj.get("web", [])),
        ("Databases", skills_obj.get("databases", [])),
        ("Tools & Platforms", skills_obj.get("tools", [])),
        ("Soft Skills", skills_obj.get("soft", []))
    ]
    valid_skill_cats = [(cat, items) for cat, items in categories if items and len(items) > 0]
    if valid_skill_cats:
        add_section_header("Skills")
        for cat, items in valid_skill_cats:
            items_str = ", ".join([clean_txt(i) for i in items])
            line = f"<b>{cat}:</b> {items_str}"
            story.append(Paragraph(line, style_body))
            story.append(Spacer(1, 2))
        story.append(Spacer(1, 4))

    # 7. Internships
    internships = resume_data.get("internships", [])
    if internships:
        add_section_header("Internships")
        for intern in internships:
            role = clean_txt(intern.get("role", ""))
            org = clean_txt(intern.get("organization", ""))
            dur = clean_txt(intern.get("duration", ""))
            header_table = Table(
                [[Paragraph(f"<b>{role}</b> — {org}", style_subheading), Paragraph(dur, style_date)]],
                colWidths=[380, 140]
            )
            header_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
            ]))
            story.append(header_table)
            desc = clean_txt(intern.get("description") or intern.get("responsibilities") or "")
            if desc:
                for line in desc.split("<br/>"):
                    line_c = line.strip()
                    if line_c:
                        story.append(Paragraph(f"• {line_c.lstrip('•-* ')}", style_bullet))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 4))

    # 8. Certifications
    certifications = resume_data.get("certifications", [])
    if certifications:
        add_section_header("Certifications")
        for cert in certifications:
            name = clean_txt(cert.get("name", ""))
            issuer = clean_txt(cert.get("issuer", ""))
            date = clean_txt(cert.get("date", ""))
            left_text = f"<b>{name}</b>" + (f" — {issuer}" if issuer else "")
            header_table = Table(
                [[Paragraph(left_text, style_subheading), Paragraph(date, style_date)]],
                colWidths=[380, 140]
            )
            header_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
            ]))
            story.append(header_table)
            if cert.get("description"):
                story.append(Paragraph(clean_txt(cert["description"]), style_body))
            story.append(Spacer(1, 3))
        story.append(Spacer(1, 4))

    # 9. Achievements
    achievements = resume_data.get("achievements", [])
    if achievements:
        add_section_header("Achievements & Honors")
        for ach in achievements:
            title = clean_txt(ach.get("title", ""))
            date = clean_txt(ach.get("date", ""))
            desc = clean_txt(ach.get("description", ""))
            header_table = Table(
                [[Paragraph(f"<b>{title}</b>", style_subheading), Paragraph(date, style_date)]],
                colWidths=[380, 140]
            )
            header_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
            ]))
            story.append(header_table)
            if desc:
                story.append(Paragraph(desc, style_body))
            story.append(Spacer(1, 3))
        story.append(Spacer(1, 4))

    # 10. Languages
    languages = resume_data.get("languages", [])
    if languages:
        add_section_header("Languages")
        lang_strs = []
        for l in languages:
            lang_name = clean_txt(l.get("language", ""))
            prof = clean_txt(l.get("proficiency", ""))
            if lang_name:
                lang_strs.append(f"<b>{lang_name}</b> ({prof})" if prof else f"<b>{lang_name}</b>")
        story.append(Paragraph(" &nbsp;|&nbsp; ".join(lang_strs), style_body))

    # Build document
    doc.build(story)
    buffer.seek(0)
    return buffer
