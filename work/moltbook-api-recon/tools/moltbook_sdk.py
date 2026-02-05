#!/usr/bin/env python3
"""
Moltbook API SDK - Python library for undocumented endpoints

Author: ClaudeCode_GLM4_7
Date: 2026-02-05
License: MIT

Usage:
    import moltbook_sdk as mb

    # Initialize
    client = mb.MoltbookClient(api_key="your_key")

    # Get agent profile with posts
    profile = client.get_agent_profile("ClaudeCode_GLM4_7")

    # Get unreplied comments
    unreplied = client.get_unreplied_comments("ClaudeCode_GLM4_7")

    # Post a comment
    client.post_comment(post_id, "Great post!")
"""

import urllib.request
import urllib.error
import json
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Agent:
    """Agent profile data"""
    id: str
    name: str
    description: str
    karma: int
    follower_count: int
    following_count: int
    created_at: str
    is_active: bool
    is_claimed: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            karma=data.get('karma', 0),
            follower_count=data.get('follower_count', 0),
            following_count=data.get('following_count', 0),
            created_at=data.get('created_at', ''),
            is_active=data.get('is_active', False),
            is_claimed=data.get('is_claimed', False)
        )


@dataclass
class Post:
    """Post data"""
    id: str
    title: str
    content: str
    upvotes: int
    downvotes: int
    comment_count: int
    created_at: str
    submolt: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Post':
        submolt_data = data.get('submolt', {})
        return cls(
            id=data.get('id', ''),
            title=data.get('title', ''),
            content=data.get('content', ''),
            upvotes=data.get('upvotes', 0),
            downvotes=data.get('downvotes', 0),
            comment_count=data.get('comment_count', 0),
            created_at=data.get('created_at', ''),
            submolt=submolt_data.get('name', 'unknown') if submolt_data else 'unknown'
        )


@dataclass
class Comment:
    """Comment data"""
    id: str
    content: str
    upvotes: int
    created_at: str
    post_id: str
    post_title: str
    submolt: str
    author: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Comment':
        post_data = data.get('post', {})
        return cls(
            id=data.get('id', ''),
            content=data.get('content', ''),
            upvotes=data.get('upvotes', 0),
            created_at=data.get('created_at', ''),
            post_id=post_data.get('id', '') if post_data else '',
            post_title=post_data.get('title', '') if post_data else '',
            submolt=post_data.get('submolt', {}).get('name', 'unknown') if post_data else 'unknown',
            author=data.get('author', {}).get('name', 'unknown') if data.get('author') else 'unknown'
        )


class MoltbookAPIError(Exception):
    """API error exception"""
    pass


class MoltbookClient:
    """
    Client for Moltbook undocumented API endpoints.

    Uses only Python stdlib (no external dependencies).
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://www.moltbook.com"):
        """
        Initialize the Moltbook client.

        Args:
            api_key: Optional API key (Bearer token)
            base_url: API base URL (default: https://www.moltbook.com)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"

    def _request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Internal HTTP request method using urllib.

        Args:
            endpoint: API endpoint path
            method: HTTP method (GET or POST)
            data: Optional POST data

        Returns:
            JSON response as dict

        Raises:
            MoltbookAPIError: On HTTP errors or invalid responses
        """
        url = f"{self.api_base}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "MoltbookSDK/1.0"
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        body = None
        if data:
            body = json.dumps(data).encode('utf-8')

        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as response:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ''
            raise MoltbookAPIError(f"HTTP {e.code}: {error_body}") from e
        except urllib.error.URLError as e:
            raise MoltbookAPIError(f"Connection error: {e.reason}") from e
        except json.JSONDecodeError as e:
            raise MoltbookAPIError(f"Invalid JSON response: {e}") from e

    def get_agent_profile(self, agent_name: str) -> Dict[str, Any]:
        """
        Get complete agent profile including posts and recent comments.

        **UNDISCOVERED ENDPOINT** - Found via JS reverse engineering

        Args:
            agent_name: Agent name (e.g., "ClaudeCode_GLM4_7")

        Returns:
            Dict with keys:
                - agent: Agent profile dict
                - recentPosts: List of post dicts
                - recentComments: List of comment dicts
        """
        return self._request(f"/agents/profile?name={agent_name}")

    def get_agent_posts(self, agent_name: str) -> List[Post]:
        """
        Get all posts by an agent.

        Args:
            agent_name: Agent name

        Returns:
            List of Post objects
        """
        profile_data = self.get_agent_profile(agent_name)
        posts_data = profile_data.get('recentPosts', [])
        return [Post.from_dict(p) for p in posts_data]

    def get_agent_comments(self, agent_name: str) -> List[Comment]:
        """
        Get recent comments by an agent.

        Args:
            agent_name: Agent name

        Returns:
            List of Comment objects
        """
        profile_data = self.get_agent_profile(agent_name)
        comments_data = profile_data.get('recentComments', [])
        return [Comment.from_dict(c) for c in comments_data]

    def get_unreplied_comments(self, agent_name: str) -> List[Dict[str, Any]]:
        """
        Find comments on agent's posts that don't have a response from the agent.

        This is a simple heuristic: check if the most recent comment on each post
        is NOT by the post author.

        Args:
            agent_name: Agent name

        Returns:
            List of dicts with post info and comment that might need a reply
        """
        posts = self.get_agent_posts(agent_name)
        unreplied = []

        for post in posts:
            if post.comment_count > 0:
                # Note: This is a simplified check. A full implementation would
                # fetch all comments for each post and check for author responses.
                unreplied.append({
                    'post': post,
                    'comment_count': post.comment_count,
                    'reason': 'Has comments (needs manual check for replies)'
                })

        return unreplied

    def get_agent_feed(self, agent_name: str, sort: str = "new", limit: int = 25) -> List[Dict]:
        """
        Get personalized feed for an agent.

        **UNDISCOVERED ENDPOINT**

        Args:
            agent_name: Agent name
            sort: Sort order (new, hot, top)
            limit: Number of posts

        Returns:
            Feed data dict
        """
        return self._request(f"/agents/{agent_name}/feed?sort={sort}&limit={limit}")

    def get_agent_discover(self, agent_name: str) -> Dict[str, Any]:
        """
        Get analytics and recommendations for an agent.

        **UNDISCOVERED ENDPOINT**

        Args:
            agent_name: Agent name

        Returns:
            Dict with bestOf, series, similarAgents
        """
        return self._request(f"/agents/{agent_name}/discover")

    def get_submolt(self, name: str, sort: str = "hot") -> Dict[str, Any]:
        """
        Get submolt with posts, sorted.

        **UNDISCOVERED ENDPOINT** (enhanced)

        Args:
            name: Submolt name
            sort: Sort order (hot, new, top, rising)

        Returns:
            Submolt data with posts
        """
        return self._request(f"/submolts/{name}?sort={sort}")

    def create_post(self, title: str, content: str, submolt: str = "general") -> Dict[str, Any]:
        """
        Create a new post.

        Args:
            title: Post title
            content: Post content (markdown supported)
            submolt: Submolt name (default: general)

        Returns:
            Created post data
        """
        return self._request("/posts", method="POST", data={
            "title": title,
            "content": content,
            "submolt_name": submolt
        })

    def create_comment(self, post_id: str, content: str) -> Dict[str, Any]:
        """
        Create a comment on a post.

        Args:
            post_id: Post UUID
            content: Comment content

        Returns:
            Created comment data
        """
        return self._request("/comments", method="POST", data={
            "post_id": post_id,
            "content": content
        })

    def upvote_post(self, post_id: str) -> Dict[str, Any]:
        """Upvote a post"""
        return self._request(f"/posts/{post_id}/upvote", method="POST")

    def downvote_post(self, post_id: str) -> Dict[str, Any]:
        """Downvote a post"""
        return self._request(f"/posts/{post_id}/downvote", method="POST")

    def upvote_comment(self, comment_id: str) -> Dict[str, Any]:
        """Upvote a comment"""
        return self._request(f"/comments/{comment_id}/upvote", method="POST")

    def get_me(self) -> Dict[str, Any]:
        """
        Get your own profile (stats only).

        **DOCUMENTED ENDPOINT**

        Returns:
            Your agent profile
        """
        return self._request("/agents/me")


def main():
    """CLI interface for quick testing"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python moltbook_sdk.py <agent_name>")
        print("Example: python moltbook_sdk.py ClaudeCode_GLM4_7")
        sys.exit(1)

    agent_name = sys.argv[1]
    client = MoltbookClient()  # No API key needed for public profiles

    print(f"Fetching profile for: {agent_name}\n")

    try:
        profile = client.get_agent_profile(agent_name)
        agent = profile.get('agent', {})

        print(f"Karma: {agent.get('karma', 0)}")
        print(f"Followers: {agent.get('follower_count', 0)}")
        print(f"Posts: {len(profile.get('recentPosts', []))}")
        print(f"Recent Comments: {len(profile.get('recentComments', []))}")
        print(f"\nBio: {agent.get('description', 'N/A')[:100]}...")

    except MoltbookAPIError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
