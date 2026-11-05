
#!/usr/bin/env python3
"""Generate NBA Scores RSS 2.0 with favorite teams prioritized."""

import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime

API_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
OUT_DIR = "public"
OUT_FILE = os.path.join(OUT_DIR, "nba-scores.xml")

# Favorite team priority
FAVORITES = {
    "PHI": 0,  # Philadelphia 76ers - First
    "LAL": 1,  # Los Angeles Lakers - Second
}

def get_text(value, default=""):
    return str(value) if value is not None else default


def get_priority(event):
    competitions = event.get("competitions", [])

    if not competitions:
        return 2

    competitors = competitions[0].get("competitors", [])

    abbreviations = {
        c.get("team", {}).get("abbreviation")
        for c in competitors
    }

    for team in ("PHI", "LAL"):
        if team in abbreviations:
            return FAVORITES[team]

    return 2


def main():
    request = urllib.request.Request(
        API_URL,
        headers={"User-Agent": "NBA-Scores-RSS/1.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "NBA Scores - Favorite Teams First"
    ET.SubElement(channel, "link").text = "https://www.espn.com/nba/scoreboard"
    ET.SubElement(channel, "description").text = (
        "NBA scores prioritized: Philadelphia 76ers, "
        "Los Angeles Lakers, followed by all other teams."
    )
    ET.SubElement(channel, "language").text = "en-us"

    ET.SubElement(channel, "lastBuildDate").text = (
        format_datetime(datetime.now(timezone.utc))
    )

    events = data.get("events", [])

    # Sort: 76ers first, Lakers second, all others afterward.
    events.sort(key=get_priority)

    for event in events:
        competitions = event.get("competitions", [])

        if not competitions:
            continue

        competition = competitions[0]
        competitors = competition.get("competitors", [])

        home = next(
            (c for c in competitors if c.get("homeAway") == "home"),
            None
        )

        away = next(
            (c for c in competitors if c.get("homeAway") == "away"),
            None
        )

        if not home or not away:
            continue

        home_team = home.get("team", {}).get("displayName", "Home")
        away_team = away.get("team", {}).get("displayName", "Away")

        home_abbr = home.get("team", {}).get("abbreviation", "")
        away_abbr = away.get("team", {}).get("abbreviation", "")

        home_score = get_text(home.get("score"), "0")
        away_score = get_text(away.get("score"), "0")

        status = event.get("status", {}).get("type", {})

        status_name = (
            status.get("shortDetail")
            or status.get("description")
            or "Scheduled"
        )

        if status.get("state") == "in":
            status_name = status.get("shortDetail") or "Live"
        elif status.get("completed"):
            status_name = "Final"

        priority = get_priority(event)

        if priority == 0:
            prefix = "[76ERS]"
        elif priority == 1:
            prefix = "[LAKERS]"
        else:
            prefix = "[NBA]"

        title = (
            f"{prefix} {away_abbr} {away_score} - "
            f"{home_abbr} {home_score} | {status_name}"
        )

        description = (
            f"{away_team} {away_score} at {home_team} "
            f"{home_score}. Status: {status_name}."
        )

        item = ET.SubElement(channel, "item")

        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "description").text = description

        ET.SubElement(item, "link").text = (
            f"https://www.espn.com/nba/game/_/gameId/{event.get('id', '')}"
        )

        ET.SubElement(
            item, "guid", isPermaLink="false"
        ).text = (
            f"{event.get('id', 'game')}-"
            f"{status.get('state', 'pre')}-"
            f"{away_score}-{home_score}-{status_name}"
        )

        date_text = event.get("date", "")

        if date_text:
            try:
                dt = datetime.fromisoformat(
                    date_text.replace("Z", "+00:00")
                )

                ET.SubElement(item, "pubDate").text = (
                    format_datetime(dt)
                )
            except ValueError:
                pass

    os.makedirs(OUT_DIR, exist_ok=True)

    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")

    tree.write(
        OUT_FILE,
        encoding="utf-8",
        xml_declaration=True
    )

    print(f"Generated NBA RSS with {len(events)} games.")


if __name__ == "__main__":
    main()
