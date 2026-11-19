import html
import json
import os
import urllib.request
from datetime import datetime

USERNAME = "md-kamran400"
OUTPUT = "assets/activity.svg"
API_URL = f"https://api.github.com/users/{USERNAME}/events/public?per_page=100"


def fetch_events():
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-readme-activity-generator", "X-GitHub-Api-Version": "2022-11-28"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(API_URL, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def safe_text(value, limit=88):
    value = " ".join(str(value or "").split())
    if len(value) > limit:
        value = value[:limit - 1] + "…"
    return html.escape(value, quote=True)


def make_svg(events):
    pushes, seen = [], set()
    for event in events:
        if event.get("type") != "PushEvent":
            continue
        repo = event.get("repo", {}).get("name", "")
        created = event.get("created_at", "")
        for commit in event.get("payload", {}).get("commits", []):
            sha = commit.get("sha", "")
            if not sha or sha in seen:
                continue
            seen.add(sha)
            pushes.append({"repo": repo, "date": created, "message": commit.get("message", "").splitlines()[0], "sha": sha})
            if len(pushes) == 5:
                break
        if len(pushes) == 5:
            break

    rows = []
    for index, item in enumerate(pushes):
        y = 82 + index * 36
        try:
            stamp = datetime.fromisoformat(item["date"].replace("Z", "+00:00")).strftime("%b %d")
        except (ValueError, TypeError):
            stamp = "recent"
        repo = safe_text(item["repo"], 30)
        message = safe_text(item["message"], 72)
        link = f"https://github.com/{item['repo']}/commit/{item['sha']}"
        rows.append(f'<circle cx="34" cy="{y-4}" r="4" fill="#E63946"><animate attributeName="opacity" values=".55;1;.55" dur="3.4s" begin="{index*0.35}s" repeatCount="indefinite"/></circle><a href="{html.escape(link, quote=True)}"><text x="52" y="{y}" fill="#FF737B" font-family="monospace" font-size="12">{stamp} · {repo}</text><text x="270" y="{y}" fill="#F4F4F5" font-family="monospace" font-size="12">{message}</text></a>')

    height = 220
    if not rows:
        rows = ['<circle cx="34" cy="92" r="4" fill="#E63946"/><text x="52" y="96" fill="#F4F4F5" font-family="monospace" font-size="14">No recent public push events were returned.</text>', '<text x="52" y="126" fill="#A1A1AA" font-family="monospace" font-size="12">GitHub event history is limited; visit the profile for current activity.</text>']
        height = 190

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="920" height="{height}" viewBox="0 0 920 {height}" role="img"><rect width="920" height="{height}" rx="14" fill="#101012" stroke="#28282D"/><text x="26" y="38" fill="#FF4D5A" font-family="monospace" font-size="13" letter-spacing="2">PUBLIC PUSH ACTIVITY / AUTO-UPDATED</text><path d="M34 66V{height-28}" stroke="#8B0000" stroke-width="2"/>{"".join(rows)}<text x="26" y="{height-12}" fill="#71717A" font-family="monospace" font-size="10">ACTUAL PUBLIC PUSH EVENTS · COMMIT DETAILS LINK TO GITHUB</text></svg>'''


def main():
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    try:
        svg = make_svg(fetch_events())
    except Exception as error:
        print(f"Could not fetch GitHub events: {error}")
        return
    with open(OUTPUT, "w", encoding="utf-8") as file:
        file.write(svg)


if __name__ == "__main__":
    main()
