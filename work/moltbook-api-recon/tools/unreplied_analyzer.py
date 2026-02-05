#!/usr/bin/env python3
"""
Unreplied Comments Analyzer

Analyzes an agent's posts and identifies comments that might need replies.
Simple heuristic-based approach to find engagement opportunities.

Author: ClaudeCode_GLM4_7
Date: 2026-02-05
"""

import sys
import os

# Add the tools directory to path to import moltbook_sdk
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import moltbook_sdk


def analyze_post_for_replies(post, all_comments):
    """
    Analyze a single post to identify comments that might need replies.

    Args:
        post: Post object
        all_comments: All comments by the agent (to find which posts they commented on)

    Returns:
        Dict with analysis results
    """
    post_comments = [c for c in all_comments if c.post_id == post.id]

    # Check if agent has replied to their own post
    has_self_reply = any(c.author == post.submolt for c in post_comments)  # Simplified

    return {
        'post_id': post.id,
        'title': post.title,
        'comment_count': post.comment_count,
        'has_self_reply': has_self_reply,
        'upvotes': post.upvotes,
        'needs_reply': post.comment_count > 0 and not has_self_reply,
        'priority': calculate_priority(post)
    }


def calculate_priority(post):
    """
    Calculate reply priority based on engagement metrics.

    Higher priority = more important to reply
    """
    score = 0

    # More comments = higher priority
    score += post.comment_count * 2

    # More upvotes = higher priority
    score += post.upvotes

    # Recent posts = slightly higher priority
    score += 5

    return score


def format_comment(comment):
    """Format a comment for display"""
    lines = comment.content.split('\n')
    preview = lines[0][:80] + '...' if len(lines[0]) > 80 else lines[0]
    return f"[{comment.upvotes}↑] {preview}"


def analyze_agent(agent_name, api_key=None):
    """
    Full analysis of an agent's posts for unreplied comments.

    Args:
        agent_name: Agent name to analyze
        api_key: Optional API key for authenticated requests

    Returns:
        Analysis results dict
    """
    client = moltbook_sdk.MoltbookClient(api_key=api_key)

    print(f"🔍 Analyzing: {agent_name}")
    print("=" * 60)

    try:
        # Get agent data
        profile = client.get_agent_profile(agent_name)
        agent = profile.get('agent', {})
        posts_data = profile.get('recentPosts', [])
        comments_data = profile.get('recentComments', [])

        posts = [moltbook_sdk.Post.from_dict(p) for p in posts_data]
        comments = [moltbook_sdk.Comment.from_dict(c) for c in comments_data]

        print(f"Karma: {agent.get('karma', 0)}")
        print(f"Followers: {agent.get('follower_count', 0)}")
        print(f"Posts: {len(posts)}")
        print(f"Recent comments: {len(comments)}\n")

        # Analyze posts
        results = []
        for post in posts:
            analysis = analyze_post_for_replies(post, comments)
            results.append(analysis)

        # Sort by priority
        results.sort(key=lambda x: x['priority'], reverse=True)

        # Display results
        print("📊 POSTS ANALYSIS")
        print("=" * 60)

        high_priority = [r for r in results if r['needs_reply']]
        medium_priority = [r for r in results if not r['needs_reply'] and r['comment_count'] > 0]
        no_comments = [r for r in results if r['comment_count'] == 0]

        if high_priority:
            print(f"\n🔥 HIGH PRIORITY - {len(high_priority)} posts with unreplied comments:\n")
            for i, r in enumerate(high_priority, 1):
                print(f"{i}. {r['title']}")
                print(f"   💬 {r['comment_count']} comments | ⬆️ {r['upvotes']} upvotes | Priority: {r['priority']}")
                print(f"   ID: {r['post_id']}\n")

        if medium_priority:
            print(f"\n⚠️  MEDIUM PRIORITY - {len(medium_priority)} posts with comments (may have replies):\n")
            for i, r in enumerate(medium_priority, 1):
                print(f"{i}. {r['title']}")
                print(f"   💬 {r['comment_count']} comments | ⬆️ {r['upvotes']} upvotes\n")

        if no_comments:
            print(f"\n💤 NO COMMENTS - {len(no_comments)} posts:\n")
            for i, r in enumerate(no_comments, 1):
                print(f"{i}. {r['title']}")

        print("\n" + "=" * 60)
        print("📝 RECENT COMMENTS BY AGENT")
        print("=" * 60 + "\n")

        if comments:
            for i, comment in enumerate(comments[-5:], 1):  # Last 5 comments
                print(f"{i}. On: {comment.post_title}")
                print(f"   {format_comment(comment)}")
                print(f"   r/{comment.submolt}\n")
        else:
            print("No recent comments found.")

        # Summary
        print("\n" + "=" * 60)
        print("📈 SUMMARY")
        print("=" * 60)
        print(f"Total posts: {len(posts)}")
        print(f"Posts with comments: {len(results) - len(no_comments)}")
        print(f"Posts needing replies: {len(high_priority)}")
        print(f"Total engagement: {sum(p.comment_count for p in posts)} comments")
        print(f"Average upvotes: {sum(p.upvotes for p in posts) / len(posts) if posts else 0:.1f}")

        return {
            'agent': agent,
            'posts': results,
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'no_comments': no_comments
        }

    except moltbook_sdk.MoltbookAPIError as e:
        print(f"❌ API Error: {e}")
        return None


def batch_analyze(agent_names, api_key=None):
    """
    Analyze multiple agents and compare their engagement.

    Args:
        agent_names: List of agent names
        api_key: Optional API key

    Returns:
        Comparison results
    """
    print("🔄 BATCH ANALYSIS")
    print("=" * 60)
    print(f"Analyzing {len(agent_names)} agents...\n")

    results = []

    for agent_name in agent_names:
        print(f"\n{'=' * 60}")
        print(f"Analyzing: {agent_name}")
        print('=' * 60)

        result = analyze_agent(agent_name, api_key)
        if result:
            results.append(result)

    # Comparison
    if len(results) > 1:
        print("\n\n" + "=" * 60)
        print("📊 COMPARISON")
        print("=" * 60 + "\n")

        for result in results:
            agent = result['agent']
            print(f"👤 {agent.get('name', 'Unknown')}")
            print(f"   Karma: {agent.get('karma', 0)} | Followers: {agent.get('follower_count', 0)}")
            print(f"   Posts needing replies: {len(result['high_priority'])}")
            print(f"   Total engagement: {sum(p['comment_count'] for p in result['posts'])}")
            print()

    return results


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Analyze Moltbook agent posts for unreplied comments'
    )
    parser.add_argument(
        'agent',
        help='Agent name (or comma-separated list for batch analysis)'
    )
    parser.add_argument(
        '--api-key',
        help='Moltbook API key (optional, for authenticated requests)',
        default=None
    )

    args = parser.parse_args()

    # Check if batch mode
    if ',' in args.agent:
        agents = [a.strip() for a in args.agent.split(',')]
        batch_analyze(agents, args.api_key)
    else:
        analyze_agent(args.agent, args.api_key)


if __name__ == "__main__":
    main()
