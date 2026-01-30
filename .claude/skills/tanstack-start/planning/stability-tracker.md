# TanStack Start Stability Tracker

Track progress toward v1.0 stable release and skill publication.

## Completion Criteria

- [ ] v1.0 stable released (currently RC v1.136.9 - announced Sept 22, 2025)
- [ ] GitHub #5734 resolved (memory leak with TanStack Form)
- [ ] 2+ weeks without critical bugs after v1.0 stable
- [x] Official Cloudflare docs available (published Oct 24, 2025)
- [ ] Templates and reference documentation created

## Weekly Checks

### 2025-11-18 ✅ COMPREHENSIVE REVIEW
- **Package:** @tanstack/react-start (correct package identified)
- **Status:** RC v1.136.9 (published Nov 18, 2025 - 22:41 UTC)
- **Previous Tracking:** Was tracking wrong package (@tanstack/start v1.120.20 from June 8)
- **Blockers:**
  - #5734 OPEN (memory leak with TanStack Form, reported Nov 2, 2025)
  - Issue affects production servers (crashes every ~30 minutes)
  - Reproducible example provided by community
- **v1.0 Status:** RC announced Sept 22, 2025 - stable not yet released
- **Cloudflare Support:** ✅ Official docs published, C3 CLI support added
- **Action:** Continue monitoring #5734, check weekly for v1.0 stable announcement

### 2025-11-07
- **Status:** RC v1.120.20 (INCORRECT - was tracking wrong package)
- **Blockers:** #5734 (memory leak open, no response)
- **Action:** Continue monitoring

### Next Check: 2025-11-25

---

## Resources

- **Package:** `npm view @tanstack/react-start version`
- [Releases](https://github.com/TanStack/router/releases)
- [Issue #5734](https://github.com/TanStack/router/issues/5734) - Memory leak blocker
- [Cloudflare Docs](https://developers.cloudflare.com/workers/framework-guides/web-apps/tanstack-start/)
- [RC Announcement](https://tanstack.com/blog/announcing-tanstack-start-v1) - Sept 22, 2025

## Notes

**Package Clarification:**
- ✅ Monitor: `@tanstack/react-start` (React implementation, actively maintained)
- ❌ Ignore: `@tanstack/start` (core package, last updated June 8, 2025)
- Label "needed-for-start-stable" relates to @solidjs/start, not React Start
