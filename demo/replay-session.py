"""Replays a real captured gcontext session in Claude Code terminal style.

Unlike claude-sim.py (which invents its output), this script renders the
REAL transcripts captured in first-session.json: every word shown comes
from the recorded session. Long stretches are condensed for pacing (tool
calls collapsed to one dim line each, long assistant texts truncated to
verbatim sentences), but nothing is invented or paraphrased.

Two modes:
  create  - transcript 0: the agent creates the supabase integration module
  query   - transcript 1: a fresh session answers "how many users" with 14

Used by gcontext-real-demo.tape via a `claude()` bash function alias.
Run: uv run python replay-session.py <create|query>
"""

import json
import re
import sys
import textwrap
import time
from pathlib import Path

SESSION_FILE = Path(__file__).resolve().parent / "first-session.json"

RESET = "\x1b[0m"
CYAN_BOLD = "\x1b[1;36m"
DIM = "\x1b[90m"
BOLD = "\x1b[1m"
GREEN_BOLD = "\x1b[1;32m"
ELLIPSIS = "…"

WRAP_WIDTH = 76

# Per-mode display plan. "tools" is an ordered allowlist of (verb, substring)
# pairs matched against the condensed tool line; only matching tool calls are
# shown (the rest are collapsed away for pacing). "assistant_keep" maps the
# Nth assistant entry to the verbatim sentences kept from its full text.
MODES = {
    "create": {
        "transcript": 0,
        # The captured prompt ends with a sandbox-only instruction (the test
        # workspace has no CLI installed). Strip it: a real user stops here.
        "strip_prompt_from": "The gcontext CLI is not installed",
        "prompt_delay": 0.006,
        "tools": [
            ("Read", "context/structure.md"),
            ("Read", "context/principles.md"),
            ("Write", "modules-repo/supabase/module.yaml"),
            ("Write", "modules-repo/supabase/llms.txt"),
            ("Write", "modules-repo/supabase/info.md"),
            ("Bash", "ln -s"),
            ("Edit", "context/llms.txt"),
            ("Edit", "context/system.md"),
        ],
        "assistant_keep": {
            1: [
                "The supabase integration module is created and loaded"
                " into the workspace.",
                "No secret values appear anywhere in the module: I verified"
                " the files reference only the variable names.",
            ],
        },
    },
    "query": {
        "transcript": 1,
        "strip_prompt_from": None,
        "prompt_delay": 0.020,
        "tools": [
            ("Read", "context/system.md"),
            ("Read", "modules-repo/supabase/info.md"),
            ("Read", "modules-repo/supabase/module.yaml"),
            ("Read", "context/secrets.md"),
            ("Bash", "curl"),
        ],
        "assistant_keep": {},
        # The last assistant turn is the answer itself: style it.
        "highlight_final": True,
    },
}

VERBS = {"Read": "Reading", "Write": "Write", "Edit": "Edit"}


def typewrite(text, delay=0.016):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def wrap(text):
    return textwrap.wrap(" ".join(text.split()), width=WRAP_WIDTH)


def workspace_prefix(entries):
    """Find the captured test-workspace path prefix so it can be stripped."""
    for e in entries:
        if e["kind"] != "tool":
            continue
        try:
            args = json.loads(e["text"])
        except (json.JSONDecodeError, TypeError):
            continue
        path = args.get("file_path", "")
        marker = "workspace/"
        if marker in path:
            return path[: path.index(marker) + len(marker)]
    return None


def shorten(text, prefix):
    if prefix:
        text = text.replace(prefix, "")
        text = text.replace(prefix.rstrip("/"), ".")
    return text


def condense_tool(entry, prefix):
    """One dim line from a real tool call: verb + primary argument."""
    label = entry.get("label", "")
    # Captured labels look like "tool call <dash> Read"; keep the tool name.
    dash = "\u2014"
    name = label.split(dash)[-1].strip() if dash in label else label
    try:
        args = json.loads(entry["text"])
    except (json.JSONDecodeError, TypeError):
        # Long tool args are truncated in the capture; recover the primary
        # argument with a regex over the raw (still real) text.
        args = {}
        for key in ("file_path", "command", "pattern", "url"):
            m = re.search(rf'"{key}"\s*:\s*"((?:[^"\\]|\\.)*)"', entry["text"])
            if m:
                args[key] = m.group(1).encode().decode("unicode_escape")
                break
    primary = (
        args.get("file_path")
        or args.get("command")
        or args.get("pattern")
        or args.get("url")
        or ""
    )
    primary = shorten(primary, prefix)
    if name == "Bash":
        snippet = primary
        if "curl" in snippet:
            snippet = snippet[snippet.index("curl"):]
        for cut in (" -H ", " && ", " | "):
            if cut in snippet:
                snippet = snippet[: snippet.index(cut)]
        snippet = snippet.strip()
        if len(snippet) > 64:
            snippet = snippet[:64].rstrip()
        return name, snippet
    verb = VERBS.get(name, name)
    return name, f"{verb} {primary}".strip() if primary else verb


def show_prompt(text, mode_cfg):
    cut = mode_cfg["strip_prompt_from"]
    if cut and cut in text:
        text = text[: text.index(cut)].rstrip()
    lines = wrap(text)
    delay = mode_cfg["prompt_delay"]
    typewrite(f"{CYAN_BOLD}>{RESET} {lines[0]}", delay)
    for line in lines[1:]:
        typewrite(f"  {line}", delay)
    print()
    time.sleep(0.7)


def show_assistant(text, keep_sentences, highlight=False):
    if highlight:
        time.sleep(0.9)
        typewrite(f"  {GREEN_BOLD}{text.strip()}{RESET}", 0.15)
        print()
        return
    if keep_sentences:
        for sentence in keep_sentences:
            if sentence not in text:
                raise SystemExit(
                    f"replay integrity error: sentence not in transcript: "
                    f"{sentence!r}"
                )
        text = " ".join(keep_sentences)
    for line in wrap(text):
        typewrite(f"  {line}", 0.014)
    print()
    time.sleep(0.4)


def replay(mode):
    cfg = MODES[mode]
    record = json.loads(SESSION_FILE.read_text())["record"]
    entries = record["transcripts"][cfg["transcript"]]["entries"]
    prefix = workspace_prefix(entries)

    wanted = list(cfg["tools"])
    assistant_seen = 0
    n_assistant = sum(1 for e in entries if e["kind"] == "assistant")
    shown_tool = False

    print()
    for entry in entries:
        kind = entry["kind"]
        if kind == "prompt":
            show_prompt(entry["text"], cfg)
        elif kind == "assistant":
            if shown_tool:
                print()
                shown_tool = False
            is_final = assistant_seen == n_assistant - 1
            highlight = cfg.get("highlight_final") and is_final
            keep = cfg["assistant_keep"].get(assistant_seen)
            show_assistant(entry["text"], keep, highlight)
            assistant_seen += 1
        elif kind == "tool":
            name, line = condense_tool(entry, prefix)
            for i, (verb, substr) in enumerate(wanted):
                if verb == name and substr in line:
                    typewrite(f"  {DIM}{line} {ELLIPSIS}{RESET}", 0.009)
                    time.sleep(0.20)
                    wanted.pop(i)
                    shown_tool = True
                    break
        # tool_result and meta entries are skipped entirely


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "create"
    if mode not in MODES:
        raise SystemExit(f"usage: replay-session.py <{'|'.join(MODES)}>")
    replay(mode)
