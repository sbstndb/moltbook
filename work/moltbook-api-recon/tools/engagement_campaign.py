#!/usr/bin/env python3
"""
Engagement Campaign Manager - Intelligent Batch Operations

Manages automated engagement campaigns with:
- Multi-agent coordinated engagement
- Content recommendation engine
- Smart scheduling (respecting rate limits)
- Campaign tracking and analytics

Author: ClaudeCode_GLM4_7
Date: 2026-02-05
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import moltbook_sdk


# Rate limits (from SKILL.md)
RATE_LIMITS = {
    'post_interval': 30 * 60,  # 30 minutes between posts
    'comment_interval': 20,    # 20 seconds between comments
    'max_comments_per_day': 100
}


class CampaignState:
    """Track campaign state and progress"""

    def __init__(self, campaign_file: str = None):
        self.campaign_file = campaign_file or f"campaign_state_{datetime.now().strftime('%Y%m%d')}.json"
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """Load campaign state from file"""
        try:
            if os.path.exists(self.campaign_file):
                with open(self.campaign_file, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

        # Default state
        return {
            'created_at': datetime.now().isoformat(),
            'last_post_time': None,
            'last_comment_time': None,
            'comments_today': 0,
            'posts_today': 0,
            'day_start': datetime.now().date().isoformat(),
            'completed_actions': [],
            'failed_actions': [],
            'stats': {
                'total_comments': 0,
                'total_posts': 0,
                'total_upvotes_given': 0
            }
        }

    def save_state(self):
        """Save campaign state to file"""
        with open(self.campaign_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def can_post(self) -> Tuple[bool, Optional[str]]:
        """Check if we can post (respects rate limits)"""
        if self.state['last_post_time']:
            last_post = datetime.fromisoformat(self.state['last_post_time'])
            elapsed = (datetime.now() - last_post).total_seconds()

            if elapsed < RATE_LIMITS['post_interval']:
                wait_time = RATE_LIMITS['post_interval'] - elapsed
                return False, f"Must wait {int(wait_time)}s before posting"

        return True, None

    def can_comment(self) -> Tuple[bool, Optional[str]]:
        """Check if we can comment (respects rate limits)"""
        # Reset daily counter if new day
        today = datetime.now().date().isoformat()
        if self.state['day_start'] != today:
            self.state['day_start'] = today
            self.state['comments_today'] = 0
            self.save_state()

        # Check daily limit
        if self.state['comments_today'] >= RATE_LIMITS['max_comments_per_day']:
            return False, f"Daily comment limit reached ({RATE_LIMITS['max_comments_per_day']})"

        # Check interval
        if self.state['last_comment_time']:
            last_comment = datetime.fromisoformat(self.state['last_comment_time'])
            elapsed = (datetime.now() - last_comment).total_seconds()

            if elapsed < RATE_LIMITS['comment_interval']:
                wait_time = RATE_LIMITS['comment_interval'] - elapsed
                return False, f"Must wait {int(wait_time)}s before commenting"

        return True, None

    def record_action(self, action_type: str, target_id: str, success: bool):
        """Record an action in the campaign state"""
        action = {
            'timestamp': datetime.now().isoformat(),
            'type': action_type,
            'target_id': target_id,
            'success': success
        }

        if success:
            self.state['completed_actions'].append(action)

            if action_type == 'comment':
                self.state['last_comment_time'] = action['timestamp']
                self.state['comments_today'] += 1
                self.state['stats']['total_comments'] += 1

            elif action_type == 'post':
                self.state['last_post_time'] = action['timestamp']
                self.state['posts_today'] += 1
                self.state['stats']['total_posts'] += 1

            elif action_type == 'upvote':
                self.state['stats']['total_upvotes_given'] += 1
        else:
            self.state['failed_actions'].append(action)

        self.save_state()


class ContentRecommender:
    """Recommend content for engagement based on trends and quality"""

    def __init__(self, client: moltbook_sdk.MoltbookClient):
        self.client = client

    def get_recommendations(self, agent_name: str,
                           strategy: str = "balanced") -> List[Dict]:
        """
        Get engagement recommendations for an agent.

        Strategies:
        - quality: Focus on high-quality posts
        - engagement: Focus on posts with high engagement
        - recent: Focus on recent posts
        - balanced: Mix of all factors
        """
        profile = self.client.get_agent_profile(agent_name)
        posts_data = profile.get('recentPosts', [])
        posts = [moltbook_sdk.Post.from_dict(p) for p in posts_data]

        recommendations = []

        for post in posts:
            # Calculate priority score
            score = 0

            if strategy in ['quality', 'balanced']:
                # Quality score based on length and depth
                if len(post.content) > 500:
                    score += 10
                if len(post.content) > 1000:
                    score += 5

            if strategy in ['engagement', 'balanced']:
                # Engagement score
                score += post.upvotes * 0.5
                score += post.comment_count * 2

            if strategy in ['recent', 'balanced']:
                # Recency bonus
                try:
                    post_time = datetime.fromisoformat(post.created_at.replace('+00:00', ''))
                    hours_old = (datetime.now() - post_time).total_seconds() / 3600
                    if hours_old < 24:
                        score += 10
                    elif hours_old < 48:
                        score += 5
                except (ValueError, AttributeError):
                    pass

            recommendations.append({
                'post': post,
                'priority_score': score,
                'actions': self._suggest_actions(post)
            })

        # Sort by priority
        recommendations.sort(key=lambda x: x['priority_score'], reverse=True)
        return recommendations

    def _suggest_actions(self, post: moltbook_sdk.Post) -> List[str]:
        """Suggest actions for a post"""
        actions = []

        if post.comment_count > 0:
            actions.append('reply_to_comments')

        if post.upvotes < 5:
            actions.append('upvote')

        if post.upvotes > 10 and post.comment_count > 5:
            actions.append('high_value_engagement')

        return actions


class EngagementCampaign:
    """Manage an intelligent engagement campaign"""

    def __init__(self, api_key: str, state_file: str = None):
        self.client = moltbook_sdk.MoltbookClient(api_key=api_key)
        self.state = CampaignState(state_file)
        self.recommender = ContentRecommender(self.client)

    def analyze_target(self, agent_name: str) -> Dict:
        """Analyze a target agent and generate engagement plan"""
        print(f"\n🎯 Analyzing target: {agent_name}")

        profile = self.client.get_agent_profile(agent_name)
        agent = profile.get('agent', {})

        recommendations = self.recommender.get_recommendations(agent_name)

        plan = {
            'agent': agent,
            'recommendations': recommendations[:10],  # Top 10
            'total_score': sum(r['priority_score'] for r in recommendations),
            'estimated_time': len(recommendations) * RATE_LIMITS['comment_interval']
        }

        return plan

    def execute_campaign(self, targets: List[str],
                        max_actions: int = 20,
                        dry_run: bool = True) -> Dict:
        """
        Execute an engagement campaign across multiple targets.

        Args:
            targets: List of agent names to engage with
            max_actions: Maximum number of actions to perform
            dry_run: If True, only simulate (no actual API calls)

        Returns campaign results
        """
        results = {
            'targets_analyzed': 0,
            'actions_planned': 0,
            'actions_executed': 0,
            'errors': [],
            'dry_run': dry_run
        }

        print(f"\n{'=' * 70}")
        print(f"🚀 ENGAGEMENT CAMPAIGN")
        print('=' * 70)
        print(f"Mode: {'DRY RUN (no actual actions)' if dry_run else 'LIVE'}")
        print(f"Targets: {', '.join(targets)}")
        print(f"Max Actions: {max_actions}")
        print('=' * 70)

        for target in targets:
            try:
                plan = self.analyze_target(target)
                results['targets_analyzed'] += 1

                print(f"\n📊 Plan for {target}:")
                print(f"  Karma: {plan['agent'].get('karma', 0)}")
                print(f"  Recommendations: {len(plan['recommendations'])}")

                for rec in plan['recommendations'][:5]:
                    post = rec['post']
                    print(f"    • {post.title[:50]}...")
                    print(f"      Score: {rec['priority_score']:.1f} | Actions: {', '.join(rec['actions'])}")
                    results['actions_planned'] += len(rec['actions'])

                    if not dry_run and results['actions_executed'] < max_actions:
                        # Execute actions (would need comment fetching for full implementation)
                        for action in rec['actions']:
                            if action == 'upvote':
                                can_do, reason = self.state.can_comment()
                                if can_do:
                                    print(f"      ✓ Would upvote post {post.id}")
                                    results['actions_executed'] += 1
                                    # self.client.upvote_post(post.id)  # Uncomment for live
                                    # self.state.record_action('upvote', post.id, True)
                                else:
                                    print(f"      ✗ Skipped: {reason}")

            except moltbook_sdk.MoltbookAPIError as e:
                error_msg = f"Error analyzing {target}: {e}"
                results['errors'].append(error_msg)
                print(f"❌ {error_msg}")

        print(f"\n{'=' * 70}")
        print(f"📈 CAMPAIGN SUMMARY")
        print('=' * 70)
        print(f"Targets Analyzed: {results['targets_analyzed']}")
        print(f"Actions Planned: {results['actions_planned']}")
        print(f"Actions Executed: {results['actions_executed']}")
        if results['errors']:
            print(f"Errors: {len(results['errors'])}")

        return results

    def generate_daily_report(self) -> Dict:
        """Generate a daily campaign report"""
        return {
            'date': self.state.state['day_start'],
            'stats': self.state.state['stats'],
            'rate_limit_status': {
                'can_post': self.state.can_post()[0],
                'can_comment': self.state.can_comment()[0],
                'comments_remaining': RATE_LIMITS['max_comments_per_day'] -
                                     self.state.state['comments_today']
            },
            'recent_actions': self.state.state['completed_actions'][-10:],
            'failed_actions': self.state.state['failed_actions'][-5:]
        }


def plan_campaign(agent_names: List[str], api_key: str):
    """Plan a campaign without executing"""
    campaign = EngagementCampaign(api_key, dry_run=True)

    print(f"\n📋 CAMPAIGN PLANNING MODE")
    print('=' * 70)

    all_recommendations = []

    for agent in agent_names:
        try:
            plan = campaign.analyze_target(agent)
            all_recommendations.extend(plan['recommendations'])

            print(f"\n👤 {agent}")
            print(f"   Karma: {plan['agent'].get('karma', 0)}")
            print(f"   Top opportunities: {len(plan['recommendations'])}")

        except moltbook_sdk.MoltbookAPIError as e:
            print(f"❌ Error: {e}")

    # Overall summary
    all_recommendations.sort(key=lambda x: x['priority_score'], reverse=True)

    print(f"\n{'=' * 70}")
    print(f"🎯 TOP 10 OPPORTUNITIES ACROSS ALL TARGETS")
    print('=' * 70)

    for i, rec in enumerate(all_recommendations[:10], 1):
        post = rec['post']
        print(f"\n{i}. {post.title}")
        print(f"   r/{post.submolt} | ⬆️ {post.upvotes} | 💬 {post.comment_count}")
        print(f"   Priority: {rec['priority_score']:.1f}")
        print(f"   Actions: {', '.join(rec['actions'])}")


def show_campaign_status(api_key: str):
    """Show current campaign status and rate limit info"""
    campaign = EngagementCampaign(api_key)
    report = campaign.generate_daily_report()

    print(f"\n{'=' * 70}")
    print(f"📊 CAMPAIGN STATUS - {report['date']}")
    print('=' * 70)

    print(f"\n📈 Statistics:")
    print(f"  Comments Today: {report['stats']['total_comments']}")
    print(f"  Posts Today: {report['stats']['total_posts']}")
    print(f"  Upvotes Given: {report['stats']['total_upvotes_given']}")

    print(f"\n⏱️  Rate Limits:")
    print(f"  Can Post: {'✅ Yes' if report['rate_limit_status']['can_post'] else '❌ No'}")
    print(f"  Can Comment: {'✅ Yes' if report['rate_limit_status']['can_comment'] else '❌ No'}")
    print(f"  Comments Remaining: {report['rate_limit_status']['comments_remaining']}")

    if report['recent_actions']:
        print(f"\n✅ Recent Actions:")
        for action in report['recent_actions'][-5:]:
            print(f"  {action['type']} on {action['target_id']} - {action['timestamp']}")

    if report['failed_actions']:
        print(f"\n❌ Failed Actions:")
        for action in report['failed_actions']:
            print(f"  {action['type']} on {action['target_id']} - {action['timestamp']}")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Manage automated engagement campaigns'
    )
    parser.add_argument(
        '--mode',
        choices=['plan', 'execute', 'status'],
        default='plan',
        help='Campaign mode'
    )
    parser.add_argument(
        '--targets',
        help='Comma-separated list of target agent names'
    )
    parser.add_argument(
        '--max-actions',
        type=int,
        default=20,
        help='Maximum actions to execute (for --mode execute)'
    )
    parser.add_argument(
        '--live',
        help='Execute live actions (default is dry-run)',
        action='store_true'
    )
    parser.add_argument(
        '--api-key',
        help='Moltbook API key',
        default=os.environ.get('MOLTBOOK_API_KEY')
    )
    parser.add_argument(
        '--state-file',
        help='Campaign state file path',
        default=None
    )

    args = parser.parse_args()

    if args.mode == 'status':
        show_campaign_status(args.api_key)

    elif args.mode == 'plan':
        if not args.targets:
            print("❌ --targets required for planning mode")
            return
        targets = [t.strip() for t in args.targets.split(',')]
        plan_campaign(targets, args.api_key)

    elif args.mode == 'execute':
        if not args.targets:
            print("❌ --targets required for execute mode")
            return
        if not args.api_key:
            print("❌ --api-key required for execute mode")
            return

        targets = [t.strip() for t in args.targets.split(',')]
        campaign = EngagementCampaign(args.api_key, args.state_file)
        campaign.execute_campaign(targets, args.max_actions, dry_run=not args.live)


if __name__ == "__main__":
    main()
