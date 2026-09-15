import re
import json
import logging
from services.ai_service import _call_openai, STRICT_ACCURACY_PROMPT

logger = logging.getLogger(__name__)

COMMON_TECH_KEYWORDS = [
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "sql", "nosql",
    "flask", "django", "fastapi", "react", "angular", "vue", "node", "express", "next.js",
    "html", "css", "rest api", "rest apis", "graphql", "microservices", "docker", "kubernetes",
    "aws", "azure", "gcp", "cloud", "git", "ci/cd", "agile", "scrum", "postgresql", "mysql",
    "mongodb", "redis", "linux", "testing", "unit tests", "system design", "machine learning",
    "data science", "oop", "algorithms", "data structures"
]

def analyze_job_description(resume_data, job_description):
    """
    Analyzes resume against a job description.
    Returns:
    {
        "success": True,
        "ats_score": 84,
        "keyword_match": 88,
        "skills_match": 82,
        "experience_match": 80,
        "structure_score": 95,
        "suggestions": [
            {"type": "positive", "text": "Your resume contains Python."},
            {"type": "warning", "text": "The job description mentions REST APIs. Add this only if you actually have REST API experience."}
        ]
    }
    """
    if not job_description or not job_description.strip():
        return {"success": False, "error": "Job description is empty"}

    # Attempt OpenAI analysis first if configured
    resume_summary_text = _format_resume_text(resume_data)
    
    system_prompt = (
        f"{STRICT_ACCURACY_PROMPT}\n"
        "You are an ATS (Applicant Tracking System) optimization expert.\n"
        "Compare the candidate's resume with the job description. Return ONLY valid JSON with this exact schema:\n"
        "{\n"
        '  "ats_score": 84,\n'
        '  "keyword_match": 88,\n'
        '  "skills_match": 82,\n'
        '  "experience_match": 80,\n'
        '  "structure_score": 95,\n'
        '  "suggestions": [\n'
        '    {"type": "positive", "text": "Your resume contains Python."},\n'
        '    {"type": "positive", "text": "Your project section is relevant."},\n'
        '    {"type": "warning", "text": "The job description mentions REST APIs. Add this only if you actually have REST API experience."},\n'
        '    {"type": "warning", "text": "Add more measurable achievements if you have relevant numbers."}\n'
        '  ]\n'
        "}\n"
        "CRITICAL: Any missing skill recommendation MUST include the advisory: 'Add this only if you actually have relevant experience.'"
    )

    user_prompt = f"Candidate Resume:\n{resume_summary_text}\n\nJob Description:\n{job_description[:3000]}"

    ai_res = _call_openai([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ], json_mode=True, temperature=0.2)

    if ai_res:
        try:
            parsed = json.loads(ai_res)
            parsed["success"] = True
            return parsed
        except Exception as e:
            logger.error(f"Failed to parse OpenAI ATS response: {e}")

    # Built-in Heuristic ATS Engine
    return _heuristic_ats_analysis(resume_data, job_description, resume_summary_text)


def _format_resume_text(resume_data):
    """Converts resume dictionary to readable text for scanning."""
    parts = []
    p = resume_data.get("personal", {})
    parts.append(f"Title: {p.get('title', '')}")
    parts.append(f"Summary: {resume_data.get('summary', '')}")
    
    skills = resume_data.get("skills", {})
    if isinstance(skills, dict):
        all_skills = []
        for v in skills.values():
            if isinstance(v, list):
                all_skills.extend(v)
        parts.append(f"Skills: {', '.join(all_skills)}")

    for exp in resume_data.get("experience", []):
        parts.append(f"Experience: {exp.get('jobTitle', '')} at {exp.get('company', '')} - {exp.get('description', '')} {exp.get('responsibilities', '')}")

    for proj in resume_data.get("projects", []):
        parts.append(f"Project: {proj.get('name', '')} ({proj.get('technologies', '')}) - {proj.get('description', '')}")

    for edu in resume_data.get("education", []):
        parts.append(f"Education: {edu.get('degree', '')} {edu.get('university', '')}")

    return "\n".join(parts)


def _heuristic_ats_analysis(resume_data, job_desc, resume_text):
    jd_lower = job_desc.lower()
    resume_lower = resume_text.lower()

    # 1. Identify JD Keywords
    jd_keywords = set()
    for kw in COMMON_TECH_KEYWORDS:
        pattern = rf'\b{re.escape(kw)}\b'
        if re.search(pattern, jd_lower):
            jd_keywords.add(kw)

    # If few tech keywords matched, extract high frequency words (>4 letters)
    if len(jd_keywords) < 4:
        words = re.findall(r'\b[a-z]{4,15}\b', jd_lower)
        stopwords = {"with", "that", "this", "from", "have", "more", "will", "your", "their", "team", "work", "role", "must", "years", "about", "other"}
        for w in words:
            if w not in stopwords:
                jd_keywords.add(w)
                if len(jd_keywords) >= 10:
                    break

    # 2. Check matches in resume
    matched_keywords = []
    missing_keywords = []
    for kw in jd_keywords:
        pattern = rf'\b{re.escape(kw)}\b'
        if re.search(pattern, resume_lower):
            matched_keywords.append(kw)
        else:
            missing_keywords.append(kw)

    total_kw = len(jd_keywords) if jd_keywords else 1
    keyword_match = min(100, int((len(matched_keywords) / total_kw) * 100))

    # 3. Skills match
    resume_skills = []
    skills_obj = resume_data.get("skills", {})
    if isinstance(skills_obj, dict):
        for v in skills_obj.values():
            if isinstance(v, list):
                resume_skills.extend([s.lower() for s in v])
    
    skill_hits = [k for k in matched_keywords if k in resume_skills]
    skills_match = min(100, max(60, int((len(skill_hits) / (len(matched_keywords) or 1)) * 100)))

    # 4. Experience match
    has_exp = len(resume_data.get("experience", [])) > 0
    has_intern = len(resume_data.get("internships", [])) > 0
    has_proj = len(resume_data.get("projects", [])) > 0
    experience_match = 85 if has_exp else (78 if has_intern or has_proj else 60)

    # 5. Structure Score
    structure_points = 0
    p = resume_data.get("personal", {})
    if p.get("name") and p.get("email"):
        structure_points += 25
    if resume_data.get("summary"):
        structure_points += 20
    if has_exp or has_intern:
        structure_points += 20
    if resume_data.get("education"):
        structure_points += 20
    if resume_skills:
        structure_points += 15
    structure_score = min(100, max(50, structure_points))

    # Overall ATS Score (weighted average)
    ats_score = int(
        (keyword_match * 0.35) +
        (skills_match * 0.25) +
        (experience_match * 0.20) +
        (structure_score * 0.20)
    )
    ats_score = max(45, min(98, ats_score))

    # Generate suggestions
    suggestions = []
    for kw in matched_keywords[:3]:
        suggestions.append({
            "type": "positive",
            "text": f"Your resume clearly matches the requirement for '{kw.title()}'."
        })

    if has_proj:
        suggestions.append({
            "type": "positive",
            "text": "Your projects section demonstrates hands-on implementation relevant to the role."
        })

    for kw in missing_keywords[:3]:
        suggestions.append({
            "type": "warning",
            "text": f"The job description mentions '{kw.title()}'. Add this only if you actually possess relevant experience with it."
        })

    # Metric warning check
    has_metrics = bool(re.search(r'\d+%', resume_text) or re.search(r'\$\d+', resume_text))
    if not has_metrics:
        suggestions.append({
            "type": "warning",
            "text": "Add more measurable achievements (e.g., performance gains, scale) if you have verified numbers."
        })

    return {
        "success": True,
        "ats_score": ats_score,
        "keyword_match": keyword_match,
        "skills_match": skills_match,
        "experience_match": experience_match,
        "structure_score": structure_score,
        "suggestions": suggestions
    }
