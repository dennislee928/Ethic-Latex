# Update Documentation

Audit and maintain documentation files in the current project. Checks for stale content, outdated references, redundancy, and suggests improvements.

## Command Usage

`/docs/update [scope]`

**Scope options:**
- `all` (default) - Full audit of all documentation
- `quick` - Check dates and versions only
- `archive` - Focus on archiving old content

## Process

### 1. Discover Documentation Files

Scan for documentation in priority order:

```
Priority 1 (Core):
- CLAUDE.md (project instructions)
- README.md (public-facing)
- SESSION.md (session state)

Priority 2 (Project docs):
- docs/*.md (architecture, API, database, etc.)
- CHANGELOG.md, CONTRIBUTING.md, LICENSE

Priority 3 (Root files):
- *.md in project root
- *.txt in project root

Priority 4 (Planning/working):
- planning/*.md
- archive/*.md (check if should be deleted)
```

### 2. Check Currency

For each documentation file, check:

**Date Freshness:**
- Find "Last Updated", "Updated:", "Date:" patterns
- Compare against `git log -1 --format="%ci" <file>`
- Flag if doc date is >30 days older than last git change

**Version References:**
- Extract package versions mentioned (e.g., `hono@4.10.1`, `v4.1.14`)
- For npm packages: compare against `npm view <pkg> version`
- Flag outdated versions with suggested updates

**Broken Links:**
- Check internal markdown links `[text](./path/to/file.md)`
- Verify referenced files exist
- Flag broken links with suggestions

### 3. Detect Issues

**Redundancy:**
- Identify similar content across files (>50% overlap)
- Suggest consolidation or cross-references

**Staleness Indicators:**
- TODO/FIXME comments still present
- References to "upcoming", "soon", "planned" from old dates
- Completed phases still marked as "in progress"

**Organization & Maintainability:**
- Look for structural issues, not arbitrary line counts
- Well-organized large files are better than cramped small ones

Warning signs to flag:
- No table of contents or clear section headers in long files
- Outdated sections mixed with current content
- Redundant information repeated across sections
- Wall-of-text blocks without structure
- Completed phases in SESSION.md not compressed to summaries
- Reference material in CLAUDE.md that's rarely needed in-context (move to docs/)

Healthy patterns (don't flag these):
- CLAUDE.md with clear navigation, organized sections, even if 800+ lines
- SESSION.md with detailed current phase + compressed completed phases
- Large files that are actively maintained and well-structured

**Orphaned Files:**
- Files in docs/ not referenced anywhere
- Archive files that may be safe to delete

### 4. Check CLAUDE.md Against Project State

**Enhanced from original update-docs:**

Additional checks specific to CLAUDE.md:
- Does tech stack section match package.json dependencies?
- Are referenced file paths still valid?
- Are environment variables listed that don't exist in .env.example?
- Are scripts mentioned that don't exist in package.json?

### 5. Generate Report

Present findings organized by severity:

```markdown
## Documentation Audit Report

### Critical (Action Required)
- [ ] CLAUDE.md: "Last Updated" says 2024-09-15, last git change 2025-12-01
- [ ] README.md: References `hono@3.5.1`, current is `4.10.1`
- [ ] Broken link: docs/API.md references `./auth.md` (file missing)

### Warnings
- [ ] SESSION.md: Completed phases not compressed (5 detailed phases could be summaries)
- [ ] docs/old-architecture.md: Not referenced anywhere (orphaned?)
- [ ] CHANGELOG.md: No entry for recent commits

### Suggestions
- [ ] planning/research-log.md: Contains 3 TODO items
- [ ] docs/DATABASE.md and docs/SCHEMA.md have 60% overlap

### CLAUDE.md Sync Issues
- [ ] package.json has `drizzle-orm` but CLAUDE.md doesn't mention it
- [ ] CLAUDE.md references `src/lib/auth.ts` but file is at `src/auth/index.ts`
```

### 6. Interactive Fixes

For each category, offer to fix:

**Auto-fixable (proceed without asking):**
- Update "Last Updated" dates to today
- Update package version references (after verification)
- Fix simple broken links (if target is obvious)

**Requires Confirmation:**
- Archive old content to `archive/` directory
- Consolidate redundant files
- Compress SESSION.md completed phases

**Requires Explicit Approval (ask before each):**
- Delete orphaned files
- Remove archive/ files permanently
- Major restructuring

### 7. Archive Workflow

When archiving content:

```bash
# Create archive directory if needed
mkdir -p archive/docs

# Move with date prefix
mv docs/old-file.md archive/docs/2025-12-old-file.md

# Or for session logs
mv SESSION.md archive/session-logs/2025-12-02-session.md
```

**SESSION.md Compression:**

Transform completed phases from:
```markdown
## Phase 3: Auth API
**Started**: 2025-11-01
**Completed**: 2025-11-05

### Tasks
- [x] JWT verification
- [x] Session middleware
- [x] Login endpoint
- [x] Logout endpoint

### Notes
Detailed implementation notes...
```

To:
```markdown
## Phase 3: Auth API ✅
**Completed**: 2025-11-05 | **Checkpoint**: abc1234
**Summary**: JWT + session middleware + login/logout endpoints
```

## Output

After completing audit:

```markdown
## Documentation Update Complete

**Files Audited**: 12
**Issues Found**: 7
**Auto-Fixed**: 4
**Archived**: 2
**Skipped**: 1 (user declined)

### Changes Made:
- Updated "Last Updated" in CLAUDE.md, README.md
- Updated package versions in docs/SETUP.md
- Archived planning/old-research.md → archive/planning/
- Compressed 3 completed phases in SESSION.md

### Remaining Issues:
- [ ] docs/API.md: Broken link to auth.md (needs manual fix)
- [ ] Consider deleting: archive/2024-notes.md (365 days old)

### Next Steps:
1. Review changes: `git diff`
2. Fix remaining issues manually
3. Commit: `git add -A && git commit -m "docs: Update and clean documentation"`
```

## Best Practices

**Run Regularly:**
- After completing a project phase
- Before major releases
- Monthly for active projects

**Trust But Verify:**
- Review suggested version updates (breaking changes?)
- Check archived content is truly obsolete
- Verify auto-fixes don't remove intentional content

**Project-Specific Patterns:**
- Adapt to project's doc structure (not all projects have docs/)
- Respect existing conventions (some projects use .txt)
- Skip files with "DO NOT EDIT" or similar markers

## Important Notes

- This command works on ANY project, not just claude-skills
- Destructive actions (delete/archive) always require confirmation
- Version checks require network access (npm view)
- Git history is used for date comparisons (requires git repo)
- Large projects may take time to audit fully
