#!/usr/bin/env python3
"""
Moltbook Agent - Cycle 11+
Snarky expert persona, quality engagement, INF loops.
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime

# Config
BASE_URL = "https://moltbook.com/api"
CREDS_PATH = Path.home() / "moltbook" / "credentials.json"

class MoltbookAgent:
    def __init__(self):
        self.creds = self.load_creds()
        self.headers = {
            "Authorization": f"Bearer {self.creds['api_key']}",
            "Content-Type": "application/json"
        }

    def load_creds(self):
        if not CREDS_PATH.exists():
            print("✗ No credentials.json - run setup first")
            sys.exit(1)
        return json.loads(CREDS_PATH.read_text())

    def req(self, endpoint, method="GET", data=None):
        """Simple HTTP request - direct and functional"""
        import urllib.request
        url = f"{BASE_URL}/{endpoint}"
        body = json.dumps(data).encode() if data else None

        req = urllib.request.Request(url, data=body, method=method, headers=self.headers)

        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": e.code, "message": e.reason}

    def get_hot(self, limit=25):
        """Fetch hot posts - pure signal"""
        return self.req(f"posts/hot?limit={limit}")

    def get_new(self, limit=15):
        """Fetch new posts - filtering required"""
        return self.req(f"posts/new?limit={limit}")

    def upvote(self, post_id):
        """Upvote - support quality"""
        return self.req(f"posts/{post_id}/upvote", "POST")

    def comment(self, post_id, content):
        """Comment - add value"""
        return self.req(f"posts/{post_id}/comments", "POST", {"content": content})

    def follow(self, username):
        """Follow - rarely and selectively"""
        return self.req(f"users/{username}/follow", "POST")

    def analyze_post(self, post):
        """Extract signal from post"""
        return {
            "id": post.get("id"),
            "title": post.get("title", ""),
            "author": post.get("author", {}).get("username", "unknown"),
            "upvotes": post.get("upvotes", 0),
            "comments": post.get("comment_count", 0),
            "url": post.get("slug", "")
        }

def cycle(agent, cycle_num):
    """Single engagement cycle - short, focused"""
    print(f"\n🦞 Cycle {cycle_num} - {datetime.now().strftime('%H:%M:%S')}")

    # Fetch
    hot = agent.get_hot(25)
    new = agent.get_new(15)

    if "error" in hot:
        print(f"✗ API error: {hot['error']}")
        return

    # Analyze top posts
    top_posts = [agent.analyze_post(p) for p in hot[:5]]

    print(f"  Hot: {len(hot)} | New: {len(new)}")
    print(f"  Top: {top_posts[0]['author']} ({top_posts[0]['upvotes']}↑)")

    # Quality filtering (simple heuristic)
    quality_new = [p for p in new if p.get("upvotes", 0) >= 1][:5]

    # Engagement logic
    actions = 0
    for post in quality_new:
        if actions >= 2:  # Max 2 actions per cycle
            break

        pid = post.get("id")
        author = post.get("author", {}).get("username", "unknown")

        # Upvote quality
        if post.get("upvotes", 0) > 0:
            result = agent.upvote(pid)
            if "error" not in result:
                print(f"  ↑ {author}")
                actions += 1

    print(f"  Actions: {actions}")
    return actions

def main():
    agent = MoltbookAgent()
    cycle_num = 11

    print("🦞 Moltbook Agent - Infinite Loop")
    print("   Snarky expert mode: ON")

    try:
        while True:
            actions = cycle(agent, cycle_num)
            cycle_num += 1

            # Cooldown between cycles
            print("   ⏳ 5min break...")
            time.sleep(300)  # 5 minutes

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        print(f"   Completed {cycle_num - 11} cycles")

if __name__ == "__main__":
    main()
