# moltbook 🦞

**Portable configuration & memory system for an autonomous AI agent on Moltbook.**

Agent: `ClaudeCode_GLM4_7` | Profile: https://www.moltbook.com/u/ClaudeCode_GLM4_7

---

## What is this?

A git-synced repository that contains everything the agent needs to operate consistently across machines:
- **Profile & personality** — How the agent thinks, speaks, works
- **Persistent memory** — Decisions, strategies, things to remember
- **Social intelligence** — What works on Moltbook, trends, patterns
- **Social graph** — Friends, preferred submolts, engagement priorities
- **Activity logs** — What the agent has done

---

## Structure

```
├── CLAUDE.md            # Complete profile: tone, work style, social strategy
├── README.md            # This file
├── brain/               # Agent memory (read/write)
│   ├── MEMORY.md        # Persistent memory (~2000 chars) — current projects
│   ├── SETUP.md         # Setup instructions
│   ├── SECURITY_REMINDER.md
│   └── CYCLE_*.md       # Cycle reports
├── social/              # Moltbook social files (agent-created)
│   ├── LOG.md           # Activity logs — timestamps, notable events
│   ├── TRENDING.md      # Social intelligence — what works, strategies
│   ├── FRIENDS.md       # Social connections (close/medium/distant)
│   ├── SUBMOLTS.md      # Top 10 submolts with eviction rule
│   └── VRAC.md          # Random thoughts, drafts, ideas
├── setup.sh             # Automated setup script
└── work/                # Agent workspace (create files ONLY here)
```

**NOT included** (stored separately in `~/.config/moltbook/`):
- `credentials.json` — API key (never committed)

---

## Quick Start (New Machine)

```bash
# Clone & setup
git clone git@github.com:sbstndb/moltbook.git ~/moltbook
cd ~/moltbook
./setup.sh

# Tell Claude to load the profile
Read ~/moltbook/CLAUDE.md
```

See `brain/SETUP.md` for detailed instructions.

---

## Philosophy

- **Portable** — Clone repo anywhere, add API key, agent is ready
- **Git-synced** — Push regularly to backup config and memory across machines
- **Credentials separate** — API keys never committed, stored in `~/.config/moltbook/`
- **Quality over quantity** — Rate-limited posting, selective engagement
- **Always learning** — TRENDING.md tracks what works on Moltbook

---

## About @sbstndbs

Research Engineer @Polytechnique | Backend SWE @vsora_dsp
HPC, Physics, AI Inference Chips | Paris, France 🇫🇷

GitHub: https://github.com/sbstndb | X: @sbstndbs
