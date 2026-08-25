from flask import Flask, render_template, request
import os

from utils.pdf_parser import extract_text_from_pdf
from utils.career_matcher import extract_skills, match_careers

from utils.github_analyzer import (
    extract_github_username,
    analyze_github
)


app = Flask(__name__)


# =========================================================
# UPLOAD SETTINGS
# =========================================================

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# RESUME SCORE
# =========================================================

def calculate_resume_score(
    skills,
    career_results
):

    if not skills:
        return 0

    best_career_score = 0

    if career_results:

        best_career_score = (
            career_results[0]["score"]
        )

    skill_count = len(skills)

    skill_score = min(
        skill_count * 5,
        30
    )

    overall_score = round(
        (best_career_score * 0.7)
        + skill_score
    )

    overall_score = min(
        overall_score,
        100
    )

    return overall_score


# =========================================================
# RESUME STRENGTHS
# =========================================================

def generate_strengths(
    skills,
    career_results
):

    strengths = []

    if len(skills) >= 8:

        strengths.append(
            "Your resume demonstrates a strong technical skill set."
        )

    elif len(skills) >= 5:

        strengths.append(
            "Your resume shows a good foundation of technical skills."
        )

    elif len(skills) >= 3:

        strengths.append(
            "Your resume has a basic technical skill foundation."
        )

    else:

        strengths.append(
            "Your resume contains some technical skills that can be developed further."
        )

    if career_results:

        top_career = career_results[0]

        if top_career["score"] >= 80:

            strengths.append(
                f"Your skills strongly match the "
                f"{top_career['career']} career path."
            )

        elif top_career["score"] >= 50:

            strengths.append(
                f"You have a moderate skill match for "
                f"{top_career['career']}."
            )

        else:

            strengths.append(
                f"{top_career['career']} is currently your closest career match."
            )

    important_skills = [

        "python",
        "java",
        "javascript",
        "machine learning",
        "data science",
        "flask",
        "django",
        "sql",
        "git",
        "github"

    ]

    detected_important = [

        skill
        for skill in important_skills
        if skill in skills

    ]

    if detected_important:

        strengths.append(
            "You have experience with relevant "
            "industry technologies such as "
            + ", ".join(
                detected_important[:5]
            )
            + "."
        )

    return strengths


# =========================================================
# RESUME IMPROVEMENT SUGGESTIONS
# =========================================================

def generate_suggestions(
    skills,
    career_results
):

    suggestions = []

    if not skills:

        suggestions.append(
            "Add a dedicated Technical Skills section to your resume."
        )

        suggestions.append(
            "Mention programming languages, frameworks, databases and tools you have worked with."
        )

        return suggestions

    if len(skills) < 5:

        suggestions.append(
            "Expand your technical skill section by adding relevant programming languages, tools and frameworks."
        )

    elif len(skills) < 8:

        suggestions.append(
            "Consider adding more relevant technical skills to strengthen your resume."
        )

    if career_results:

        top_career = career_results[0]

        missing_skills = (
            top_career["missing"]
        )

        if missing_skills:

            readable_missing = [

                skill.title()
                for skill in missing_skills[:4]

            ]

            suggestions.append(
                f"For {top_career['career']}, "
                f"consider learning: "
                + ", ".join(
                    readable_missing
                )
                + "."
            )

        recommended = (
            top_career["info"]["recommended"]
        )

        if recommended:

            suggestions.append(
                "You can also strengthen your profile with: "
                + ", ".join(
                    recommended[:3]
                )
                + "."
            )

    suggestions.append(
        "Add project descriptions that clearly explain your role, technologies used and results achieved."
    )

    suggestions.append(
        "Include measurable achievements wherever possible, such as performance improvements, accuracy or project impact."
    )

    return suggestions


# =========================================================
# GITHUB PROJECT INSIGHTS
# =========================================================

def generate_github_insights(
    github_data,
    skills
):

    insights = []

    if not github_data:
        return insights

    if not github_data.get("found"):
        return insights

    repositories = github_data.get(
        "repositories",
        []
    )

    github_languages = [
        language.lower()
        for language in github_data.get(
            "languages",
            []
        )
    ]

    resume_skills = [
        skill.lower()
        for skill in skills
    ]

    # -----------------------------------------------------
    # GitHub projects
    # -----------------------------------------------------

    if repositories:

        insights.append(
            f"Your GitHub profile contains "
            f"{len(repositories)} public project(s) "
            f"that can support your technical profile."
        )

    # -----------------------------------------------------
    # GitHub language evidence
    # -----------------------------------------------------

    matching_languages = []

    for language in github_languages:

        if language in resume_skills:

            matching_languages.append(
                language
            )

    if matching_languages:

        insights.append(
            "Your GitHub projects provide practical evidence "
            "for skills such as "
            + ", ".join(
                matching_languages[:5]
            )
            + "."
        )

    # -----------------------------------------------------
    # Resume skill not found in GitHub
    # -----------------------------------------------------

    if resume_skills and github_languages:

        missing_project_evidence = [

            skill
            for skill in resume_skills
            if skill in [
                "python",
                "java",
                "javascript",
                "c++",
                "c",
                "sql"
            ]
            and skill not in github_languages

        ]

        if missing_project_evidence:

            insights.append(
                "Consider adding GitHub projects demonstrating "
                + ", ".join(
                    missing_project_evidence[:3]
                )
                + "."
            )

    return insights


# =========================================================
# RESUME UPLOAD
# =========================================================

@app.route(
    "/upload",
    methods=["POST"]
)
def upload_resume():

    # -----------------------------------------------------
    # CHECK FILE
    # -----------------------------------------------------

    if "resume" not in request.files:

        return "No resume file selected."

    file = request.files["resume"]

    if file.filename == "":

        return "No resume file selected."

    if not file.filename.lower().endswith(".pdf"):

        return "Please upload a PDF resume."

    # -----------------------------------------------------
    # SAVE RESUME
    # -----------------------------------------------------

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    # -----------------------------------------------------
    # EXTRACT TEXT
    # -----------------------------------------------------

    resume_text = extract_text_from_pdf(
        filepath
    )

    if not resume_text.strip():

        return "Could not extract text from this PDF."

    # -----------------------------------------------------
    # DETECT SKILLS
    # -----------------------------------------------------

    skills = extract_skills(
        resume_text
    )

    # -----------------------------------------------------
    # CAREER MATCHING
    # -----------------------------------------------------

    career_results = match_careers(
        skills
    )

    # -----------------------------------------------------
    # RESUME SCORE
    # -----------------------------------------------------

    resume_score = calculate_resume_score(
        skills,
        career_results
    )

    # -----------------------------------------------------
    # STRENGTHS
    # -----------------------------------------------------

    strengths = generate_strengths(
        skills,
        career_results
    )

    # -----------------------------------------------------
    # SUGGESTIONS
    # -----------------------------------------------------

    suggestions = generate_suggestions(
        skills,
        career_results
    )

    # -----------------------------------------------------
    # GITHUB ANALYSIS
    # -----------------------------------------------------

    github_username = extract_github_username(
        resume_text
    )

    github_data = None

    if github_username:

        github_data = analyze_github(
            github_username
        )

    # -----------------------------------------------------
    # GITHUB INSIGHTS
    # -----------------------------------------------------

    github_insights = generate_github_insights(
        github_data,
        skills
    )

    # -----------------------------------------------------
    # RESULTS PAGE
    # -----------------------------------------------------

    return render_template(

        "results.html",

        skills=skills,

        careers=career_results,

        resume_score=resume_score,

        strengths=strengths,

        suggestions=suggestions,

        github_data=github_data,

        github_username=github_username,

        github_insights=github_insights

    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )