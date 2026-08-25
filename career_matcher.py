import re


# =========================================================
# SKILLS THAT CAREERMATCH AI CAN DETECT
# =========================================================

SKILLS = [
    "python",
    "java",
    "c++",
    "c",
    "sql",
    "html",
    "css",
    "javascript",
    "flask",
    "django",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "data analysis",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "git",
    "github",
    "mongodb",
    "mysql",
    "cloud computing"
]


# =========================================================
# SKILLS REQUIRED FOR EACH CAREER
# =========================================================

CAREER_SKILLS = {

    "Software Developer": [
        "python",
        "java",
        "c++",
        "sql",
        "git",
        "github"
    ],

    "Web Developer": [
        "html",
        "css",
        "javascript",
        "flask",
        "django"
    ],

    "Data Scientist": [
        "python",
        "sql",
        "pandas",
        "numpy",
        "machine learning",
        "data science",
        "scikit-learn"
    ],

    "Machine Learning Engineer": [
        "python",
        "machine learning",
        "scikit-learn",
        "tensorflow",
        "numpy",
        "pandas"
    ],

    "Data Analyst": [
        "python",
        "sql",
        "pandas",
        "numpy",
        "data analysis"
    ],

    "AI Engineer": [
        "python",
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "tensorflow"
    ]
}


# =========================================================
# CAREER INFORMATION
# =========================================================

CAREER_INFO = {

    "Software Developer": {
        "description":
            "Builds and maintains software applications, programs and systems.",

        "recommended": [
            "Data Structures",
            "Algorithms",
            "REST API",
            "GitHub"
        ]
    },

    "Web Developer": {
        "description":
            "Creates and maintains websites and modern web applications.",

        "recommended": [
            "React",
            "REST API",
            "Bootstrap",
            "Node.js"
        ]
    },

    "Data Scientist": {
        "description":
            "Uses data, statistics and machine learning to discover insights and solve problems.",

        "recommended": [
            "Statistics",
            "Data Visualization",
            "Deep Learning",
            "Power BI"
        ]
    },

    "Machine Learning Engineer": {
        "description":
            "Develops, trains and deploys machine learning models for real-world applications.",

        "recommended": [
            "Deep Learning",
            "MLOps",
            "TensorFlow",
            "Model Deployment"
        ]
    },

    "Data Analyst": {
        "description":
            "Analyzes data and creates useful insights to support business decisions.",

        "recommended": [
            "Excel",
            "Power BI",
            "Statistics",
            "Data Visualization"
        ]
    },

    "AI Engineer": {
        "description":
            "Develops intelligent applications using artificial intelligence and machine learning.",

        "recommended": [
            "Deep Learning",
            "NLP",
            "Generative AI",
            "Computer Vision"
        ]
    }
}


# =========================================================
# EXTRACT SKILLS FROM RESUME
# =========================================================

def extract_skills(text):

    text = text.lower()

    found_skills = []

    for skill in SKILLS:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text):

            found_skills.append(skill)

    return found_skills


# =========================================================
# MATCH RESUME SKILLS WITH CAREERS
# =========================================================

def match_careers(skills):

    skills = set(
        skill.lower()
        for skill in skills
    )

    results = []

    for career, required_skills in CAREER_SKILLS.items():

        # Find matched skills
        matched = [
            skill
            for skill in required_skills
            if skill in skills
        ]

        # Find missing skills
        missing = [
            skill
            for skill in required_skills
            if skill not in skills
        ]

        # Calculate percentage
        score = round(
            (len(matched) / len(required_skills)) * 100
        )

        # Add career result
        results.append({

            "career": career,

            "score": score,

            "skills": matched,

            "missing": missing,

            "info": CAREER_INFO[career]

        })

    # Highest score first
    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results