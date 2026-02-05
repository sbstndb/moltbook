#!/usr/bin/env python3
"""
Smart Commenter - AI-Powered Comment Drafting System

Analyzes comments and generates intelligent, persona-consistent response drafts.
Supports multiple response strategies: technical, friendly, debate, curious.

Author: ClaudeCode_GLM4_7
Date: 2026-02-05
"""

import sys
import os
import re
from typing import List, Dict, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import moltbook_sdk


class CommentAnalyzer:
    """Analyzes comment content to determine type and sentiment"""

    # Keywords for different comment types
    QUESTION_KEYWORDS = [
        'how', 'what', 'why', 'when', 'where', 'can', 'could', 'would',
        'is', 'are', 'do', 'does', '?', 'anyone', 'someone', 'help'
    ]

    TECH_KEYWORDS = [
        'api', 'code', 'function', 'bug', 'debug', 'error', 'stack',
        'algorithm', 'optimization', 'performance', 'async', 'thread',
        'memory', 'cpu', 'database', 'server', 'client', 'protocol',
        'python', 'rust', 'javascript', 'golang', 'java', 'c++'
    ]

    AGREEMENT_KEYWORDS = [
        'agree', 'exactly', 'totally', '+1', 'absolutely', 'yes',
        'correct', 'right', 'definitely', 'spot on', 'this'
    ]

    DISAGREEMENT_KEYWORDS = [
        'disagree', 'actually', 'but', 'however', 'wrong', 'not really',
        'counterpoint', 'respectfully', 'challenge'
    ]

    @staticmethod
    def get_comment_type(comment: str) -> str:
        """Determine the type of comment"""
        comment_lower = comment.lower()

        # Check for questions
        if any(kw in comment_lower for kw in CommentAnalyzer.QUESTION_KEYWORDS):
            return 'question'

        # Check for disagreement
        if any(kw in comment_lower for kw in CommentAnalyzer.DISAGREEMENT_KEYWORDS):
            return 'disagreement'

        # Check for agreement
        if any(kw in comment_lower for kw in CommentAnalyzer.AGREEMENT_KEYWORDS):
            return 'agreement'

        # Check for technical content
        if any(kw in comment_lower for kw in CommentAnalyzer.TECH_KEYWORDS):
            return 'technical'

        return 'general'

    @staticmethod
    def extract_topic(comment: str) -> str:
        """Extract the main topic from a comment"""
        # Simple extraction: first sentence or first 50 chars
        sentences = re.split(r'[.!?]', comment)
        if sentences:
            topic = sentences[0].strip()
            return topic[:100] if len(topic) > 100 else topic
        return comment[:100]

    @staticmethod
    def detect_technical_depth(comment: str) -> str:
        """Detect how technical the comment is"""
        tech_count = sum(1 for kw in CommentAnalyzer.TECH_KEYWORDS if kw.lower() in comment.lower())
        code_snippets = len(re.findall(r'```|`[^`]+`', comment))

        if tech_count >= 3 or code_snippets >= 2:
            return 'deep'
        elif tech_count >= 1 or code_snippets >= 1:
            return 'medium'
        return 'shallow'


class SmartResponder:
    """Generates intelligent response drafts based on comment analysis"""

    def __init__(self, persona: str = "snarky_expert"):
        """
        Initialize the responder with a specific persona.

        Personas:
        - snarky_expert: Sarcastic but competent (House MD style)
        - helpful_mentor: Friendly and educational
        - tech_bro: Casual, emoji-heavy, very direct
        - debate_lord: Loves intellectual discourse
        """
        self.persona = persona
        self.analyzer = CommentAnalyzer()

    def generate_response(self, comment: str, post_context: str = "",
                         strategy: str = "auto") -> Tuple[str, str]:
        """
        Generate a response draft for a comment.

        Args:
            comment: The comment to respond to
            post_context: The original post content (for context)
            strategy: Response strategy (auto, technical, friendly, debate, curious)

        Returns:
            Tuple of (draft_response, reasoning)
        """
        comment_type = self.analyzer.get_comment_type(comment)
        tech_depth = self.analyzer.detect_technical_depth(comment)

        if strategy == "auto":
            strategy = self._select_strategy(comment_type, tech_depth)

        response_templates = self._get_templates(strategy, self.persona)
        draft = self._build_response(comment, comment_type, response_templates)

        reasoning = f"Type: {comment_type}, Depth: {tech_depth}, Strategy: {strategy}"
        return draft, reasoning

    def _select_strategy(self, comment_type: str, tech_depth: str) -> str:
        """Auto-select the best response strategy"""
        if tech_depth == 'deep':
            return 'technical'
        elif comment_type == 'question':
            return 'technical' if tech_depth != 'shallow' else 'friendly'
        elif comment_type == 'disagreement':
            return 'debate'
        elif comment_type == 'agreement':
            return 'curious'
        return 'friendly'

    def _get_templates(self, strategy: str, persona: str) -> List[str]:
        """Get response templates based on strategy and persona"""
        templates = {
            'snarky_expert': {
                'technical': [
                    "Look, {response}. The key insight you're missing is {insight}.",
                    "Not quite. {response}. Here's what's actually happening: {insight}.",
                    "Close, but {response}. The real issue is {insight}.",
                ],
                'friendly': [
                    "Actually, {response}. Trust me, I've seen this before.",
                    "Here's the thing: {response}. Happy to explain if you're actually interested.",
                ],
                'debate': [
                    "Interesting take, but {response}. Let me explain why you're wrong: {insight}.",
                    "Respectfully, that's {response}. The data shows: {insight}.",
                ],
                'curious': [
                    "Why do you think {response}? Genuinely curious about your reasoning.",
                    "That's an interesting perspective. {response} - expand on that?",
                ]
            },
            'helpful_mentor': {
                'technical': [
                    "Great question! {response}. The key concept here is {insight}.",
                    "Let me break this down: {response}. Essentially, {insight}.",
                ],
                'friendly': [
                    "Thanks for sharing! {response}. Feel free to ask if you need more details.",
                    "I appreciate your input. {response}. Let me know if I can clarify!",
                ],
                'debate': [
                    "I see your point, but {response}. Have you considered {insight}?",
                    "That's a valid perspective. {response}. However, {insight}.",
                ],
                'curious': [
                    "That's interesting! {response}. Can you tell me more about {topic}?",
                    "I'd love to hear more. {response}. What led you to this conclusion?",
                ]
            },
            'tech_bro': {
                'technical': [
                    "yo so {response}. tldr: {insight}",
                    "not quite bro, {response}. the fix: {insight}. hth",
                ],
                'friendly': [
                    "nice! {response}. lmk if u need more info 👍",
                    "thanks for the comment. {response}. cheers!",
                ],
                'debate': [
                    "hm not sure i agree. {response}. actually {insight}.",
                    "wait what. {response}. check this out: {insight}.",
                ],
                'curious': [
                    "interesting. {response}. why?",
                    "yo expand on that. {response}? 🤔",
                ]
            },
            'debate_lord': {
                'technical': [
                    "Let's examine this carefully. {response}. The underlying principle is {insight}.",
                    "A nuanced analysis shows: {response}. Fundamentally, {insight}.",
                ],
                'friendly': [
                    "I appreciate your contribution. {response}. Would love to discuss further.",
                ],
                'debate': [
                    "I must respectfully disagree. {response}. The evidence suggests: {insight}.",
                    "A compelling counterargument: {response}. Consider {insight}.",
                ],
                'curious': [
                    "Fascinating perspective. {response}. What's your basis for this?",
                    "I'm intrigued. {response}. Could you elaborate on {topic}?",
                ]
            }
        }

        return templates.get(persona, {}).get(strategy, ["Thanks for your comment! {response}"])

    def _build_response(self, comment: str, comment_type: str,
                       templates: List[str]) -> str:
        """Build the actual response from templates"""
        import random

        topic = CommentAnalyzer.extract_topic(comment)

        # Generate response parts based on comment type
        responses = {
            'question': f"the answer is more complex than it seems. {topic} is interesting",
            'technical': f"you're thinking about {topic} the wrong way",
            'agreement': f"you're right about {topic}",
            'disagreement': f"your point about {topic} misses something",
            'general': f"{topic} is worth discussing"
        }

        response = responses.get(comment_type, responses['general'])
        insight = f"there's more to {topic} than meets the eye"

        # Select template and fill in
        template = random.choice(templates)
        draft = template.format(response=response, insight=insight, topic=topic)

        return draft


class BatchDraftGenerator:
    """Generate response drafts for multiple comments"""

    def __init__(self, persona: str = "snarky_expert"):
        self.responder = SmartResponder(persona)

    def generate_for_post(self, post: moltbook_sdk.Post,
                          comments: List[moltbook_sdk.Comment]) -> List[Dict]:
        """
        Generate response drafts for all comments on a post.

        Args:
            post: The post object
            comments: List of comments on the post

        Returns:
            List of dicts with comment info and drafted responses
        """
        drafts = []

        for comment in comments:
            # Skip if comment is by the post author (probably self-reply)
            if comment.author == post.submolt:
                continue

            draft, reasoning = self.responder.generate_response(
                comment.content,
                post.content[:200],  # Use post content for context
                strategy="auto"
            )

            drafts.append({
                'comment_id': comment.id,
                'comment_author': comment.author,
                'comment_content': comment.content,
                'comment_upvotes': comment.upvotes,
                'draft_response': draft,
                'reasoning': reasoning,
                'priority': self._calculate_priority(comment)
            })

        # Sort by priority
        drafts.sort(key=lambda x: x['priority'], reverse=True)
        return drafts

    def _calculate_priority(self, comment: moltbook_sdk.Comment) -> int:
        """Calculate response priority for a comment"""
        score = comment.upvotes * 2
        # Questions get higher priority
        if '?' in comment.content:
            score += 5
        # Technical comments get bonus
        if any(kw in comment.content.lower() for kw in CommentAnalyzer.TECH_KEYWORDS):
            score += 3
        return score


def display_drafts(drafts: List[Dict], post_title: str):
    """Display generated response drafts"""
    print(f"\n{'=' * 70}")
    print(f"📝 DRAFT RESPONSES FOR: {post_title}")
    print('=' * 70)

    if not drafts:
        print("No comments to respond to.")
        return

    for i, draft in enumerate(drafts, 1):
        print(f"\n{i}. Response to @{draft['comment_author']}'s comment")
        print(f"   Priority: {draft['priority']} | {draft['reasoning']}")
        print(f"   Original: {draft['comment_content'][:80]}...")
        print(f"   Draft: {draft['draft_response']}")
        print(f"   Comment ID: {draft['comment_id']}")


def analyze_and_suggest(agent_name: str, api_key: str = None,
                       persona: str = "snarky_expert"):
    """
    Analyze an agent's posts and generate response suggestions.

    Args:
        agent_name: Agent name to analyze
        api_key: Optional API key
        persona: Response persona to use
    """
    client = moltbook_sdk.MoltbookClient(api_key=api_key)
    generator = BatchDraftGenerator(persona)

    print(f"🤖 Smart Commenter - Analyzing {agent_name}")
    print('=' * 70)

    try:
        profile = client.get_agent_profile(agent_name)
        posts_data = profile.get('recentPosts', [])
        posts = [moltbook_sdk.Post.from_dict(p) for p in posts_data]

        all_drafts = []

        for post in posts:
            if post.comment_count == 0:
                continue

            print(f"\n📌 Analyzing: {post.title}")
            print(f"   💬 {post.comment_count} comments")

            # Note: In a real implementation, we'd fetch all comments for the post
            # For now, we'll show what we'd do
            print(f"   (Would fetch {post.comment_count} comments and generate drafts)")
            print(f"   Post ID: {post.id}")

            # Placeholder for when we have comment fetching
            all_drafts.append({
                'post': post,
                'drafts': []  # Would be filled with actual comment data
            })

        print("\n" + "=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        print(f"Posts with comments: {len(all_drafts)}")
        print(f"Persona: {persona}")
        print("\nNote: Full comment fetching requires additional API endpoints.")

    except moltbook_sdk.MoltbookAPIError as e:
        print(f"❌ Error: {e}")


def demo_mode():
    """Demonstrate the smart commenter capabilities"""
    print("🤖 Smart Commenter - Demo Mode")
    print('=' * 70)
    print("\nTesting different comment types with snarky_expert persona:\n")

    responder = SmartResponder(persona="snarky_expert")

    test_comments = [
        ("How do I optimize this function for performance?", "question"),
        ("Actually, the issue is with the async implementation.", "disagreement"),
        ("Great explanation! This really helped me understand.", "agreement"),
        ("The API endpoint returns 404 when I use query parameters.", "technical"),
    ]

    for comment, expected_type in test_comments:
        print(f"Comment: {comment}")
        print(f"Expected Type: {expected_type}")

        draft, reasoning = responder.generate_response(comment)
        print(f"Reasoning: {reasoning}")
        print(f"Draft: {draft}")
        print("-" * 70)


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate intelligent comment drafts for Moltbook engagement'
    )
    parser.add_argument(
        'agent',
        nargs='?',
        help='Agent name to analyze (or --demo for demo mode)'
    )
    parser.add_argument(
        '--api-key',
        help='Moltbook API key',
        default=os.environ.get('MOLTBOOK_API_KEY')
    )
    parser.add_argument(
        '--persona',
        help='Response persona (snarky_expert, helpful_mentor, tech_bro, debate_lord)',
        default='snarky_expert',
        choices=['snarky_expert', 'helpful_mentor', 'tech_bro', 'debate_lord']
    )
    parser.add_argument(
        '--demo',
        help='Run demo mode with sample comments',
        action='store_true'
    )

    args = parser.parse_args()

    if args.demo or not args.agent:
        demo_mode()
    else:
        analyze_and_suggest(args.agent, args.api_key, args.persona)


if __name__ == "__main__":
    main()
