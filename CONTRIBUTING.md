# Contributing

You don't need to know Git. You can add a puzzle write-up in about five minutes using only your web browser.

## Rules for everything you add

- Sign your work **first name and last initial** only, for example "Henry F.".
- No email addresses, phone numbers, dates of birth, photos of people or passwords. Not in files, not in comments.
- Link to a puzzle or article instead of copying it out in full.
- Use your own words.

## Add a puzzle write-up (5 minutes)

1. Make a free GitHub account. Choose a username that doesn't show your full name.
2. Open the `puzzles` folder in this repository and open `TEMPLATE.md`. Copy its contents.
3. Go back to the `puzzles` folder, then **Add file → Create new file**.
4. Name it `YYYY-MM-short-name.md`, for example `2026-10-birthday-problem.md`. Paste the template and fill it in.
5. Press **Commit changes**. If GitHub asks, choose **Create a new branch and start a pull request** (or **Propose changes**), then **Create pull request**.
6. The Scorekeeper will review it. If it's good, they'll merge it and add your points.

The same steps work for `pitches/`, `resources/` and `tools/`.

## How points work

Points live in `leaderboard/points.csv` and the rules in `leaderboard/rules.json`.

| Category | Points |
|---|---|
| Puzzle write-up | 3 to 5, depending on quality |
| Tournament | 10 / 7 / 5 for the top three, 2 for everyone else who plays |
| Stock pitch | 5 for presenting, plus 3 if the room votes it best |
| Research note | 3 |
| Tool or code | 5 |
| Helping others | 2 |
| Attendance | 1 per session |

- Points reward quality, not volume. Every award has a written reason.
- Nobody awards themselves points.
- At most 15 points per category per month count towards your total.

## Running the checks (optional, for people comfortable with Git)

```
git config core.hooksPath .githooks
python3 scripts/privacy_check.py --all
python3 leaderboard/build.py --check
python3 -m unittest discover -s tests
```

Set `git config user.email` to your GitHub noreply address (GitHub → Settings → Emails). The commit hook blocks any other address.
