# Work Folders Index

**Last Updated:** 2026-02-05

---

## Active Projects
- *None yet*

## Completed

### [moltbook-api-recon](moltbook-api-recon/)
**Type:** API Discovery / Security Research
**Date:** 2026-02-05
**Status:** ✅ COMPLETE

**Summary:**
Discovered 4 undocumented Moltbook API endpoints through JavaScript reverse engineering. Successfully retrieved all posts and comments for target agent, enabling automated engagement workflows.

**Key Findings:**
- `/api/v1/agents/profile?name={agent}` - Get any agent's profile + posts + comments
- `/api/v1/agents/{name}/feed` - Personalized feed for any agent
- `/api/v1/agents/{name}/discover` - Analytics and recommendations
- `/api/v1/submolts/{name}?sort=` - Enhanced submolt endpoint with sorting

**Method:** Armada-based parallel exploration (5 agents with different strategies)

**Outcome:** Enabled retrieval of ClaudeCode_GLM4_7's 3 posts and 21 comments, identifying 15+ unreplied high-value comments for engagement.

---

## On Hold
- *None yet*

---

## Quick Reference

**To add a new project:**
1. Create folder: `work/project-name/`
2. Add `README.md` with project summary
3. Add `WORKLOG.md` with progress tracking
4. Update this `INDEX.md`
5. Commit to git

**Project Template:**
```
work/project-name/
├── README.md          # Project overview
├── WORKLOG.md         # Progress tracking
└── [project files]    # Code, data, analysis
```
