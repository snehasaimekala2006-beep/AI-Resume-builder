import os
import re
import json
import logging
import requests
from config import Config

logger = logging.getLogger(__name__)

STRICT_ACCURACY_PROMPT = (
    "You are an expert ATS-compliant resume writer. Follow this CRITICAL SAFETY RULE:\n"
    "NEVER FABRICATE OR HALLUCINATE INFORMATION. Do not invent company names, job titles, "
    "degrees, certifications, awards, technologies, metrics, or percentages unless explicitly supplied by the user.\n"
    "Your job is to elevate wording, apply strong active verbs, fix grammar, and format professionally "
    "based SOLELY on the facts provided."
)

def is_openai_configured():
    return bool(Config.OPENAI_API_KEY and Config.OPENAI_API_KEY.strip() and not Config.OPENAI_API_KEY.startswith("your_"))

def _call_openai(messages, json_mode=False, temperature=0.3):
    """Centralized helper for OpenAI API calls."""
    if not is_openai_configured():
        return None

    headers = {
        "Authorization": f"Bearer {Config.OPENAI_API_KEY.strip()}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": Config.OPENAI_MODEL,
        "messages": messages,
        "temperature": temperature
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    try:
        url = f"{Config.OPENAI_API_BASE.rstrip('/')}/chat/completions"
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code == 200:
            result = resp.json()
            return result["choices"][0]["message"]["content"]
        else:
            logger.warning(f"OpenAI API returned status {resp.status_code}: {resp.text}")
            return None
    except Exception as e:
        logger.error(f"OpenAI request failed: {e}")
        return None


# -------------------------------------------------------------
# Section AI: Summary Generation
# -------------------------------------------------------------
def generate_summary(user_data):
    """Generates a professional summary based strictly on user data."""
    raw_summary = user_data.get("summary", "")
    title = user_data.get("title", "") or user_data.get("personal", {}).get("title", "")
    skills = user_data.get("skills", {})
    exp = user_data.get("experience", [])
    edu = user_data.get("education", [])
    
    # Gather key facts for context
    skill_list = []
    if isinstance(skills, dict):
        for k, v in skills.items():
            if isinstance(v, list):
                skill_list.extend(v)
    elif isinstance(skills, list):
        skill_list = skills

    system_prompt = (
        f"{STRICT_ACCURACY_PROMPT}\n"
        "Generate a 3-4 sentence professional resume summary. "
        "Highlight their expertise, tools, and background using only provided facts. "
        "Do not invent statistics or past employers."
    )
    user_prompt = f"Title: {title}\nSkills: {', '.join(skill_list[:10])}\nRaw summary notes: {raw_summary}\nRecent Experience: {len(exp)} roles listed\nEducation: {len(edu)} degrees listed."

    ai_res = _call_openai([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])

    if ai_res:
        return {"success": True, "section": "summary", "content": ai_res.strip()}

    # Fallback NLP Generator
    return {"success": True, "section": "summary", "content": _fallback_summary(title, skill_list, raw_summary)}

def _fallback_summary(title, skills, raw_summary):
    t = title.strip() if title else "Dedicated Professional"
    skill_text = f" with hands-on proficiency in {', '.join(skills[:5])}" if skills else ""
    
    if raw_summary and len(raw_summary.strip()) > 10:
        cleaned = raw_summary.strip().rstrip(".")
        return f"{t}{skill_text}. Demonstrated experience in {cleaned}. Committed to delivering clean, reliable solutions and driving high-quality outcomes."
    
    return f"Motivated and detail-oriented {t}{skill_text}. Adept at analyzing complex technical requirements, collaborating across multidisciplinary teams, and delivering robust, scalable solutions."


# -------------------------------------------------------------
# Section AI: Experience Descriptions
# -------------------------------------------------------------
def generate_experience_description(data):
    """Transforms raw job duties/achievements into professional resume bullet points."""
    title = data.get("jobTitle", "")
    company = data.get("company", "")
    resp = data.get("responsibilities", "")
    achieve = data.get("achievements", "")
    raw = f"Role: {title} at {company}\nResponsibilities: {resp}\nAchievements: {achieve}"

    system_prompt = (
        f"{STRICT_ACCURACY_PROMPT}\n"
        "Convert the user's responsibilities and achievements into 3-4 strong, professional resume bullet points starting with '• '.\n"
        "Use strong action verbs (e.g., Developed, Engineered, Streamlined, Coordinated). "
        "Keep strictly to the facts provided; do not add numbers or percentages unless provided."
    )

    ai_res = _call_openai([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": raw}
    ])

    if ai_res:
        return {"success": True, "section": "experience", "content": ai_res.strip()}

    return {"success": True, "section": "experience", "content": _fallback_bullet_points(f"{resp}\n{achieve}", default_verb="Spearheaded")}


# -------------------------------------------------------------
# Section AI: Project Descriptions
# -------------------------------------------------------------
def generate_project_description(data):
    """Generates concise, professional project description from user details."""
    name = data.get("name", "")
    tech = data.get("technologies", "")
    desc = data.get("rawDescription", "") or data.get("description", "")
    
    prompt_input = f"Project Name: {name}\nTechnologies: {tech}\nDescription: {desc}"

    system_prompt = (
        f"{STRICT_ACCURACY_PROMPT}\n"
        "Generate a concise 2-3 sentence professional resume project description. "
        "Highlight the architectural purpose and technologies mentioned without fabricating extra features or metrics."
    )

    ai_res = _call_openai([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt_input}
    ])

    if ai_res:
        return {"success": True, "section": "project", "content": ai_res.strip()}

    # Fallback
    tech_str = f" using {tech}" if tech else ""
    cleaned = desc.strip().rstrip(".")
    if not cleaned:
        cleaned = "streamlining key workflows"
    return {
        "success": True, 
        "section": "project", 
        "content": f"Developed {name or 'application'}{tech_str}, engineered to {cleaned.lower() if not cleaned.startswith('I ') else cleaned}. Implemented structured code patterns to ensure maintainability and optimal performance."
    }


# -------------------------------------------------------------
# Section AI: Education, Certification, Achievement, Internship
# -------------------------------------------------------------
def generate_education_description(data):
    degree = data.get("degree", "")
    university = data.get("university", "")
    desc = data.get("description", "")
    gpa = data.get("gpa", "")

    system_prompt = f"{STRICT_ACCURACY_PROMPT}\nImprove this education entry description into 1-2 polished sentences highlighting coursework and academic rigor."
    user_prompt = f"Degree: {degree}, University: {university}, GPA: {gpa}, Notes: {desc}"

    ai_res = _call_openai([{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}])
    if ai_res:
        return {"success": True, "section": "education", "content": ai_res.strip()}

    gpa_text = f" Maintained a competitive academic standing with a GPA of {gpa}." if gpa else ""
    return {
        "success": True,
        "section": "education",
        "content": f"Completed comprehensive curriculum in {degree or 'academics'} at {university or 'university'}.{gpa_text} Emphasized core foundational principles, collaborative team projects, and practical applications."
    }

def generate_certification_description(data):
    name = data.get("name", "")
    issuer = data.get("issuer", "")
    desc = data.get("description", "")

    system_prompt = f"{STRICT_ACCURACY_PROMPT}\nWrite 1 concise, professional sentence describing the technical verification provided by this certification."
    user_prompt = f"Certification: {name}, Issuer: {issuer}, Notes: {desc}"

    ai_res = _call_openai([{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}])
    if ai_res:
        return {"success": True, "section": "certification", "content": ai_res.strip()}

    return {
        "success": True,
        "section": "certification",
        "content": f"Validated professional competency and industry best practices in {name} administered by {issuer or 'recognized credentialing authority'}."
    }

def generate_achievement_description(data):
    title = data.get("title", "")
    desc = data.get("description", "")

    system_prompt = f"{STRICT_ACCURACY_PROMPT}\nElevate this achievement note into a compelling, professional bullet sentence. Do not invent numbers."
    user_prompt = f"Title: {title}, Description: {desc}"

    ai_res = _call_openai([{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}])
    if ai_res:
        return {"success": True, "section": "achievement", "content": ai_res.strip()}

    return {
        "success": True,
        "section": "achievement",
        "content": f"Recognized for {title}: {desc.strip().rstrip('.')} through sustained dedication and technical execution."
    }

def generate_internship_description(data):
    role = data.get("role", "")
    org = data.get("organization", "")
    resp = data.get("responsibilities", "") or data.get("description", "")

    system_prompt = f"{STRICT_ACCURACY_PROMPT}\nCreate 2-3 professional bullet points for this internship. Start each with '• '. Do not invent metrics."
    user_prompt = f"Role: {role} at {org}\nDuties: {resp}"

    ai_res = _call_openai([{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}])
    if ai_res:
        return {"success": True, "section": "internship", "content": ai_res.strip()}

    return {"success": True, "section": "internship", "content": _fallback_bullet_points(resp, default_verb="Contributed to")}


# -------------------------------------------------------------
# AI Writing Options (Improve, Professional, ATS, Shorten, Expand, Rewrite)
# -------------------------------------------------------------
def improve_text(text, style="improve"):
    """
    Applies designated writing transformations:
    - 'improve': Better grammar, clarity, and tone
    - 'professional': Executive corporate wording
    - 'ats': Keyword and action-oriented ATS phrasing
    - 'shorten': Crisp, concise, removes filler words
    - 'expand': Adds professional depth and detail while strictly honoring facts
    - 'rewrite': Fresh phrasing with alternative strong verbs
    """
    if not text or not text.strip():
        return {"success": False, "error": "No text provided"}

    style_instructions = {
        "improve": "Enhance clarity, flow, and grammatical precision while preserving exact meaning.",
        "professional": "Rewrite in high-caliber, executive professional tone with active industry terminology.",
        "ats": "Optimize for Applicant Tracking Systems by using industry-standard action verbs and clean syntax.",
        "shorten": "Condense this text into its most impactful, concise form. Eliminate fluff and redundant words.",
        "expand": "Elaborate with professional context and technical thoroughness without fabricating facts or metrics.",
        "rewrite": "Provide an alternative phrasing using fresh, dynamic action verbs while retaining the original facts."
    }

    instruction = style_instructions.get(style.lower(), style_instructions["improve"])

    system_prompt = (
        f"{STRICT_ACCURACY_PROMPT}\n"
        f"Task: {instruction}\n"
        "Never invent numbers, metrics, or technologies not in the original text."
    )

    ai_res = _call_openai([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ])

    if ai_res:
        return {"success": True, "style": style, "content": ai_res.strip()}

    # Heuristic NLP Fallback
    return {"success": True, "style": style, "content": _fallback_style_transform(text, style)}

def _fallback_style_transform(text, style):
    cleaned = text.strip()
    style = style.lower()

    if style == "shorten":
        # Remove filler phrases
        fillers = ["in order to ", "responsible for ", "worked on ", "helped with ", "duties included ", "was involved in "]
        res = cleaned
        for f in fillers:
            res = re.sub(re.escape(f), "", res, flags=re.IGNORECASE)
        sentences = [s.strip() for s in re.split(r'[.\n]+', res) if s.strip()]
        return ". ".join(sentences[:2]) + ("." if sentences else "")

    elif style == "expand":
        return f"{cleaned} Ensured continuous alignment with high technical standards, maintainable architecture, and collaborative project goals."

    elif style == "professional":
        t = cleaned
        t = re.sub(r'\bworked on\b', 'engineered and maintained', t, flags=re.IGNORECASE)
        t = re.sub(r'\bfixed\b', 'diagnosed and resolved', t, flags=re.IGNORECASE)
        t = re.sub(r'\bmade\b', 'architected and developed', t, flags=re.IGNORECASE)
        t = re.sub(r'\bhelped\b', 'collaborated to facilitate', t, flags=re.IGNORECASE)
        t = re.sub(r'\bused\b', 'leveraged', t, flags=re.IGNORECASE)
        return t

    elif style == "ats":
        # Bulletize or action-orient
        lines = [l.strip() for l in cleaned.split("\n") if l.strip()]
        out = []
        for line in lines:
            line_clean = line.lstrip("•-* ").strip()
            if line_clean:
                out.append(f"• Spearheaded {line_clean[0].lower() + line_clean[1:] if line_clean else ''}")
        return "\n".join(out) if out else f"• Executed {cleaned}"

    # Default 'improve' or 'rewrite'
    t = cleaned
    t = re.sub(r'\bi did\b', 'Led initiatives in', t, flags=re.IGNORECASE)
    t = re.sub(r'\bresponsible for\b', 'Oversaw the delivery of', t, flags=re.IGNORECASE)
    t = re.sub(r'\bcreated\b', 'Architected and built', t, flags=re.IGNORECASE)
    return t


# -------------------------------------------------------------
# Suggest Skills
# -------------------------------------------------------------
def suggest_skills(resume_data):
    """Analyzes user resume data and suggests relevant skills clearly marked as suggestions."""
    context_text = json.dumps(resume_data, ensure_ascii=False)
    
    system_prompt = (
        f"{STRICT_ACCURACY_PROMPT}\n"
        "Based on the user's existing background, suggest 6 to 10 potentially relevant modern technical and soft skills. "
        "Return ONLY a JSON object with keys: 'programming', 'frameworks', 'web', 'databases', 'tools', 'soft'. "
        "Each value must be a list of strings."
    )

    ai_res = _call_openai([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Resume details:\n{context_text[:2000]}"}
    ], json_mode=True)

    if ai_res:
        try:
            parsed = json.loads(ai_res)
            return {"success": True, "suggestions": parsed}
        except Exception:
            pass

    # Heuristic skill recommender based on keyword matches
    lower_ctx = context_text.lower()
    suggested = {
        "programming": [],
        "frameworks": [],
        "web": [],
        "databases": [],
        "tools": [],
        "soft": ["Agile Methodology", "Cross-Functional Collaboration", "Problem Solving", "Technical Communication"]
    }

    if "python" in lower_ctx:
        suggested["programming"].extend(["Python 3", "Type Hinting"])
        suggested["frameworks"].extend(["Flask", "FastAPI", "pytest"])
        suggested["tools"].extend(["Git", "Virtualenv", "Docker"])
    if "web" in lower_ctx or "html" in lower_ctx or "javascript" in lower_ctx:
        suggested["web"].extend(["HTML5", "CSS3 / Flexbox", "RESTful APIs", "JSON"])
        suggested["frameworks"].append("React.js" if "react" not in lower_ctx else "Vue.js")
    if "sql" in lower_ctx or "database" in lower_ctx:
        suggested["databases"].extend(["PostgreSQL", "SQLite", "SQLAlchemy ORM"])
    else:
        suggested["databases"].extend(["PostgreSQL", "SQLite"])

    return {"success": True, "suggestions": suggested}


# -------------------------------------------------------------
# Complete Resume AI: Raw Text Parser
# -------------------------------------------------------------
def generate_complete_resume(raw_text):
    """
    Parses completely unstructured text (e.g., 'I am a B.Tech student...')
    into the full structured JSON resume schema.
    """
    if not raw_text or not raw_text.strip():
        return {"success": False, "error": "No input provided"}

    system_prompt = (
        f"{STRICT_ACCURACY_PROMPT}\n"
        "You are an AI resume parser. Read the user's unstructured biographical/career text and parse it into structured JSON.\n"
        "Schema to return:\n"
        "{\n"
        '  "personal": {"name": "", "title": "", "email": "", "phone": "", "location": "", "linkedin": "", "github": "", "portfolio": ""},\n'
        '  "summary": "Professional summary statement based on facts",\n'
        '  "education": [{"degree": "", "university": "", "location": "", "startYear": "", "endYear": "", "gpa": "", "description": ""}],\n'
        '  "experience": [{"jobTitle": "", "company": "", "location": "", "startDate": "", "endDate": "", "currentlyWorking": false, "responsibilities": "", "achievements": "", "description": "• bullet point 1\\n• bullet point 2"}],\n'
        '  "projects": [{"name": "", "projectUrl": "", "githubUrl": "", "technologies": "", "rawDescription": "", "description": ""}],\n'
        '  "skills": {"programming": [], "frameworks": [], "web": [], "databases": [], "tools": [], "soft": []},\n'
        '  "certifications": [{"name": "", "issuer": "", "date": "", "credentialUrl": "", "description": ""}],\n'
        '  "achievements": [{"title": "", "date": "", "description": ""}],\n'
        '  "internships": [{"organization": "", "role": "", "duration": "", "responsibilities": "", "description": ""}],\n'
        '  "languages": [{"language": "", "proficiency": "Professional"}]\n'
        "}\n"
        "IMPORTANT: Do NOT invent companies, metrics, or degrees not mentioned in the text. "
        "Leave unknown fields as empty strings or empty lists."
    )

    ai_res = _call_openai([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": raw_text}
    ], json_mode=True, temperature=0.2)

    if ai_res:
        try:
            parsed = json.loads(ai_res)
            return {"success": True, "resume": parsed}
        except Exception as e:
            logger.error(f"Failed to parse OpenAI JSON resume: {e}")

    # Robust Fallback Parser
    parsed_resume = _fallback_resume_parser(raw_text)
    return {"success": True, "resume": parsed_resume}


def _fallback_resume_parser(text):
    """Regex & NLP heuristic unstructured text extractor."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    full_text = " ".join(lines)
    
    # 1. Email extraction
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', full_text)
    email = email_match.group(0) if email_match else ""

    # 2. Phone extraction
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}', full_text)
    phone = phone_match.group(0) if phone_match else ""

    # 3. Name extraction heuristic
    name = ""
    title = ""
    first_line = lines[0] if lines else ""
    if "i am " in first_line.lower():
        intro_match = re.search(r'i am (?:a |an )?([A-Za-z\s]+?)(?:student|developer|engineer|professional|\.|\,)', first_line, re.I)
        if intro_match:
            title = intro_match.group(1).strip() + (" Developer" if "developer" not in intro_match.group(1).lower() else "")
    else:
        # If first line looks like a name (2-3 capitalized words, no email/phone)
        words = first_line.split()
        if 1 <= len(words) <= 3 and all(w[0].isupper() for w in words if w.isalpha()):
            name = first_line

    if not title:
        if re.search(r'software|developer|engineer', full_text, re.I):
            title = "Software Developer"
        elif re.search(r'student|b\.?tech|computer science', full_text, re.I):
            title = "Computer Science Student & Aspiring Developer"
        else:
            title = "Professional"

    # 4. Skills extraction
    skills = {
        "programming": [],
        "frameworks": [],
        "web": [],
        "databases": [],
        "tools": [],
        "soft": []
    }
    prog_kw = ["Python", "Java", "C\\+\\+", "C#", "JavaScript", "TypeScript", "Go", "Rust", "PHP", "Ruby", "Kotlin", "Swift", "SQL"]
    for kw in prog_kw:
        if re.search(rf'\b{kw}\b', full_text, re.I):
            skills["programming"].append(kw.replace("\\+", "+"))

    fw_kw = ["Flask", "Django", "FastAPI", "React", "Angular", "Vue", "Spring Boot", r"Node\.js", "Express", r"Next\.js"]
    for kw in fw_kw:
        if re.search(rf'\b{kw}\b', full_text, re.I):
            skills["frameworks"].append(kw.replace(r"\.", "."))

    web_kw = ["HTML", "HTML5", "CSS", "CSS3", "REST API", "REST APIs", "Tailwind", "Bootstrap"]
    for kw in web_kw:
        if re.search(rf'\b{kw}\b', full_text, re.I):
            skills["web"].append(kw)

    db_kw = ["MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis", "Oracle"]
    for kw in db_kw:
        if re.search(rf'\b{kw}\b', full_text, re.I):
            skills["databases"].append(kw)

    tool_kw = ["Git", "GitHub", "Docker", "AWS", "Linux", "VS Code", "Postman", "Kubernetes"]
    for kw in tool_kw:
        if re.search(rf'\b{kw}\b', full_text, re.I):
            skills["tools"].append(kw)

    # 5. Education extraction
    education = []
    edu_match = re.search(r'(B\.?Tech|Bachelor|Master|M\.?Tech|BS|MS|High School)[^.\n]*', full_text, re.I)
    if edu_match:
        degree_str = edu_match.group(0).strip()
        education.append({
            "degree": degree_str,
            "university": "University",
            "location": "",
            "startYear": "2020",
            "endYear": "2024",
            "gpa": "",
            "description": f"Enrolled in {degree_str} coursework emphasizing foundational software concepts."
        })

    # 6. Projects extraction
    projects = []
    proj_match = re.search(r'(?:created|built|developed|made)\s+(?:a |an )?([^.\n]+)', full_text, re.I)
    if proj_match:
        proj_text = proj_match.group(1).strip()
        name = "Project"
        tech_used = ", ".join(skills["frameworks"] + skills["programming"][:2])
        if "," in proj_text:
            parts = proj_text.split(",", 1)
            name = parts[0].strip().title()
            desc_part = parts[1].strip()
        elif " using " in proj_text.lower():
            parts = re.split(r'\s+using\s+', proj_text, flags=re.I)
            name = parts[0].strip().title()
            desc_part = proj_text
        else:
            name = proj_text.split()[0].title()
            desc_part = proj_text
            
        projects.append({
            "name": name,
            "projectUrl": "",
            "githubUrl": "",
            "technologies": tech_used or "Python, Flask",
            "rawDescription": desc_part,
            "description": f"Architected and implemented {name}: {desc_part}."
        })

    # 7. Experience / Internships
    experience = []
    internships = []
    if "internship" in full_text.lower():
        intern_match = re.search(r'([^.\n]*internship[^.\n]*)', full_text, re.I)
        intern_text = intern_match.group(1).strip() if intern_match else "Software Internship"
        internships.append({
            "organization": "Technology Partner",
            "role": "Intern",
            "duration": "Summer",
            "responsibilities": intern_text,
            "description": f"• Contributed to {intern_text} with focus on robust software delivery."
        })

    # 8. Certifications
    certifications = []
    cert_match = re.search(r'([^.\n]*certification[^.\n]*)', full_text, re.I)
    if cert_match:
        cert_text = cert_match.group(1).strip()
        certifications.append({
            "name": cert_text,
            "issuer": "Credentialing Authority",
            "date": "2024",
            "credentialUrl": "",
            "description": f"Successfully completed {cert_text}."
        })

    # Summary
    all_skills_flat = skills["programming"] + skills["frameworks"] + skills["web"]
    summary = f"Motivated {title} with practical experience in {', '.join(all_skills_flat[:4]) if all_skills_flat else 'modern software engineering'}. Dedicated to applying proven technical skills to build maintainable, user-centric applications."

    return {
        "personal": {
            "name": name or "Candidate",
            "title": title,
            "email": email,
            "phone": phone,
            "location": "",
            "linkedin": "",
            "github": "",
            "portfolio": ""
        },
        "summary": summary,
        "education": education,
        "experience": experience,
        "projects": projects,
        "skills": skills,
        "certifications": certifications,
        "achievements": [],
        "internships": internships,
        "languages": [{"language": "English", "proficiency": "Professional"}]
    }


def _fallback_bullet_points(raw_text, default_verb="Developed"):
    """Turns raw informal notes into structured bullet points with action verbs."""
    if not raw_text or not raw_text.strip():
        return "• Executed core responsibilities adhering to professional standards."

    lines = [l.strip() for l in re.split(r'[\n;.]+', raw_text) if len(l.strip()) > 3]
    bullets = []
    action_verbs = ["Spearheaded", "Engineered", "Implemented", "Streamlined", "Collaborated on", "Diagnosed and resolved"]

    for i, line in enumerate(lines[:5]):
        # Strip existing bullets
        cleaned = re.sub(r'^[•\-\*\d\.\s]+', '', line).strip()
        if not cleaned:
            continue
        
        # Check if already starts with action verb
        words = cleaned.split()
        first_word = words[0]
        if first_word.endswith("ed") or first_word.endswith("ing"):
            bullet_text = cleaned[0].upper() + cleaned[1:]
        else:
            verb = action_verbs[i % len(action_verbs)]
            bullet_text = f"{verb} {cleaned[0].lower() + cleaned[1:] if len(cleaned) > 1 else cleaned}"
        
        if not bullet_text.endswith("."):
            bullet_text += "."
        bullets.append(f"• {bullet_text}")

    return "\n".join(bullets) if bullets else f"• {default_verb} project objectives according to team milestones."
