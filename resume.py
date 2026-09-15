import json
from datetime import datetime
from models import db

DEFAULT_RESUME_DATA = {
    "personal": {
        "name": "",
        "title": "",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "github": "",
        "portfolio": ""
    },
    "summary": "",
    "education": [],
    "experience": [],
    "projects": [],
    "skills": {
        "programming": [],
        "frameworks": [],
        "web": [],
        "databases": [],
        "tools": [],
        "soft": []
    },
    "certifications": [],
    "achievements": [],
    "internships": [],
    "languages": []
}

SAMPLE_RESUME_DATA = {
    "personal": {
        "name": "Sneha Sai",
        "title": "Software Developer & Python Specialist",
        "email": "sneha.sai@example.com",
        "phone": "+1 (555) 349-2810",
        "location": "San Francisco, CA",
        "linkedin": "linkedin.com/in/snehasai",
        "github": "github.com/snehasai",
        "portfolio": "snehasai.dev"
    },
    "summary": "Results-oriented Software Developer with strong foundational expertise in Python, web architectures, and relational database systems. Proven track record of developing responsive web applications, optimizing backend workflows, and solving real-world challenges through clean, maintainable code.",
    "education": [
        {
            "degree": "B.Tech in Computer Science & Engineering",
            "university": "ABC University",
            "location": "San Jose, CA",
            "startYear": "2020",
            "endYear": "2024",
            "gpa": "3.85 / 4.0",
            "description": "Graduated Magna Cum Laude. Coursework in Data Structures & Algorithms, Database Systems, Computer Networks, and Distributed Computing."
        }
    ],
    "experience": [
        {
            "jobTitle": "Software Developer Intern",
            "company": "ABC Technologies",
            "location": "San Francisco, CA",
            "startDate": "Jun 2023",
            "endDate": "Dec 2023",
            "currentlyWorking": False,
            "responsibilities": "Developed modular Python backend services for high-traffic web applications.\nIdentified and resolved 40+ application bugs and improved system stability.\nCollaborated with cross-functional engineering teams during agile sprints.",
            "achievements": "Spearheaded caching improvements that reduced server response times.",
            "description": "• Developed modular Python backend services for high-traffic web applications.\n• Identified and resolved application issues, contributing to test coverage improvements.\n• Streamlined API endpoints to optimize database query performance."
        }
    ],
    "projects": [
        {
            "name": "Travel Buddy",
            "projectUrl": "https://travelbuddy.example.com",
            "githubUrl": "https://github.com/snehasai/travel-buddy",
            "technologies": "Python, Flask, SQLite, HTML5, CSS3, JavaScript",
            "rawDescription": "Website to help users find hotels and restaurants in their destination city.",
            "description": "Developed a comprehensive travel planning web application using Python and Flask that empowers users to discover, filter, and review nearby hotels and restaurants."
        },
        {
            "name": "Intelligent Task Planner",
            "projectUrl": "https://taskplanner.example.com",
            "githubUrl": "https://github.com/snehasai/task-planner",
            "technologies": "Python, Django, PostgreSQL, Bootstrap",
            "rawDescription": "Task management tool with deadline alerts and team collaboration.",
            "description": "Architected a collaborative task management platform featuring real-time status tracking, automated notification schedules, and role-based access controls."
        }
    ],
    "skills": {
        "programming": ["Python", "Java", "C++", "SQL", "JavaScript"],
        "frameworks": ["Flask", "Django", "FastAPI"],
        "web": ["HTML5", "CSS3", "REST APIs", "JSON", "Bootstrap"],
        "databases": ["PostgreSQL", "MySQL", "SQLite"],
        "tools": ["Git", "GitHub", "Docker", "VS Code", "Postman"],
        "soft": ["Problem Solving", "Team Collaboration", "Communication", "Critical Thinking"]
    },
    "certifications": [
        {
            "name": "Python Institute Certified Associate Programmer (PCAP)",
            "issuer": "Python Institute",
            "date": "2023",
            "credentialUrl": "https://pythoninstitute.org/verify/12345",
            "description": "Demonstrated core competency in Python 3 object-oriented programming, data structures, and file operations."
        }
    ],
    "achievements": [
        {
            "title": "1st Place Winner - Regional University Hackathon",
            "date": "Nov 2023",
            "description": "Built an accessible educational web tool within 36 hours among 45 competing university teams."
        }
    ],
    "internships": [
        {
            "organization": "NextGen Web Labs",
            "role": "Web Development Trainee",
            "duration": "Jan 2023 - May 2023",
            "responsibilities": "Assisted in building responsive landing pages and integrating client REST APIs.",
            "description": "Delivered responsive web interfaces using semantic HTML and CSS, ensuring mobile-first compatibility."
        }
    ],
    "languages": [
        {"language": "English", "proficiency": "Professional"},
        {"language": "Hindi", "proficiency": "Professional"},
        {"language": "Telugu", "proficiency": "Native"}
    ]
}

class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, default="Untitled Resume")
    template = db.Column(db.String(50), nullable=False, default="classic")
    data_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def data(self):
        try:
            return json.loads(self.data_json) if self.data_json else DEFAULT_RESUME_DATA.copy()
        except Exception:
            return DEFAULT_RESUME_DATA.copy()

    @data.setter
    def data(self, val):
        self.data_json = json.dumps(val, ensure_ascii=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "template": self.template,
            "data": self.data,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
        }
