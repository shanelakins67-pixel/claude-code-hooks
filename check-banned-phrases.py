#!/usr/bin/env python3
"""
Claude Code PostToolUse Hook: Banned Phrase Checker
----------------------------------------------------
Blocks Claude from finishing a file edit if it contains any banned
characters or phrases that you've defined below.

HOW IT WORKS:
  Claude Code runs this script automatically after every Write or Edit.
  If a violation is found, Claude gets a blocking error and must fix it
  before it can continue.

SETUP:
  1. Save this file somewhere on your computer (e.g. ~/.claude/hooks/)
  2. Find your Python path:
       Mac/Linux:  run "which python3" in Terminal
       Windows:    run "where python" in Command Prompt
  3. Add the hook to your Claude Code settings:
       Open: ~/.claude/settings.json
       Add the block shown in settings-snippet.json (included with this file)
  4. Restart Claude Code for the hook to take effect.

CUSTOMIZE:
  Edit the BANNED list below to match your own rules.
  Each entry is a plain text string. Claude cannot save a file containing any of them.
"""

import sys
import json

# -----------------------------------------------------------------------
# EDIT THIS LIST to match your rules.
# Add any character, word, or phrase you never want Claude to write.
# -----------------------------------------------------------------------
BANNED = [
    "—",   # em-dash  (—)
    "–",   # en-dash  (–)
    # Add more below, one per line, in quotes, separated by commas:
    # "synergy",
    # "leverage",
    # "game-changer",
]

# File types to check. Files with other extensions are skipped.
CHECK_EXTENSIONS = {".html", ".js", ".css", ".md", ".txt", ".json"}

# Maximum number of violation lines shown in the error message.
MAX_LINES_SHOWN = 10
# -----------------------------------------------------------------------


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    ext = ("." + file_path.rsplit(".", 1)[-1].lower()) if "." in file_path else ""
    if ext not in CHECK_EXTENSIONS:
        sys.exit(0)

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        sys.exit(0)

    violations = []
    for i, line in enumerate(lines):
        for banned in BANNED:
            if banned in line:
                violations.append((i + 1, line.rstrip()))
                break

    if not violations:
        sys.exit(0)

    message_lines = [
        f"RULE VIOLATION in {file_path}. Fix before continuing.",
    ]
    for line_num, line_text in violations[:MAX_LINES_SHOWN]:
        message_lines.append(f"  Line {line_num}: {line_text[:120]}")
    if len(violations) > MAX_LINES_SHOWN:
        message_lines.append(f"  ...and {len(violations) - MAX_LINES_SHOWN} more.")
    message_lines.append("Fix the violations above, then continue.")

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "\n".join(message_lines)
        }
    }))
    sys.exit(2)


if __name__ == "__main__":
    main()
