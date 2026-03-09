from __future__ import annotations

import os

from flask import Flask, render_template, request

app = Flask(__name__)
app.config["SITE_NAME"] = os.getenv("SITE_NAME", "Ethical Academy")
app.config["SITE_DOMAIN"] = os.getenv("SITE_DOMAIN", "https://ethical-academy.onrender.com")

LABS = [
    {
        "title": "Authentication Hardening Lab",
        "goal": "Defend a login endpoint with lockouts and strong password policy.",
        "focus": "Brute-force resistance and account security.",
        "difficulty": "Beginner",
        "duration": 45,
        "tags": ["IAM", "Authentication", "Policy"],
    },
    {
        "title": "Input Validation Lab",
        "goal": "Identify unsafe input and apply allowlist validation.",
        "focus": "SQLi and command-injection prevention patterns.",
        "difficulty": "Intermediate",
        "duration": 60,
        "tags": ["Validation", "Secure Coding", "OWASP"],
    },
    {
        "title": "Incident Response Drill",
        "goal": "Read suspicious log events and classify attack stages.",
        "focus": "Detection and triage workflow.",
        "difficulty": "Intermediate",
        "duration": 70,
        "tags": ["Detection", "SOC", "Logs"],
    },
    {
        "title": "Threat Modeling Workshop",
        "goal": "Build a STRIDE model and map controls to attack paths.",
        "focus": "System design security and risk prioritization.",
        "difficulty": "Advanced",
        "duration": 90,
        "tags": ["Architecture", "Threat Modeling", "Risk"],
    },
    {
        "title": "Cloud Misconfiguration Hunt",
        "goal": "Audit identity, network, and storage settings in a cloud sandbox.",
        "focus": "Least privilege and public exposure prevention.",
        "difficulty": "Advanced",
        "duration": 100,
        "tags": ["Cloud", "IAM", "CSPM"],
    },
]

QUIZ = [
    {
        "question": "What is the first requirement before testing any target?",
        "choices": [
            "Written authorization",
            "Admin password",
            "VPN access",
        ],
        "answer": "Written authorization",
        "topic": "Ethics and Legal Scope",
        "explanation": "Every assessment starts with explicit written permission and clear scope.",
    },
    {
        "question": "Which password storage method is recommended?",
        "choices": [
            "Plain text",
            "SHA1 without salt",
            "Argon2 or bcrypt with salt",
        ],
        "answer": "Argon2 or bcrypt with salt",
        "topic": "Identity Security",
        "explanation": "Adaptive hashing plus unique salts slows offline cracking significantly.",
    },
    {
        "question": "What helps reduce brute-force attacks on login?",
        "choices": [
            "Unlimited retries",
            "Rate limiting and lockout controls",
            "Hiding the login page",
        ],
        "answer": "Rate limiting and lockout controls",
        "topic": "Authentication Hardening",
        "explanation": "Rate limits, lockouts, and MFA drastically cut brute-force effectiveness.",
    },
    {
        "question": "Best default approach for user input in backend APIs?",
        "choices": [
            "Block only known bad strings",
            "Allowlist expected patterns and lengths",
            "Trust frontend validation only",
        ],
        "answer": "Allowlist expected patterns and lengths",
        "topic": "Secure Coding",
        "explanation": "Allowlists are safer than deny-lists because unknown malicious patterns still get blocked.",
    },
    {
        "question": "Which control helps detect credential abuse quickly?",
        "choices": [
            "Disable logging",
            "Alerting on unusual login patterns",
            "Longer session timeout",
        ],
        "answer": "Alerting on unusual login patterns",
        "topic": "Monitoring and Detection",
        "explanation": "Behavior-based alerts catch suspicious activity faster than manual review.",
    },
]

LEARNING_PATH = [
    "Understand legal scope, rules of engagement, and reporting requirements.",
    "Practice preventive controls in application and identity layers.",
    "Build detection signals and triage workflows for real incidents.",
    "Map findings to remediations and verify fixes through retesting.",
]

@app.context_processor
def inject_site_config():
    return {
        "site_name": app.config["SITE_NAME"],
        "site_domain": app.config["SITE_DOMAIN"],
    }


@app.route("/")
def home():
    total_labs = len(LABS)
    advanced_labs = sum(1 for lab in LABS if lab["difficulty"] == "Advanced")
    total_quiz_questions = len(QUIZ)
    focus_areas = sorted({tag for lab in LABS for tag in lab["tags"]})
    return render_template(
        "index.html",
        total_labs=total_labs,
        advanced_labs=advanced_labs,
        total_quiz_questions=total_quiz_questions,
        focus_areas=focus_areas,
        learning_path=LEARNING_PATH,
    )


@app.route("/labs")
def labs():
    difficulty_filter = request.args.get("difficulty", "All")
    topic_filter_raw = request.args.get("topic", "").strip()
    topic_filter = topic_filter_raw.lower()
    sort_by = request.args.get("sort", "difficulty")

    filtered_labs = LABS
    if difficulty_filter != "All":
        filtered_labs = [
            lab for lab in filtered_labs if lab["difficulty"] == difficulty_filter
        ]

    if topic_filter:
        filtered_labs = [
            lab
            for lab in filtered_labs
            if any(topic_filter in tag.lower() for tag in lab["tags"])
            or topic_filter in lab["focus"].lower()
        ]

    difficulty_order = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
    if sort_by == "duration":
        filtered_labs = sorted(filtered_labs, key=lambda lab: lab["duration"])
    else:
        filtered_labs = sorted(
            filtered_labs,
            key=lambda lab: (
                difficulty_order.get(lab["difficulty"], 99),
                lab["duration"],
            ),
        )

    topics = sorted({tag for lab in LABS for tag in lab["tags"]})
    return render_template(
        "labs.html",
        labs=filtered_labs,
        selected_difficulty=difficulty_filter,
        selected_topic=topic_filter_raw,
        selected_sort=sort_by,
        topics=topics,
    )


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    score = None
    total = len(QUIZ)
    result = None
    selected_answers: dict[str, str] = {}
    if request.method == "POST":
        score = 0
        question_feedback = []
        topic_errors = {}
        for idx, item in enumerate(QUIZ):
            user_answer = request.form.get(f"q{idx}")
            selected_answers[f"q{idx}"] = user_answer or ""
            if user_answer == item["answer"]:
                score += 1
                is_correct = True
            else:
                is_correct = False
                topic_errors[item["topic"]] = topic_errors.get(item["topic"], 0) + 1

            question_feedback.append(
                {
                    "question": item["question"],
                    "selected": user_answer or "No answer selected",
                    "correct_answer": item["answer"],
                    "is_correct": is_correct,
                    "topic": item["topic"],
                    "explanation": item["explanation"],
                }
            )

        percent = round((score / total) * 100)
        if percent >= 85:
            level = "Strong"
        elif percent >= 60:
            level = "Developing"
        else:
            level = "Needs Practice"

        weak_topics = sorted(topic_errors, key=topic_errors.get, reverse=True)
        recommendations = [
            f"Revisit {topic} concepts before retaking the quiz."
            for topic in weak_topics[:3]
        ]
        if not recommendations:
            recommendations = ["Great work. Move on to advanced labs for deeper practice."]

        result = {
            "percent": percent,
            "level": level,
            "feedback": question_feedback,
            "recommendations": recommendations,
            "weak_topics": weak_topics,
        }
    return render_template(
        "quiz.html",
        quiz=QUIZ,
        score=score,
        total=total,
        result=result,
        selected_answers=selected_answers,
    )


if __name__ == "__main__":
    app.run(debug=False)
