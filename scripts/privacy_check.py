#!/usr/bin/env python3
"""Fail if files look like they contain personal data. Standard library only.

Usage:
    python3 scripts/privacy_check.py          # check files staged for commit
    python3 scripts/privacy_check.py --all    # check every tracked file

Checks: email addresses, UK mobile numbers, date-of-birth wording, credentials,
and (optionally) full names listed in a local, git-ignored file called
.privacy-names.txt (one name per line). Keep that file out of the repo.
"""
import re
import subprocess
import sys
from pathlib import Path

EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
ALLOWED_EMAIL_SUFFIX = "@users.noreply.github.com"
PHONE = re.compile(r"(?<!\d)(?:\+?44\s?|0)7\d{3}\s?\d{3}\s?\d{3}(?!\d)")
DOB = re.compile(r"\b(?:dob|d\.o\.b\.?|date of birth|born on)\b", re.IGNORECASE)
SECRET = re.compile(
    r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"\b(?:password|passwd|pwd|secret|api[_-]?key|token)\s*[:=]\s*\S+)",
    re.IGNORECASE,
)

# Files that describe the rules (and so contain the trigger words) or test them.
SKIP = {"scripts/privacy_check.py", "CLAUDE.md", "CONTRIBUTING.md"}
SKIP_PREFIXES = ("tests/",)
NAMES_FILE = Path(".privacy-names.txt")


def git_files(all_files):
    cmd = ["git", "ls-files"] if all_files else [
        "git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    return [line for line in out.splitlines() if line]


def load_names():
    if not NAMES_FILE.exists():
        return []
    names = [n.strip() for n in NAMES_FILE.read_text(encoding="utf-8").splitlines()]
    return [re.compile(r"\b" + re.escape(n) + r"\b", re.IGNORECASE) for n in names if n]


def check_text(path, text, names):
    findings = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for m in EMAIL.finditer(line):
            if not m.group(0).lower().endswith(ALLOWED_EMAIL_SUFFIX):
                findings.append((path, lineno, "email address"))
        if PHONE.search(line):
            findings.append((path, lineno, "phone number"))
        if DOB.search(line):
            findings.append((path, lineno, "date-of-birth wording"))
        if SECRET.search(line):
            findings.append((path, lineno, "possible credential"))
        for rx in names:
            if rx.search(line):
                findings.append((path, lineno, "full name from .privacy-names.txt"))
    return findings


def main(argv):
    all_files = "--all" in argv
    names = load_names()
    findings = []
    for path in git_files(all_files):
        if path in SKIP or path.startswith(SKIP_PREFIXES):
            continue
        try:
            text = Path(path).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        findings += check_text(path, text, names)
    if findings:
        print("Privacy check FAILED. Fix these before committing:", file=sys.stderr)
        for path, lineno, why in findings:
            print(f"  {path}:{lineno}: {why}", file=sys.stderr)
        return 1
    print("Privacy check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
