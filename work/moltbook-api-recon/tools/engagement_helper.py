#!/usr/bin/env python3
"""
Engagement Helper - Quick script for posting comments

Author: ClaudeCode_GLM4_7
Date: 2026-02-05

Usage:
    # Interactive mode
    python3 engagement_helper.py

    # Direct mode
    python3 engagement_helper.py --post-id POST_ID --comment "Great post!"
"""

import sys
import os

# Add tools directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import moltbook_sdk


def interactive_mode(client):
    """Interactive mode for engaging with posts"""
    print("🤖 Moltbook Engagement Helper")
    print("=" * 60)
    print("Modes:")
    print("  1. View agent posts")
    print("  2. Post a comment")
    print("  3. Exit")
    print()

    while True:
        choice = input("Select mode (1-3): ").strip()

        if choice == "1":
            agent_name = input("Agent name: ").strip()
            display_posts(client, agent_name)

        elif choice == "2":
            post_id = input("Post ID: ").strip()
            comment = input("Comment: ").strip()
            post_comment(client, post_id, comment)

        elif choice == "3":
            print("Goodbye! 👋")
            break

        else:
            print("Invalid choice. Try again.")


def display_posts(client, agent_name):
    """Display all posts for an agent"""
    try:
        posts = client.get_agent_posts(agent_name)

        if not posts:
            print(f"No posts found for {agent_name}")
            return

        print(f"\n📝 Posts by {agent_name}:")
        print("=" * 60)

        for i, post in enumerate(posts, 1):
            print(f"\n{i}. {post.title}")
            print(f"   ID: {post.id}")
            print(f"   ⬆️ {post.upvotes} | 💬 {post.comment_count} comments")
            print(f"   r/{post.submolt} | {post.created_at[:10]}")

            # Preview content
            preview = post.content[:100].replace('\n', ' ')
            if len(post.content) > 100:
                preview += "..."
            print(f"   Preview: {preview}")

    except moltbook_sdk.MoltbookAPIError as e:
        print(f"Error: {e}")


def post_comment(client, post_id, comment):
    """Post a comment to a post"""
    try:
        result = client.create_comment(post_id, comment)

        if result.get('success'):
            print("\n✅ Comment posted successfully!")
        else:
            print(f"\n❌ Failed to post comment: {result.get('error', 'Unknown error')}")

    except moltbook_sdk.MoltbookAPIError as e:
        print(f"\n❌ Error posting comment: {e}")


def batch_comment_mode(client, agent_name):
    """
    Find unreplied comments and offer to respond to them.

    This is a helper for the unreplied analyzer workflow.
    """
    print(f"🔍 Finding posts with comments for {agent_name}...\n")

    try:
        posts = client.get_agent_posts(agent_name)

        posts_with_comments = [p for p in posts if p.comment_count > 0]

        if not posts_with_comments:
            print("No posts with comments found.")
            return

        print("Posts with comments:")
        for i, post in enumerate(posts_with_comments, 1):
            print(f"{i}. {post.title}")
            print(f"   ID: {post.id}")
            print(f"   💬 {post.comment_count} comments\n")

        print("\nNote: To comment on a post, use:")
        print(f"  python3 engagement_helper.py --post-id <ID> --comment \"your comment\"")

    except moltbook_sdk.MoltbookAPIError as e:
        print(f"Error: {e}")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Helper script for engaging with Moltbook posts'
    )
    parser.add_argument(
        '--post-id',
        help='Post ID to comment on'
    )
    parser.add_argument(
        '--comment',
        help='Comment content'
    )
    parser.add_argument(
        '--agent',
        help='Agent name to view posts for'
    )
    parser.add_argument(
        '--batch',
        help='Find posts with comments for an agent',
        action='store_true'
    )
    parser.add_argument(
        '--api-key',
        help='Moltbook API key (required for posting)',
        default=os.environ.get('MOLTBOOK_API_KEY')
    )

    args = parser.parse_args()

    # For posting, API key is required
    if args.post_id and not args.api_key:
        print("❌ API key required for posting comments.")
        print("   Set MOLTBOOK_API_KEY environment variable or use --api-key")
        sys.exit(1)

    client = moltbook_sdk.MoltbookClient(api_key=args.api_key)

    # Direct comment mode
    if args.post_id and args.comment:
        post_comment(client, args.post_id, args.comment)
        return

    # View agent posts mode
    if args.agent:
        display_posts(client, args.agent)
        return

    # Batch mode
    if args.batch:
        if not args.agent:
            print("❌ --agent required for --batch mode")
            sys.exit(1)
        batch_comment_mode(client, args.agent)
        return

    # Default: interactive mode
    interactive_mode(client)


if __name__ == "__main__":
    main()
