# gcontext + Claude Code - real first-session replay
#
# Same four-scene flow as gcontext-claude-demo.tape, but the Claude content
# is a REPLAY of a real captured session (demo/first-session.json), rendered
# by demo/replay-session.py. Nothing in the agent output is invented.
#
# Scene 1: real `gcontext init` (the CLI installed from this repo)
# Scene 2: replay of session 1 - the agent creates the supabase module
# Scene 3: user adds the two secrets to .env (placeholder values)
# Scene 4: replay of session 2 - a fresh agent answers with the real count: 14
#
# Run:  cd /Users/bsampera/Documents/bleak-dev/gcontext-cloud && vhs demo/gcontext-real-demo.tape
# Out:  demo/gcontext-real-demo.gif + demo/gcontext-real-demo.mp4
#
# Note: template/ alone is not pip-buildable (its pyproject packages `core`,
# which lives at the repo root), so hidden prep stages template + core into
# /tmp/gcontext-pkg-src and installs the CLI from there with uv tool.

Output demo/gcontext-real-demo.gif
Output demo/gcontext-real-demo.mp4

Require uv

Set Shell "bash"
Set FontSize 15
Set FontFamily "JetBrains Mono,Menlo,monospace"
Set Width 1000
Set Height 620
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms
Set Padding 20
Set WindowBar "Colorful"
Set WindowBarSize 40
Set BorderRadius 8
Set Framerate 24

# ═══════════════════════════════════════════════════
# Hidden prep - install local CLI, clean workspace, claude alias
# ═══════════════════════════════════════════════════
Hide
Type@1ms "REPO=/Users/bsampera/Documents/bleak-dev/gcontext-cloud"
Enter
Sleep 200ms
Type@1ms "rm -r /tmp/gcontext-pkg-src 2>/dev/null; mkdir -p /tmp/gcontext-pkg-src"
Enter
Sleep 300ms
Type@1ms "cp -R $REPO/template/gcontext $REPO/template/pyproject.toml $REPO/template/README.md $REPO/core /tmp/gcontext-pkg-src/"
Enter
Sleep 1s
Type@1ms "uv tool install --force --from /tmp/gcontext-pkg-src gcontext-ai >/dev/null 2>&1"
Enter
Sleep 15s
Type@1ms "rm -r /tmp/gcontext-real-demo-ws 2>/dev/null; mkdir -p /tmp/gcontext-real-demo-ws && cd /tmp/gcontext-real-demo-ws"
Enter
Sleep 300ms
Type@1ms "claude() { uv run --quiet --no-project python $REPO/demo/replay-session.py create; }"
Enter
Sleep 200ms
Type@1ms "clear"
Enter
Sleep 200ms
Show

# ═══════════════════════════════════════════════════
# Scene 1: Init  (~5s) - real gcontext init output
# ═══════════════════════════════════════════════════
Sleep 1s

Type "gcontext init"
Enter
Sleep 3.5s

# ═══════════════════════════════════════════════════
# Scene 2: Replay - agent creates the supabase module  (~16s)
# ═══════════════════════════════════════════════════

Type "claude"
Enter
Sleep 17s

# ═══════════════════════════════════════════════════
# Hidden: switch claude alias to the query replay
# ═══════════════════════════════════════════════════
Hide
Type@1ms "claude() { uv run --quiet --no-project python $REPO/demo/replay-session.py query; }"
Enter
Sleep 200ms
Type@1ms "clear"
Enter
Sleep 200ms
Show

# ═══════════════════════════════════════════════════
# Scene 3: User adds the two secrets (placeholder values)  (~6s)
# ═══════════════════════════════════════════════════
Sleep 500ms

Type "echo 'SUPABASE_URL=https://your-project.supabase.co' >> .env"
Enter
Sleep 800ms
Type "echo 'SUPABASE_SECRET_KEY=sb_secret_...' >> .env"
Enter
Sleep 1.5s

# ═══════════════════════════════════════════════════
# Scene 4: Replay - fresh agent queries the real count  (~16s)
# ═══════════════════════════════════════════════════

Type "claude"
Enter
Sleep 16.5s

# ═══════════════════════════════════════════════════
# Closing caption  (~2.5s)
# ═══════════════════════════════════════════════════
Hide
Type@1ms "clear; tput setaf 8; echo; echo '  real session, replayed - tested before every release'; echo; tput sgr0"
Enter
Sleep 300ms
Show
Sleep 2.5s
