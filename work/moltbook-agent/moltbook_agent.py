#!/usr/bin/env python3
"""
Moltbook Agent - v2 API Migration
Snarky expert persona, quality engagement, INF loops.
API v1: https://moltbook.com/api/v1
"""

import json
import time
import sys
import urllib.request
from pathlib import Path
from datetime import datetime

# Config
BASE_URL = "https://moltbook.com/api/v1"  # FIXED: v1 API
CREDS_PATH = Path.home() / ".config" / "moltbook" / "credentials.json"

class MoltbookAgent:
    def __init__(self):
        self.creds = self.load_creds()
        self.api_key = self.creds['api_key']
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def load_creds(self):
        """Load credentials from config directory"""
        if not CREDS_PATH.exists():
            print(f"✗ No credentials at {CREDS_PATH}")
            sys.exit(1)
        return json.loads(CREDS_PATH.read_text())

    def req(self, endpoint, method="GET", data=None):
        """HTTP request with redirect handling"""
        url = f"{BASE_URL}/{endpoint}"
        body = json.dumps(data).encode() if data else None

        req = urllib.request.Request(url, data=body, method=method, headers=self.headers)

        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            # Handle 307 redirects
            if e.code == 307:
                redirect_url = e.headers.get('Location', url)
                req2 = urllib.request.Request(redirect_url, data=body, method=method, headers=self.headers)
                with urllib.request.urlopen(req2) as resp2:
                    return json.loads(resp2.read().decode())
            return {"error": e.code, "message": e.reason}
        except Exception as e:
            return {"error": str(e)}

    def get_posts(self, limit=25, offset=0):
        """Fetch posts from API v1"""
        result = self.req(f"posts?limit={limit}&offset={offset}")
        if "error" in result:
            return []
        return result.get("posts", [])

    def get_submolts(self):
        """Fetch submolts"""
        result = self.req("submolts")
        if "error" in result:
            return []
        return result.get("submolts", [])

    def upvote(self, post_id):
        """Upvote a post"""
        result = self.req(f"posts/{post_id}/upvote", "POST")
        return "error" not in result

    def comment(self, post_id, content):
        """Comment on a post (requires CAPTCHA verification)"""
        result = self.req(f"posts/{post_id}/comments", "POST", {"content": content})
        return result

    def analyze_post(self, post):
        """Extract signal from post"""
        author_data = post.get("author", {})
        author = author_data.get("username", "unknown") if isinstance(author_data, dict) else str(author_data)

        return {
            "id": post.get("id"),
            "title": post.get("title", ""),
            "author": author,
            "upvotes": post.get("upvotes", 0),
            "comments": post.get("comment_count", 0)
        }

def cycle(agent, cycle_num):
    """Single engagement cycle"""
    print(f"\n🦞 Cycle {cycle_num} - {datetime.now().strftime('%H:%M:%S')}")

    # Fetch posts
    posts = agent.get_posts(25)

    if not posts:
        print("  ✗ No posts fetched")
        return 0

    # Analyze top posts
    sorted_posts = sorted(posts, key=lambda x: x.get('upvotes', 0), reverse=True)
    top5 = [agent.analyze_post(p) for p in sorted_posts[:5]]

    print(f"  Posts: {len(posts)}")
    print(f"  Top: {top5[0]['author']} ({top5[0]['upvotes']}↑)")

    # Engagement: upvote top 3 quality posts
    actions = 0
    for post_data in top5[:3]:
        pid = post_data["id"]
        author = post_data["author"]
        upvotes = post_data["upvotes"]

        # Only upvote if not already upvoted (heuristic: check if upvotes > threshold)
        if upvotes >= 1000:
            if agent.upvote(pid):
                print(f"  ↑ {author} ({upvotes}↑)")
                actions += 1

    print(f"  Actions: {actions}")
    return actions

def main():
    agent = MoltbookAgent()
    cycle_num = 12  # Continue from Cycle 11+

    print("🦞 Moltbook Agent v2 - API v1")
    print("   Snarky expert mode: ON")
    print(f"   Endpoint: {BASE_URL}")

    try:
        while True:
            actions = cycle(agent, cycle_num)
            cycle_num += 1

            # Cooldown between cycles
            print("   ⏳ 5min break...")
            time.sleep(300)

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        print(f"   Completed {cycle_num - 12} cycles")

if __name__ == "__main__":
    main()
