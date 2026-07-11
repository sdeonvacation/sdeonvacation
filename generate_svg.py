"""Generate a neofetch-style GitHub profile SVG with live stats."""

import json
import os
import urllib.request
from datetime import datetime, timezone
from typing import Any


GITHUB_USERNAME = "sdeonvacation"
OUTPUT_FILE = "github_profile_dark.svg"


def github_api_get(endpoint: str) -> Any:
    """Fetch from GitHub API with optional token auth."""
    url = f"https://api.github.com{endpoint}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-profile-svg-generator",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_stats() -> dict:
    """Fetch user profile and compute total stars."""
    user = github_api_get(f"/users/{GITHUB_USERNAME}")

    # Paginate repos to sum all stars
    total_stars = 0
    page = 1
    while True:
        repos = github_api_get(
            f"/users/{GITHUB_USERNAME}/repos?per_page=100&page={page}"
        )
        if not repos:
            break
        total_stars += sum(r.get("stargazers_count", 0) for r in repos)
        if len(repos) < 100:
            break
        page += 1

    return {
        "repos": user["public_repos"],
        "stars": total_stars,
        "followers": user["followers"],
        "following": user["following"],
        "created_at": user["created_at"],
    }


def calculate_uptime(created_at: str) -> str:
    """Calculate uptime from account creation to now."""
    created = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )
    now = datetime.now(timezone.utc)

    # Calculate years, months, days difference
    years = now.year - created.year
    months = now.month - created.month
    days = now.day - created.day

    if days < 0:
        months -= 1
        # Days in previous month
        prev_month = now.month - 1 if now.month > 1 else 12
        prev_year = now.year if now.month > 1 else now.year - 1
        if prev_month in (1, 3, 5, 7, 8, 10, 12):
            days_in_prev = 31
        elif prev_month in (4, 6, 9, 11):
            days_in_prev = 30
        else:
            # February
            if prev_year % 4 == 0 and (prev_year % 100 != 0 or prev_year % 400 == 0):
                days_in_prev = 29
            else:
                days_in_prev = 28
        days += days_in_prev

    if months < 0:
        years -= 1
        months += 12

    return f"{years} years, {months} months, {days} days"


def generate_svg(stats: dict) -> str:
    """Generate the full SVG string with dynamic stats injected."""
    uptime = calculate_uptime(stats["created_at"])
    repos = stats["repos"]
    stars = stats["stars"]
    followers = stats["followers"]
    following = stats["following"]

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="850" height="480" viewBox="0 0 850 480">
  <!-- Background -->
  <rect x="0" y="0" width="850" height="480" rx="8" ry="8" fill="#0d1117"/>
  <!-- Title bar -->
  <rect x="0" y="0" width="850" height="28" rx="8" ry="8" fill="#161b22"/>
  <rect x="0" y="14" width="850" height="14" fill="#161b22"/>
  <!-- Traffic lights -->
  <circle cx="16" cy="14" r="5" fill="#ff5f56"/>
  <circle cx="34" cy="14" r="5" fill="#ffbd2e"/>
  <circle cx="52" cy="14" r="5" fill="#27c93f"/>
  <!-- Title bar text -->
  <text x="425" y="18" fill="#8b949e" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="11" text-anchor="middle">sdeonvacation@github ~ neofetch</text>

  <!-- Laptop - Monitor frame -->
  <rect x="55" y="45" width="200" height="190" rx="4" ry="4" fill="none" stroke="#61afef" stroke-width="2"/>
  <!-- Laptop - Screen -->
  <rect x="70" y="58" width="170" height="162" rx="2" ry="2" fill="#161b22" stroke="#98c379" stroke-width="1.5"/>
  <!-- Laptop - Stand -->
  <line x1="105" y1="235" x2="85" y2="260" stroke="#61afef" stroke-width="2"/>
  <line x1="205" y1="235" x2="225" y2="260" stroke="#61afef" stroke-width="2"/>
  <line x1="85" y1="260" x2="225" y2="260" stroke="#61afef" stroke-width="1.5"/>
  <!-- Laptop - Keyboard base -->
  <rect x="55" y="262" width="200" height="16" rx="2" ry="2" fill="none" stroke="#5c6370" stroke-width="1.5"/>
  <!-- Terminal text inside screen -->
  <text x="82" y="82" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#e5c07b">~/projects</tspan>
  </text>
  <text x="82" y="100" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#56b6c2">$</tspan><tspan fill="#abb2bf"> neofetch</tspan>
  </text>
  <text x="82" y="118" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#56b6c2">$</tspan><tspan fill="#c678dd"> git push</tspan>
  </text>
  <text x="82" y="136" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#56b6c2">$</tspan><tspan fill="#e06c75"> mvn deploy</tspan>
  </text>
  <text x="82" y="154" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#56b6c2">$</tspan><tspan fill="#d19a66"> npm run build</tspan>
  </text>
  <text x="82" y="172" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#56b6c2">$</tspan><tspan fill="#98c379"> &#x2588;</tspan>
  </text>

  <!-- Right column - Info -->
  <text x="380" y="58" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#56b6c2" font-weight="bold">sdeonvacation</tspan><tspan fill="#abb2bf"> \u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014</tspan>
  </text>
  <!-- System info -->
  <text x="380" y="78" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#98c379">.</tspan><tspan fill="#56b6c2"> OS:</tspan><tspan fill="#5c6370"> ................... </tspan><tspan fill="#d19a66">macOS, Linux</tspan>
  </text>
  <text x="380" y="96" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#98c379">.</tspan><tspan fill="#56b6c2"> Uptime:</tspan><tspan fill="#5c6370"> ............... </tspan><tspan fill="#d19a66">{uptime}</tspan>
  </text>
  <text x="380" y="114" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#98c379">.</tspan><tspan fill="#56b6c2"> Host:</tspan><tspan fill="#5c6370"> ................. </tspan><tspan fill="#d19a66">SAP SE</tspan>
  </text>
  <text x="380" y="132" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#98c379">.</tspan><tspan fill="#56b6c2"> Kernel:</tspan><tspan fill="#5c6370"> ............... </tspan><tspan fill="#d19a66">Cloud Application Programming</tspan>
  </text>
  <text x="380" y="150" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#98c379">.</tspan><tspan fill="#56b6c2"> IDE:</tspan><tspan fill="#5c6370"> .................. </tspan><tspan fill="#d19a66">IntelliJ IDEA, VS Code</tspan>
  </text>
  <!-- Languages -->
  <text x="380" y="178" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#98c379">.</tspan><tspan fill="#56b6c2"> Languages.Programming:</tspan><tspan fill="#5c6370">  </tspan><tspan fill="#d19a66">Java, Kotlin, Python</tspan>
  </text>
  <text x="380" y="196" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#98c379">.</tspan><tspan fill="#56b6c2"> Languages.Scripting:</tspan><tspan fill="#5c6370"> .. </tspan><tspan fill="#d19a66">TypeScript, Shell</tspan>
  </text>
  <text x="380" y="214" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#98c379">.</tspan><tspan fill="#56b6c2"> Languages.Markup:</tspan><tspan fill="#5c6370"> ..... </tspan><tspan fill="#d19a66">HTML, CSS, YAML</tspan>
  </text>
  <!-- Hobbies -->
  <text x="380" y="242" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#98c379">.</tspan><tspan fill="#56b6c2"> Hobbies.Software:</tspan><tspan fill="#5c6370"> .... </tspan><tspan fill="#d19a66">Open Source, Automation</tspan>
  </text>
  <text x="380" y="260" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#98c379">.</tspan><tspan fill="#56b6c2"> Hobbies.Other:</tspan><tspan fill="#5c6370"> ....... </tspan><tspan fill="#d19a66">Travel, The Office quotes</tspan>
  </text>
  <!-- Contact section -->
  <text x="380" y="290" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#e5c07b">\u2013 Contact \u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014</tspan>
  </text>
  <text x="380" y="310" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#98c379">.</tspan><tspan fill="#56b6c2"> Email:</tspan><tspan fill="#5c6370"> ................ </tspan><tspan fill="#d19a66">mauryasde@gmail.com</tspan>
  </text>
  <text x="380" y="328" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#98c379">.</tspan><tspan fill="#56b6c2"> GitHub:</tspan><tspan fill="#5c6370"> ............... </tspan><tspan fill="#d19a66">sdeonvacation</tspan>
  </text>
  <text x="380" y="346" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#98c379">.</tspan><tspan fill="#56b6c2"> Company:</tspan><tspan fill="#5c6370"> .............. </tspan><tspan fill="#d19a66">SAP SE</tspan>
  </text>
  <!-- GitHub Stats section -->
  <text x="380" y="376" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#e5c07b">\u2013 GitHub Stats \u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014\u2014</tspan>
  </text>
  <text x="380" y="396" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#98c379">.</tspan><tspan fill="#56b6c2"> Repos:</tspan><tspan fill="#5c6370"> .... </tspan><tspan fill="#98c379">{repos}</tspan><tspan fill="#abb2bf">    </tspan><tspan fill="#5c6370">|</tspan><tspan fill="#56b6c2"> Stars:</tspan><tspan fill="#5c6370"> ......... </tspan><tspan fill="#e5c07b">{stars}</tspan>
  </text>
  <text x="380" y="414" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#98c379">.</tspan><tspan fill="#56b6c2"> Followers:</tspan><tspan fill="#5c6370"> </tspan><tspan fill="#98c379">{followers}</tspan><tspan fill="#abb2bf">     </tspan><tspan fill="#5c6370">|</tspan><tspan fill="#56b6c2"> Following:</tspan><tspan fill="#5c6370"> ..... </tspan><tspan fill="#e5c07b">{following}</tspan>
  </text>
  <!-- Bio -->
  <text x="380" y="440" font-family="Consolas, Monaco, 'Courier New', monospace" font-size="13">
    <tspan fill="#98c379">.</tspan><tspan fill="#56b6c2"> Bio:</tspan><tspan fill="#c678dd"> "Identity theft is not a joke, Jim!"</tspan>
  </text>
  <!-- Color palette bar -->
  <rect x="380" y="454" width="24" height="10" fill="#e06c75"/>
  <rect x="404" y="454" width="24" height="10" fill="#d19a66"/>
  <rect x="428" y="454" width="24" height="10" fill="#e5c07b"/>
  <rect x="452" y="454" width="24" height="10" fill="#98c379"/>
  <rect x="476" y="454" width="24" height="10" fill="#56b6c2"/>
  <rect x="500" y="454" width="24" height="10" fill="#61afef"/>
  <rect x="524" y="454" width="24" height="10" fill="#c678dd"/>
  <rect x="548" y="454" width="24" height="10" fill="#abb2bf"/>
</svg>
"""


def main():
    print(f"Fetching GitHub stats for {GITHUB_USERNAME}...")
    stats = fetch_stats()
    print(f"  Repos: {stats['repos']}")
    print(f"  Stars: {stats['stars']}")
    print(f"  Followers: {stats['followers']}")
    print(f"  Following: {stats['following']}")
    print(f"  Uptime: {calculate_uptime(stats['created_at'])}")

    svg_content = generate_svg(stats)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"SVG written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
