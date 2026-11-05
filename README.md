# NBA Scores RSS 2.0

A small GitHub Actions project that fetches ESPN's public NBA scoreboard endpoint
and publishes a standards-based RSS 2.0 feed containing NBA game scores.

## Setup

1. Create a **public** GitHub repository, for example `nba-scores-rss`.
2. Upload the contents of this folder to the repository's `main` branch.
3. Open **Settings → Pages**. Under **Build and deployment**, choose **GitHub Actions**.
4. Open **Actions**, enable workflows if prompted, then run **Update NBA Scores RSS** once using **Run workflow**.
5. After the workflow succeeds, the feed will be available at:

   `https://YOUR-GITHUB-USERNAME.github.io/nba-scores-rss/nba-scores.xml`

6. Paste that URL into MemoMind Glass.

The workflow also runs every five minutes. GitHub scheduled workflows use UTC and
may be delayed during busy periods; five minutes is the shortest supported schedule
interval. The feed contains live, final, and scheduled games returned by the
scoreboard endpoint for the current NBA scoreboard date.

## Notes

- No API key or GitHub secret is required.
- The repository must be public for free GitHub Pages on GitHub Free.
- This uses ESPN's publicly accessible scoreboard endpoint; it is not an official
  NBA RSS service, and ESPN may change the endpoint or response format.
