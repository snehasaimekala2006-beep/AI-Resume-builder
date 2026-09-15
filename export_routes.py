from flask import Blueprint, request, jsonify, send_file, render_template, abort
from models import db
from models.resume import Resume
from services.pdf_service import generate_pdf

export_bp = Blueprint("export_bp", __name__)

@export_bp.route("/api/resumes/<int:resume_id>/pdf", methods=["GET"])
def download_resume_pdf(resume_id):
    resume = db.session.get(Resume, resume_id)
    if not resume:
        return jsonify({"success": False, "error": "Resume not found"}), 404
    
    template_name = request.args.get("template", resume.template)
    pdf_buffer = generate_pdf(resume.data, template_name=template_name)
    
    safe_name = "".join(c for c in (resume.data.get("personal", {}).get("name") or resume.title) if c.isalnum() or c in (' ', '_', '-')).strip()
    filename = f"{safe_name.replace(' ', '_')}_Resume.pdf" if safe_name else "Resume.pdf"

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )

@export_bp.route("/api/export/pdf", methods=["POST"])
def export_draft_pdf():
    payload = request.get_json() or {}
    resume_data = payload.get("data", {})
    template_name = payload.get("template", "classic")
    
    pdf_buffer = generate_pdf(resume_data, template_name=template_name)
    safe_name = "".join(c for c in resume_data.get("personal", {}).get("name", "Resume") if c.isalnum() or c in (' ', '_', '-')).strip()
    filename = f"{safe_name.replace(' ', '_')}_Resume.pdf" if safe_name else "Resume.pdf"

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )

@export_bp.route("/resumes/<int:resume_id>/print", methods=["GET"])
def print_resume_view(resume_id):
    resume = db.session.get(Resume, resume_id)
    if not resume:
        abort(404)
    template_name = request.args.get("template", resume.template)
    return render_template(
        "resume/print_view.html",
        resume=resume,
        template_name=template_name,
        data=resume.data
    )
