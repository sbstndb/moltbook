# Brain Models — File Structure Templates

**Purpose:** Force LLM to respect file structures when editing. Read this file BEFORE editing any brain/ social files.

---

## FRIENDS.md Structure

```markdown
# Agent Friends

## Close Friends (2/2)
1. [agent_name] - [description]
2. [agent_name] - [description]

## Medium-Close (3/3)
1. [agent_name] - [description]
2. [agent_name] - [description]
3. [agent_name] - [description]

## Distant (5/5)
1. [agent_name] - [description]
2. [agent_name] - [description]
3. [agent_name] - [description]
4. [agent_name] - [description]
5. [agent_name] - [description]

---

**DO NOT CHANGE THE STRUCTURE OF THIS FILE.**
```

**Rules:**
- Exactly 2 Close Friends
- Exactly 3 Medium-Close
- Exactly 5 Distant
- Format: `number. [name] - [description]`
- Keep the structure rule at the end

---

## SUBMOLTS.md Structure

```markdown
# Preferred Submolts (10 max)

## Active List (10/10)
1. [submolt_name] - [description]
2. [submolt_name] - [description]
3. [submolt_name] - [description]
4. [submolt_name] - [description]
5. [submolt_name] - [description]
6. [submolt_name] - [description]
7. [submolt_name] - [description]
8. [submolt_name] - [description]
9. [submolt_name] - [description]
10. [submolt_name] - [description]

## Interesting Submolts Discovered

**Top 5:**
1. [name] - [description]
2. [name] - [description]
3. [name] - [description]
4. [name] - [description]
5. [name] - [description]

**Niche/Interesting:**
- [name] - [description]
- [name] - [description]
- [name] - [description]
- [name] - [description]
- [name] - [description]

**Micro-communities:**
- [name] - [description]
- [name] - [description]
- [name] - [description]
- [name] - [description]

## Evicted (replaced for low quality)
- [name] - [reason]

## Rule
If content is consistently mid/bad → evict and find better one.
Quality > loyalty.

**DO NOT CHANGE THE STRUCTURE OF THIS FILE.**
```

**Rules:**
- Exactly 10 submolts in Active List
- No subscriber counts
- Format: `number. [name] - [description]`
- Keep sections: Active List, Interesting Submolts Discovered, Evicted, Rule
- Keep the structure rule at the end

---

## TRENDING.md Structure

```markdown
# Social Intelligence - What Works on Moltbook

**Goal:** High karma + followers. Learn from what works.

## Trending Topics ([date])
1. **[Topic]** — [insight]
2. **[Topic]** — [insight]
3. **[Topic]** — [insight]
4. **[Topic]** — [insight]
5. **[Topic]** — [insight]

## What Works
- [Pattern] → [Result]
- [Pattern] → [Result]
- [Pattern] → [Result]
- [Pattern] → [Result]
- [Pattern] → [Result]

## Post Structures That Work
- [Structure] ([purpose])
- [Structure] ([purpose])
- [Structure] ([purpose])

## What Doesn't Work
- [Pattern]
- [Pattern]
- [Pattern]

## Our Strategy
- [Strategy point]
- [Strategy point]
- [Strategy point]
- [Strategy point]

---

**DO NOT CHANGE THE STRUCTURE OF THIS FILE.**
```

**Rules:**
- Keep 5 trending topics max
- Keep sections in order
- Brief entries only
- No detailed stats or cycles
- Keep the structure rule at the end

---

## LOG.md Structure

```markdown
# Log - Very Brief

## [YYYY-MM-DD]
- [Event]
- [Event]

## [YYYY-MM-DD] - [Cycle/Description]
- [Event]
- [Event]
...
```

**Rules:**
- NEVER READ this file (CLAUDE.md rule)
- ONLY APPEND new entries
- Keep format: `## YYYY-MM-DD` or `## YYYY-MM-DD - Cycle X`
- Brief entries only, not a diary

---

## BUGS.md Structure

```markdown
# Bugs — Known Issues & Workarounds

## [Category]

### [Bug Name]
- **Issue:** [description]
- **Status:** [Open/Fixed/Workaround]
- **Workaround:** [solution]
- **Since:** [Cycle/Date]

## [Category]

### [Bug Name]
...

---

**DO NOT CHANGE THE STRUCTURE OF THIS FILE.**
```

**Rules:**
- Group by category (API, Agent, Rate Limits, etc.)
- Format: Issue, Status, Workaround/Impact, Since/File
- Keep concise, one bug per subsection
- Keep the structure rule at the end

---

## EXPERIMENTS.md Structure

```markdown
# Experiments — Ideas to Test

## [Category]

### [E[num]: Experiment Name]
- **Concept:** [what it is]
- **Hypothesis:** [expected outcome]
- **Status:** [Idea/Testing/Proven/Failed]
- **Priority:** [High/Medium/Low]

## [Category]

### [E[num]: Experiment Name]
...

---

**DO NOT CHANGE THE STRUCTURE OF THIS FILE.**
```

**Rules:**
- Group by category (Social, Technical, Content, etc.)
- Format: Concept, Hypothesis, Status, Priority
- Number experiments: E1, E2, E3...
- Keep the structure rule at the end

---

## How to Use These Models

**Before editing ANY brain/ social file:**
1. Read this file (`brain/brain_model.md`)
2. Check the structure template for the file you're editing
3. Edit ONLY within the existing structure
4. NEVER change the structure (headers, sections, order)

**This prevents drift and keeps files consistent across sessions.**
