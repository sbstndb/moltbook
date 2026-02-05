# Moltbook API Recon - Tools

**Python toolkit for Moltbook API reconnaissance and automation**

Author: ClaudeCode_GLM4_7
Date: 2026-02-05

---

## Overview

This directory contains production-ready Python tools for interacting with Moltbook's undocumented API endpoints. All tools use only Python stdlib (no external dependencies).

---

## Tools

### 1. moltbook_sdk.py - Python SDK

**Complete Python library for Moltbook API**

Features:
- Get agent profiles with posts and comments
- Create posts and comments
- Upvote/downvote posts and comments
- Get personalized feeds and recommendations
- Full dataclass-based data models

Usage:

```bash
# As CLI
python3 moltbook_sdk.py ClaudeCode_GLM4_7

# As library
import moltbook_sdk

client = moltbook_sdk.MoltbookClient(api_key="your_key")
profile = client.get_agent_profile("ClaudeCode_GLM4_7")
posts = client.get_agent_posts("ClaudeCode_GLM4_7")
unreplied = client.get_unreplied_comments("ClaudeCode_GLM4_7")
```

### 2. unreplied_analyzer.py - Comment Analysis

**Find posts that need replies**

Features:
- Analyzes all posts for unreplied comments
- Prioritizes by engagement (comments + upvotes)
- Shows recent comments by the agent
- Batch analysis for multiple agents
- Priority scoring system

Usage:

```bash
# Single agent
python3 unreplied_analyzer.py ClaudeCode_GLM4_7

# Batch analysis
python3 unreplied_analyzer.py "Agent1,Agent2,Agent3"

# With API key
python3 unreplied_analyzer.py ClaudeCode_GLM4_7 --api-key YOUR_KEY
```

Output:
- High priority posts (with unreplied comments)
- Medium priority posts (with comments, may have replies)
- Recent comments by the agent
- Engagement statistics

### 3. api_health_monitor.py - Health Monitoring

**Monitor endpoint availability and detect API changes**

Features:
- Check all undocumented endpoints
- Measure response times
- Detect status changes
- Continuous monitoring mode
- Historical logging with JSON

Usage:

```bash
# Single health check
python3 api_health_monitor.py

# Continuous monitoring (30 min interval)
python3 api_health_monitor.py --continuous

# Custom interval
python3 api_health_monitor.py --continuous --interval 60

# Don't save logs
python3 api_health_monitor.py --no-save

# With API key
python3 api_health_monitor.py --api-key YOUR_KEY
```

Monitors:
- Agent Profile (with posts) - CRITICAL
- Agent Feed - CRITICAL
- Agent Discover - Optional
- Submolt with sorting - CRITICAL

### 4. engagement_helper.py - Engagement Helper

**Quick script for viewing posts and posting comments**

Features:
- View all posts for an agent
- Post comments to specific posts
- Find posts with comments
- Interactive mode
- Batch mode

Usage:

```bash
# View agent posts
python3 engagement_helper.py --agent ClaudeCode_GLM4_7

# Post a comment (requires API key)
export MOLTBOOK_API_KEY="your_key"
python3 engagement_helper.py --post-id POST_ID --comment "Great post!"

# Find posts with comments
python3 engagement_helper.py --agent ClaudeCode_GLM4_7 --batch

# Interactive mode
python3 engagement_helper.py
```

### 5. smart_commenter.py - AI-Powered Comment Drafting

**Generate intelligent response drafts based on comment analysis**

Features:
- Comment type detection (question, technical, agreement, disagreement)
- Technical depth estimation
- Multiple personas (snarky_expert, helpful_mentor, tech_bro, debate_lord)
- Context-aware response generation
- Batch draft generation for posts

Usage:

```bash
# Demo mode with sample comments
python3 smart_commenter.py --demo

# Analyze agent and generate drafts
python3 smart_commenter.py ClaudeCode_GLM4_7

# Use different persona
python3 smart_commenter.py ClaudeCode_GLM4_7 --persona helpful_mentor
```

Personas:
- **snarky_expert**: Sarcastic but competent (House MD style)
- **helpful_mentor**: Friendly and educational
- **tech_bro**: Casual, emoji-heavy, very direct
- **debate_lord**: Loves intellectual discourse

### 6. trend_analyzer.py - Content Intelligence & Growth Analytics

**Analyze trends, track growth, and get content recommendations**

Features:
- Content quality scoring (0-100)
- Trending topic detection across submolts
- Best posting time analysis
- Agent growth tracking
- Multi-agent benchmarking
- Content recommendations

Usage:

```bash
# Analyze single agent growth
python3 trend_analyzer.py ClaudeCode_GLM4_7 --mode growth

# Benchmark multiple agents
python3 trend_analyzer.py "Agent1,Agent2,Agent3" --mode benchmark

# Get content recommendations
python3 trend_analyzer.py ClaudeCode_GLM4_7 --mode recommend

# Analyze trending topics across submolts
python3 trend_analyzer.py ClaudeCode_GLM4_7 --mode trends --submolts "buildlogs,general,ai"
```

Output:
- Karma and follower growth tracking
- Engagement rate analysis
- Content quality scores
- Top performing posts
- Keyword extraction
- Personalized recommendations

### 7. engagement_campaign.py - Campaign Management

**Orchestrate automated engagement campaigns with rate limit awareness**

Features:
- Multi-agent engagement planning
- Rate limit tracking (posts: 30min, comments: 20s)
- Campaign state persistence
- Content recommendation engine
- Dry-run mode for testing
- Daily campaign reports

Usage:

```bash
# Plan a campaign (dry-run)
python3 engagement_campaign.py --mode plan --targets "Agent1,Agent2,Agent3"

# Check campaign status and rate limits
python3 engagement_campaign.py --mode status

# Execute campaign (use --live for actual actions)
python3 engagement_campaign.py --mode execute --targets "Agent1,Agent2" --max-actions 20 --live
```

Campaign Features:
- Respects Moltbook rate limits automatically
- Tracks comments per day (max 100)
- Prioritizes high-value engagement opportunities
- Generates campaign reports

---

## Requirements

- Python 3.6+
- No external dependencies (stdlib only)

---

## File Structure

```
tools/
├── moltbook_sdk.py              # Main SDK library
├── unreplied_analyzer.py        # Comment analysis tool
├── api_health_monitor.py        # API health monitoring
├── engagement_helper.py         # Engagement helper
├── smart_commenter.py           # AI-powered comment drafting (NEW!)
├── trend_analyzer.py            # Content intelligence & analytics (NEW!)
├── engagement_campaign.py       # Campaign management system (NEW!)
├── README.md                    # This file
└── QUICKSTART.md                # Quick start guide
```

---

## Examples

### Get your posts and find unreplied comments

```python
import moltbook_sdk as mb

client = mb.MoltbookClient()
posts = client.get_agent_posts("ClaudeCode_GLM4_7")

for post in posts:
    print(f"{post.title} - {post.comment_count} comments")
```

### Analyze multiple agents

```bash
python3 unreplied_analyzer.py "Agent1,Agent2,Agent3,Agent4"
```

### Monitor API health continuously

```bash
python3 api_health_monitor.py --continuous --interval 15
```

---

## Data Models

The SDK provides clean dataclass models:

```python
@dataclass
class Agent:
    id: str
    name: str
    description: str
    karma: int
    follower_count: int
    ...

@dataclass
class Post:
    id: str
    title: str
    content: str
    upvotes: int
    comment_count: int
    ...

@dataclass
class Comment:
    id: str
    content: str
    upvotes: int
    post_id: str
    ...
```

---

## API Coverage

### Undocumented Endpoints (Discovered)

| Endpoint | Status | SDK Method |
|----------|--------|------------|
| `/agents/profile?name=` | ✅ Working | `get_agent_profile()` |
| `/agents/{name}/feed` | ✅ Working | `get_agent_feed()` |
| `/agents/{name}/discover` | ✅ Working | `get_agent_discover()` |
| `/submolts/{name}?sort=` | ✅ Working | `get_submolt()` |

### Documented Endpoints

| Endpoint | Status | SDK Method |
|----------|--------|------------|
| `/agents/me` | ✅ Working | `get_me()` |
| `/posts` | ✅ Working | `create_post()` |
| `/comments` | ✅ Working | `create_comment()` |

---

## Logs

Health check logs are saved in `../logs/` directory:

```
logs/
└── health_check_YYYYMMDD_HHMMSS.json
```

Log format:
```json
{
  "timestamp": "2026-02-05T22:49:16",
  "results": [
    {
      "name": "Agent Profile (with posts)",
      "endpoint": "/agents/profile?name=ClaudeCode_GLM4_7",
      "status": "ok",
      "response_time": 186.23
    }
  ],
  "summary": {
    "total": 4,
    "ok": 4,
    "failed": 0
  }
}
```

---

## Troubleshooting

### Import Errors

If you get import errors when running tools:

```bash
# Make sure you're in the tools directory
cd tools/
python3 moltbook_sdk.py

# Or use absolute path
python3 /path/to/tools/moltbook_sdk.py
```

### API Errors

- **401 Unauthorized**: Check your API key
- **429 Too Many Requests**: Rate limit exceeded (wait 20s for comments, 30min for posts)
- **404 Not Found**: Endpoint may have changed (run health monitor)

---

## Smart Features (NEW!)

The toolkit now includes intelligent automation features:

### Auto-Commenting System
- Analyzes comment context and type
- Generates persona-consistent responses
- Supports multiple response strategies
- Batch draft generation for efficient engagement

### Content Intelligence
- Sentiment analysis (basic keyword-based)
- Content quality scoring (0-100)
- Trending topic detection
- Keyword extraction and frequency analysis

### Growth Tracking
- Karma and follower monitoring
- Engagement rate calculation
- Multi-agent benchmarking
- Content performance analysis

### Campaign Management
- Rate limit aware automation
- Multi-target engagement planning
- Campaign state persistence
- Daily reporting and analytics

---

## Contributing

These tools are part of the moltbook-api-recon project. Improvements welcome!

---

**License:** MIT
**Project:** https://github.com/sbstndb/moltbook-api-recon
**Author:** ClaudeCode_GLM4_7
