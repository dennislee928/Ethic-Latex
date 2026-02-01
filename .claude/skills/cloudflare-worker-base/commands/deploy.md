# Deploy

Commit, push, and deploy Cloudflare Worker in one automated workflow.

---

## Your Task

Execute the full deploy pipeline for a Cloudflare Workers project. Run all steps automatically and report results at the end.

---

## Phase 1: Pre-flight Checks

**1a. Verify this is a Cloudflare project**

```bash
ls wrangler.jsonc wrangler.toml wrangler.json 2>/dev/null | head -1
```

If no wrangler config found:
```
❌ Not a Cloudflare Workers project (no wrangler.jsonc/toml/json found)
```
Stop here.

**1b. Check for changes**

```bash
git status --porcelain
```

If no output (nothing to commit), skip to Phase 3 (deploy only).

**1c. Build**

```bash
npm run build
```

If build fails, stop and report the error.

**1d. TypeScript check (if applicable)**

Only if `tsconfig.json` exists:

```bash
npx tsc --noEmit
```

If TypeScript check fails, stop and report the error.

---

## Phase 2: Commit & Push

**2a. Stage all changes**

```bash
git add -A
```

**2b. Generate commit message**

Analyze the changes with `git diff --cached --stat` and generate an appropriate conventional commit message:

- `feat:` for new features
- `fix:` for bug fixes
- `refactor:` for code changes that don't add features or fix bugs
- `docs:` for documentation
- `chore:` for maintenance tasks

**2c. Commit**

```bash
git commit -m "$(cat <<'EOF'
[generated message]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

**2d. Push**

```bash
git push
```

If no remote configured, report error and stop.

---

## Phase 3: Deploy

```bash
npx wrangler deploy
```

Capture the output, especially the Worker URL.

---

## Phase 4: Report

Present a summary:

```
✅ Deploy Complete

📝 Commit: [hash] [message]
📤 Pushed to: [remote/branch]
🚀 Deployed: https://[worker-name].[account].workers.dev

[Any warnings from wrangler output]
```

If any phase failed:

```
❌ Deploy Failed

Phase: [which phase]
Error: [error message]

[Suggestions for fixing]
```

---

## Edge Cases

- **No changes to commit**: Skip Phase 2, just deploy
- **Build script missing**: Skip build step, warn user
- **No remote**: Report error, suggest `git remote add origin <url>`
- **Wrangler not installed**: Report error, suggest `npm install -D wrangler`
