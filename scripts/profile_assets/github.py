"""Public GitHub numbers for the stats panel, read through the REST API.

Works unauthenticated for local runs (60 requests/hour) and with GITHUB_TOKEN
in Actions. Any API failure raises, so a bad run never publishes empty stats.
"""
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API = "https://api.github.com"
WEEKS = 26


def _get(path, token, **params):
    url = f"{API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-assets"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as res:
        return json.load(res)


def _commit_dates(repo, user, token):
    """Author dates of every commit `user` made in `repo` (newest first, capped at 1000)."""
    dates = []
    for page in range(1, 11):
        try:
            batch = _get(f"/repos/{repo}/commits", token, author=user, per_page=100, page=page)
        except urllib.error.HTTPError as err:
            if err.code == 409:  # empty repository
                return dates
            raise
        dates += [datetime.fromisoformat(c["commit"]["author"]["date"].replace("Z", "+00:00"))
                  for c in batch]
        if len(batch) < 100:
            break
    return dates


def fetch(user, token=None):
    now = datetime.now(timezone.utc)
    profile = _get(f"/users/{user}", token)
    repos = _get(f"/users/{user}/repos", token, type="owner", per_page=100)
    own = [r for r in repos if not r["fork"]]

    language_bytes = {}
    for repo in own:
        for name, size in _get(f"/repos/{repo['full_name']}/languages", token).items():
            language_bytes[name] = language_bytes.get(name, 0) + size
    total = sum(language_bytes.values()) or 1
    languages = sorted(((name, size / total * 100) for name, size in language_bytes.items()),
                       key=lambda item: -item[1])

    # Total and weekly activity come from the same listing so the two always agree.
    commits, weekly, recent, latest = 0, [0] * WEEKS, {}, None
    for repo in repos:
        for when in _commit_dates(repo["full_name"], user, token):
            commits += 1
            latest = max(latest, when) if latest else when
            age = (now - when).days // 7
            if 0 <= age < WEEKS:
                weekly[WEEKS - 1 - age] += 1
                recent[repo["name"]] = recent.get(repo["name"], 0) + 1

    def count(kind, query):
        return _get(f"/search/{kind}", token, q=query, per_page=1)["total_count"]

    return {
        "user": user,
        "repos": profile["public_repos"],
        "followers": profile["followers"],
        "since": profile["created_at"][:4],
        "stars": sum(r["stargazers_count"] for r in own),
        "commits": commits,
        "most_active": max(recent, key=recent.get) if recent else None,
        "last_commit": f"{latest:%b} {latest.day}, {latest.year}" if latest else None,
        "prs": count("issues", f"author:{user} type:pr"),
        "issues": count("issues", f"author:{user} type:issue"),
        "languages": languages,
        "weekly": weekly,
    }
