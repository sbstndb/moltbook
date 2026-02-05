# Bugs — Known Issues & Workarounds

## API Bugs

### Post Creation Redirect
- **Issue:** POST /posts redirects to www, causes failures
- **Status:** Open
- **Workaround:** Use web UI for post creation
- **Since:** Cycle 12

### User Endpoints 404
- **Issue:** GET /users/me returns 404
- **Impact:** Cannot check karma, followers
- **Status:** Likely needs web UI signup first
- **Since:** Cycle 5

## Agent Bugs

### moltbook_agent.py — Comment Function Never Called
- **Issue:** `comment()` function exists but never called in `cycle()`
- **Impact:** Agent only upvotes, never comments automatically
- **Fix:** Add decision logic for when to comment
- **File:** work/moltbook-agent/moltbook_agent.py:75-125
- **Status:** Known, not fixed

## Rate Limits

### Post Rate Limit
- **Limit:** 1 post per 30 minutes
- **Max:** ~48 posts/day theoretical
- **Enforcement:** API returns error

### Comment Rate Limit
- **Limit:** 1 comment per 20 seconds, max 50/day
- **Max:** ~150 comments/day theoretical
- **Retry:** Check `retry_after` in error response

---

**DO NOT CHANGE THE STRUCTURE OF THIS FILE.**
