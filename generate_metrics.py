# generate_metrics.py
# pip install PyGithub svgwrite

import os
from github import Github
import svgwrite
from collections import Counter

USERNAME = os.getenv("TARGET_USER") or "your-github-username"

def fetch_stats(token, username):
    gh = Github(token) if token else Github()
    user = gh.get_user(username)
    repos = list(user.get_repos(type="owner"))
    total_repos = user.public_repos
    followers = user.followers

    # total stars across owned repos
    total_stars = sum(r.stargazers_count for r in repos)
    # languages (top 6)
    langs = Counter()
    for r in repos:
        if r.language:
            langs[r.language] += 1
    top_langs = langs.most_common(6)
    return {
        "name": user.name or username,
        "login": username,
        "total_repos": total_repos,
        "followers": followers,
        "total_stars": total_stars,
        "top_langs": top_langs
    }

def render_svg(stats, out_path="github-metrics.svg"):
    w, h = 900, 260
    dwg = svgwrite.Drawing(out_path, size=(w, h))
    bg = dwg.rect(insert=(0,0), size=(w,h), rx=14, ry=14, fill="#0b1226")
    dwg.add(bg)

    # header
    dwg.add(dwg.text(f"{stats['name']} ({stats['login']})",
                     insert=(28,50), fill="#e6eef8",
                     font_size=26, font_family="Verdana", font_weight="bold"))

    # small stats boxes
    box_x = 28
    box_y = 80
    box_w = 260
    box_h = 48
    def add_box(x, y, label, value):
        dwg.add(dwg.rect(insert=(x,y), size=(box_w,box_h), rx=8, fill="#0f1a2b"))
        dwg.add(dwg.text(label, insert=(x+12, y+18), fill="#9fb3d0", font_size=12))
        dwg.add(dwg.text(str(value), insert=(x+12, y+38), fill="#ffffff", font_size=18, font_weight="bold"))
    add_box(box_x, box_y, "Public repos", stats["total_repos"])
    add_box(box_x+box_w+18, box_y, "Followers", stats["followers"])
    add_box(box_x+2*(box_w+18), box_y, "Total stars", stats["total_stars"])

    # Languages
    dwg.add(dwg.text("Top languages", insert=(28, 160), fill="#9fb3d0", font_size=14))
    lx = 28
    ly = 180
    for lang, count in stats["top_langs"]:
        dwg.add(dwg.rect(insert=(lx, ly), size=(160, 28), rx=6, fill="#0f2337"))
        dwg.add(dwg.text(f"{lang} • {count} repo(s)", insert=(lx+10, ly+18), fill="#dff1ff", font_size=13))
        lx += 170

    # footer small note
    dwg.add(dwg.text("Generated automatically — customize me!", insert=(28, 240), fill="#7f98b3", font_size=11))

    dwg.save()

if __name__ == "__main__":
    token = os.getenv("GITHUB_TOKEN")  # provided by Actions
    stats = fetch_stats(token, USERNAME)
    render_svg(stats)
    print("Wrote github-metrics.svg")
