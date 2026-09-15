from flask import Blueprint, request, jsonify
from services.ai_service import (
    generate_summary,
    generate_experience_description,
    generate_project_description,
    generate_education_description,
    generate_certification_description,
    generate_achievement_description,
    generate_internship_description,
    improve_text,
    suggest_skills,
    generate_complete_resume,
    is_openai_configured
)
from services.ats_service import analyze_job_description

ai_bp = Blueprint("ai_bp", __name__)

@ai_bp.route("/api/ai/status", methods=["GET"])
def ai_status():
    has_key = is_openai_configured()
    return jsonify({
        "success": True,
        "openai_configured": has_key,
        "mode": "OpenAI Cloud Engine" if has_key else "Local Smart NLP Engine"
    })

@ai_bp.route("/api/ai/generate-summary", methods=["POST"])
def api_generate_summary():
    payload = request.get_json() or {}
    data = payload.get("data", payload)
    res = generate_summary(data)
    return jsonify(res)

@ai_bp.route("/api/ai/generate-description", methods=["POST"])
def api_generate_description():
    payload = request.get_json() or {}
    section = payload.get("section", "experience").lower()
    data = payload.get("data", {})

    if section in ["experience", "job", "work"]:
        res = generate_experience_description(data)
    elif section in ["project", "projects"]:
        res = generate_project_description(data)
    elif section in ["education", "academic"]:
        res = generate_education_description(data)
    elif section in ["certification", "certifications"]:
        res = generate_certification_description(data)
    elif section in ["achievement", "achievements"]:
        res = generate_achievement_description(data)
    elif section in ["internship", "internships"]:
        res = generate_internship_description(data)
    else:
        res = {"success": False, "error": f"Unknown section: {section}"}
    
    return jsonify(res)

@ai_bp.route("/api/ai/improve", methods=["POST"])
def api_improve():
    payload = request.get_json() or {}
    text = payload.get("text", "")
    style = payload.get("style", "improve")
    res = improve_text(text, style=style)
    return jsonify(res)

@ai_bp.route("/api/ai/rewrite", methods=["POST"])
def api_rewrite():
    payload = request.get_json() or {}
    text = payload.get("text", "")
    res = improve_text(text, style="rewrite")
    return jsonify(res)

@ai_bp.route("/api/ai/shorten", methods=["POST"])
def api_shorten():
    payload = request.get_json() or {}
    text = payload.get("text", "")
    res = improve_text(text, style="shorten")
    return jsonify(res)

@ai_bp.route("/api/ai/expand", methods=["POST"])
def api_expand():
    payload = request.get_json() or {}
    text = payload.get("text", "")
    res = improve_text(text, style="expand")
    return jsonify(res)

@ai_bp.route("/api/ai/suggest-skills", methods=["POST"])
def api_suggest_skills():
    payload = request.get_json() or {}
    resume_data = payload.get("resume", {})
    res = suggest_skills(resume_data)
    return jsonify(res)

@ai_bp.route("/api/ai/generate-resume", methods=["POST"])
def api_generate_complete_resume():
    payload = request.get_json() or {}
    raw_text = payload.get("raw_text", "")
    if not raw_text.strip():
        return jsonify({"success": False, "error": "Please provide your background or experience text."}), 400
    res = generate_complete_resume(raw_text)
    return jsonify(res)

@ai_bp.route("/api/ai/analyze-job", methods=["POST"])
def api_analyze_job():
    payload = request.get_json() or {}
    resume_data = payload.get("resume", {})
    job_description = payload.get("job_description", "")
    if not job_description.strip():
        return jsonify({"success": False, "error": "Please paste a job description."}), 400
    res = analyze_job_description(resume_data, job_description)
    return jsonify(res)
