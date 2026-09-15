import json
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from models import db
from models.resume import Resume, DEFAULT_RESUME_DATA, SAMPLE_RESUME_DATA

resume_bp = Blueprint("resume_bp", __name__)

@resume_bp.route("/")
def index():
    # If there are existing resumes, open the most recent one or editor
    first = Resume.query.order_by(Resume.updated_at.desc()).first()
    if not first:
        # Seed an initial sample resume for instant wow-factor
        new_resume = Resume(
            title="Sneha Sai - Software Developer",
            template="classic",
            data_json=json.dumps(SAMPLE_RESUME_DATA, ensure_ascii=False)
        )
        db.session.add(new_resume)
        db.session.commit()
        return redirect(url_for("resume_bp.editor", id=new_resume.id))
    return redirect(url_for("resume_bp.editor", id=first.id))

@resume_bp.route("/dashboard")
def dashboard():
    resumes = Resume.query.order_by(Resume.updated_at.desc()).all()
    return render_template("dashboard.html", resumes=resumes)

@resume_bp.route("/editor")
def editor():
    resume_id = request.args.get("id", type=int)
    active_resume = None
    if resume_id:
        active_resume = db.session.get(Resume, resume_id)
    if not active_resume:
        active_resume = Resume.query.order_by(Resume.updated_at.desc()).first()
        if not active_resume:
            active_resume = Resume(
                title="Untitled Resume",
                template="classic",
                data_json=json.dumps(DEFAULT_RESUME_DATA, ensure_ascii=False)
            )
            db.session.add(active_resume)
            db.session.commit()

    all_resumes = Resume.query.order_by(Resume.updated_at.desc()).all()
    return render_template(
        "editor.html",
        active_resume=active_resume,
        all_resumes=all_resumes,
        initial_data_json=json.dumps(active_resume.data)
    )

# ----------------- REST API -----------------

@resume_bp.route("/api/resumes", methods=["GET"])
def get_all_resumes():
    resumes = Resume.query.order_by(Resume.updated_at.desc()).all()
    return jsonify({"success": True, "resumes": [r.to_dict() for r in resumes]})

@resume_bp.route("/api/resumes", methods=["POST"])
def create_resume():
    payload = request.get_json() or {}
    title = payload.get("title", "Untitled Resume")
    template = payload.get("template", "classic")
    load_sample = payload.get("load_sample", False)
    
    data = SAMPLE_RESUME_DATA if load_sample else payload.get("data", DEFAULT_RESUME_DATA)
    new_resume = Resume(
        title=title,
        template=template,
        data_json=json.dumps(data, ensure_ascii=False)
    )
    db.session.add(new_resume)
    db.session.commit()
    return jsonify({"success": True, "resume": new_resume.to_dict()}), 201

@resume_bp.route("/api/resumes/<int:resume_id>", methods=["GET"])
def get_resume(resume_id):
    r = db.session.get(Resume, resume_id)
    if not r:
        return jsonify({"success": False, "error": "Resume not found"}), 404
    return jsonify({"success": True, "resume": r.to_dict()})

@resume_bp.route("/api/resumes/<int:resume_id>", methods=["PUT"])
def update_resume(resume_id):
    r = db.session.get(Resume, resume_id)
    if not r:
        return jsonify({"success": False, "error": "Resume not found"}), 404
    payload = request.get_json() or {}
    if "title" in payload:
        r.title = payload["title"]
    if "template" in payload:
        r.template = payload["template"]
    if "data" in payload:
        r.data = payload["data"]
    db.session.commit()
    return jsonify({"success": True, "resume": r.to_dict()})

@resume_bp.route("/api/resumes/<int:resume_id>", methods=["DELETE"])
def delete_resume(resume_id):
    r = db.session.get(Resume, resume_id)
    if not r:
        return jsonify({"success": False, "error": "Resume not found"}), 404
    db.session.delete(r)
    db.session.commit()
    return jsonify({"success": True, "message": "Resume deleted successfully"})

@resume_bp.route("/api/resumes/<int:resume_id>/duplicate", methods=["POST"])
def duplicate_resume(resume_id):
    r = db.session.get(Resume, resume_id)
    if not r:
        return jsonify({"success": False, "error": "Resume not found"}), 404
    dup = Resume(
        title=f"{r.title} (Copy)",
        template=r.template,
        data_json=r.data_json
    )
    db.session.add(dup)
    db.session.commit()
    return jsonify({"success": True, "resume": dup.to_dict()})

@resume_bp.route("/api/resumes/<int:resume_id>/rename", methods=["PUT"])
def rename_resume(resume_id):
    r = db.session.get(Resume, resume_id)
    if not r:
        return jsonify({"success": False, "error": "Resume not found"}), 404
    payload = request.get_json() or {}
    new_title = payload.get("title", "").strip()
    if not new_title:
        return jsonify({"success": False, "error": "Title cannot be blank"}), 400
    r.title = new_title
    db.session.commit()
    return jsonify({"success": True, "resume": r.to_dict()})
