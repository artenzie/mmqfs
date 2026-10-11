# CLAUDE.md — MMQFS public repository

Public repository of the Marlborough College Mathematics and Quantitative Finance Society (MMQFS). Members are mostly under 18. Everything here is visible to the world. A private companion repository (`mmqfs-private`) holds session logs and Wharton team work.

## Privacy rules (non-negotiable)

- Refer to members by **first name and last initial only** ("Henry F."). Never full names.
- Never commit email addresses, dates of birth, school ID numbers, phone numbers, logins or API keys, or anything from the Wharton roster.
- Never write evaluative comments about named individuals. Record decisions, tasks and owners.
- No room names, timetables beyond "Thursdays 17:00", photos of members, or Wharton strategy or trades.
- Commit only with the GitHub noreply address `295525142+artenzie@users.noreply.github.com`. The pre-commit hook blocks any other address.
- Before every commit: `python3 scripts/privacy_check.py` (staged files) or `--all`.
- Optional local safety net: a git-ignored file `.privacy-names.txt` with one full name per line makes the check fail on those names. Never commit that file.

## Conventions

- Python, standard library only. No third-party dependencies.
- After cloning: `git config core.hooksPath .githooks`.
- Tests: `python3 -m unittest discover -s tests`. Tests build their own fake data in temp files; never commit fake data.
- Leaderboard: edit only `leaderboard/points.csv`, then run `python3 leaderboard/build.py` to regenerate `leaderboard/LEADERBOARD.md`. Never edit `LEADERBOARD.md` by hand.
- Do not push without the president's approval.

## Layout

`puzzles/`, `pitches/`, `resources/`, `tools/`, `leaderboard/`, `scripts/`, `tests/`.
