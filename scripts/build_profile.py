#!/usr/bin/env python3
"""Generate the profile README's SVGs from data/profile.json.

    python scripts/build_profile.py --out dist

Writes highlights.svg, project-featured.svg, project-NN.svg, roadmap.svg and
stats.svg. The workflow publishes them to the `output` branch, which is where
README.md loads them from. Standard library only.
"""
import argparse
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from profile_assets import cards, github, roadmap, stats

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "profile.json")
    parser.add_argument("--out", type=Path, default=ROOT / "dist")
    parser.add_argument("--skip-stats", action="store_true",
                        help="do not call the GitHub API (stats.svg is not written)")
    args = parser.parse_args()

    data = json.loads(args.data.read_text(encoding="utf-8"))
    today = datetime.now(timezone.utc).date()

    files = {
        "highlights": cards.highlights(data["highlights"]),
        "project-featured": cards.featured(data["featured"]),
        "roadmap": roadmap.render(data, today),
        **cards.project_cards(data["projects"]),
    }
    if not args.skip_stats:
        files["stats"] = stats.render(github.fetch(data["user"], os.environ.get("GITHUB_TOKEN")))

    args.out.mkdir(parents=True, exist_ok=True)
    for name, svg in files.items():
        ET.fromstring(svg)  # refuse to publish a malformed image
        (args.out / f"{name}.svg").write_text(svg, encoding="utf-8")
        print(f"wrote {args.out / (name + '.svg')}")


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        if os.environ.get("GITHUB_ACTIONS"):
            # Surfaces the cause in the run summary, where it is readable without the logs.
            where = getattr(err, "url", "") or getattr(err, "filename", "") or ""
            print(f"::error title=build_profile.py::{type(err).__name__}: {err} {where}".rstrip())
        raise
