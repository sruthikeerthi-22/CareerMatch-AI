import re
import requests


# =========================================================
# GITHUB API SETTINGS
# =========================================================

GITHUB_API = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2026-03-10"
}


# =========================================================
# EXTRACT GITHUB USERNAME FROM RESUME
# =========================================================

def extract_github_username(text):

    if not text:
        return None

    # Find normal GitHub profile URLs
    pattern = r"(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9-]+)"

    matches = re.findall(pattern, text, re.IGNORECASE)

    if matches:
        return matches[0]

    return None


# =========================================================
# GET GITHUB USER PROFILE
# =========================================================

def get_github_profile(username):

    url = f"{GITHUB_API}/users/{username}"

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        if response.status_code != 200:
            return None

        return response.json()

    except requests.RequestException:
        return None


# =========================================================
# GET USER PUBLIC REPOSITORIES
# =========================================================

def get_github_repositories(username):

    url = f"{GITHUB_API}/users/{username}/repos"

    params = {
        "type": "owner",
        "sort": "updated",
        "direction": "desc",
        "per_page": 100
    }

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return []

        return response.json()

    except requests.RequestException:
        return []


# =========================================================
# GET REPOSITORY LANGUAGES
# =========================================================

def get_repository_languages(username, repo_name):

    url = (
        f"{GITHUB_API}/repos/"
        f"{username}/{repo_name}/languages"
    )

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        if response.status_code != 200:
            return []

        data = response.json()

        return list(data.keys())

    except requests.RequestException:
        return []


# =========================================================
# ANALYZE GITHUB PROFILE
# =========================================================

def analyze_github(username):

    profile = get_github_profile(username)

    if not profile:
        return {
            "found": False,
            "username": username,
            "message": "GitHub profile could not be found."
        }

    repositories = get_github_repositories(username)

    analyzed_repositories = []

    all_languages = set()
    all_topics = set()

    for repo in repositories:

        # Ignore forked repositories
        if repo.get("fork"):
            continue

        repo_name = repo.get("name", "")

        description = repo.get("description") or ""

        topics = repo.get("topics") or []

        languages = get_repository_languages(
            username,
            repo_name
        )

        # Add languages
        for language in languages:
            all_languages.add(language)

        # Add topics
        for topic in topics:
            all_topics.add(topic)

        analyzed_repositories.append({

            "name": repo_name,

            "description": description,

            "languages": languages,

            "topics": topics,

            "stars": repo.get("stargazers_count", 0),

            "url": repo.get("html_url"),

            "updated": repo.get("updated_at")

        })

    return {

        "found": True,

        "username": username,

        "profile_url": profile.get("html_url"),

        "name": profile.get("name"),

        "bio": profile.get("bio"),

        "public_repos": profile.get(
            "public_repos",
            0
        ),

        "followers": profile.get(
            "followers",
            0
        ),

        "repositories": analyzed_repositories,

        "languages": sorted(
            all_languages
        ),

        "topics": sorted(
            all_topics
        )

    }