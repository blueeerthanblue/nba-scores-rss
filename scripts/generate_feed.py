#!/usr/bin/env python3
"""Generate a valid RSS 2.0 feed containing NBA scoreboard items."""
import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime

API_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
OUT_DIR = "public"
OUT_FILE = os.path.join(OUT_DIR, "nba-scores.xml")

def get_text(value, default=""):
    return str(value) if value is not None else default

def main():
    request = urllib.request.Request(
        API_URL,
        headers={"User-Agent": "NBA-Scores-RSS/1.0"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)

    ET.register_namespace("", "")
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "NBA Scores"
    ET.SubElement(channel, "link").text = "https://www.espn.com/nba/scoreboard"
    ET.SubElement(channel, "description").text = (
        "NBA game scores only: live scores, final results, and upcoming games."
    )
    ET.SubElement(channel, "language").text = "en-us"
    ET.SubElement(channel, "lastBuildDate").text = format_datetime(datetime.now(timezone.utc))

    events = data.get("events", [])
    for event in events:
        competitions = event.get("competitions", [])
        if not competitions:
            continue
        competition = competitions[0]
        competitors = competition.get("competitors", [])
        home = next((c for c in competitors if c.get("homeAway") == "home"), None)
        away = next((c for c in competitors if c.get("homeAway") == "away"), None)
        if not home or not away:
            continue

        home_team = home.get("team", {}).get("displayName", "Home")
        away_team = away.get("team", {}).get("displayName", "Away")
        home_abbr = home.get("team", {}).get("abbreviation", "")
        away_abbr = away.get("team", {}).get("abbreviation", "")
        home_score = get_text(home.get("score"), "0")
        away_score = get_text(away.get("score"), "0")

        status = event.get("status", {}).get("type", {})
        status_name = status.get("shortDetail") or status.get("description") or "Scheduled"
        completed = bool(status.get("completed"))
        state = status.get("state", "pre")
        if state == "in":
            status_name = status.get("shortDetail") or "Live"
        elif completed:
            status_name = "Final"

        date_text = event.get("date", "")
        title = f"{away_abbr} {away_score} - {home_abbr} {home_score} | {status_name}"
        description = (
            f"{away_team} {away_score} at {home_team} {home_score}. "
            f"Status: {status_name}. "
            f"Game: {event.get('name', '')}"
        )

        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "description").text = description
        ET.SubElement(item, "link").text = (
            f"https://www.espn.com/nba/game/_/gameId/{event.get('id', '')}"
        )
        # Score/status in GUID ensures RSS readers can see meaningful score updates.
        ET.SubElement(item, "guid", isPermaLink="false").text = (
            f"{event.get('id', 'game')}-{state}-{away_score}-{home_score}-{status_name}"
        )
        if date_text:
            try:
                dt = datetime.fromisoformat(date_text.replace("Z", "+00:00"))
                ET.SubElement(item, "pubDate").text = format_datetime(dt)
            except ValueError:
                pass

    os.makedirs(OUT_DIR, exist_ok=True)
    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")
    tree.write(OUT_FILE, encoding="utf-8", xml_declaration=True)
    print(f"Wrote {OUT_FILE} with {len(events)} scoreboard events.")

if __name__ == "__main__":
    main()
