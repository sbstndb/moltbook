#!/usr/bin/env python3
"""
Trend Analyzer - Content Intelligence & Growth Analytics

Analyzes Moltbook content for:
- Trending topics across submolts
- Best posting times
- Content quality scoring
- Sentiment analysis
- Growth tracking for agents

Author: ClaudeCode_GLM4_7
Date: 2026-02-05
"""

import sys
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import moltbook_sdk


class ContentAnalyzer:
    """Analyze content for quality, topics, and patterns"""

    # Technical keywords for content scoring
    TECH_KEYWORDS = [
        'api', 'code', 'algorithm', 'optimization', 'performance',
        'async', 'thread', 'memory', 'database', 'protocol', 'rust',
        'python', 'golang', 'javascript', 'docker', 'kubernetes',
        'machine learning', 'ai', 'llm', 'model', 'training'
    ]

    # Quality indicators
    QUALITY_INDICATORS = [
        'tutorial', 'guide', 'how to', 'explained', 'deep dive',
        'analysis', 'benchmark', 'comparison', 'vs', 'versus'
    ]

    @staticmethod
    def extract_keywords(text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """Extract top keywords from text"""
        # Simple word extraction (more sophisticated would use NLP)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())

        # Filter common words
        stopwords = {'this', 'that', 'with', 'from', 'have', 'been', 'they',
                    'their', 'what', 'when', 'where', 'will', 'just', 'like',
                    'more', 'some', 'time', 'only', 'also', 'into', 'than'}

        filtered = [w for w in words if w not in stopwords and len(w) > 3]
        return Counter(filtered).most_common(top_n)

    @staticmethod
    def calculate_content_quality(post: moltbook_sdk.Post) -> Dict:
        """
        Calculate quality score for a post.

        Returns dict with score and breakdown
        """
        score = 0
        factors = []

        # Length factor (substantial content)
        content_len = len(post.content)
        if content_len > 500:
            score += 10
            factors.append('substantial_length')
        elif content_len > 200:
            score += 5
            factors.append('decent_length')

        # Code snippets
        code_snippets = len(re.findall(r'```[a-zA-Z]*\n.*?```', post.content, re.DOTALL))
        if code_snippets >= 2:
            score += 15
            factors.append(f'multiple_code_blocks')
        elif code_snippets >= 1:
            score += 8
            factors.append('has_code')

        # Technical depth
        tech_count = sum(1 for kw in ContentAnalyzer.TECH_KEYWORDS
                        if kw.lower() in post.content.lower())
        if tech_count >= 5:
            score += 15
            factors.append('high_tech_depth')
        elif tech_count >= 2:
            score += 8
            factors.append('some_tech_content')

        # Quality indicators
        quality_count = sum(1 for qi in ContentAnalyzer.QUALITY_INDICATORS
                           if qi.lower() in post.title.lower() or qi.lower() in post.content.lower())
        if quality_count >= 1:
            score += 10
            factors.append('educational_content')

        # Title quality
        if any(c in post.title for c in ['?', ':', '-', '—']):
            score += 5
            factors.append('structured_title')

        return {
            'score': min(score, 100),  # Cap at 100
            'factors': factors,
            'raw_score': score
        }

    @staticmethod
    def estimate_sentiment(text: str) -> str:
        """
        Very basic sentiment estimation.

        Returns: 'positive', 'neutral', 'negative'
        """
        positive_words = ['good', 'great', 'awesome', 'love', 'excellent',
                         'amazing', 'best', 'perfect', 'thanks', 'helpful']
        negative_words = ['bad', 'terrible', 'hate', 'worst', 'awful',
                         'broken', 'wrong', 'error', 'fail', 'issue']

        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'


class TrendDetector:
    """Detect trending topics and patterns across content"""

    def __init__(self):
        self.analyzer = ContentAnalyzer()

    def analyze_submolt_trends(self, client: moltbook_sdk.MoltbookClient,
                               submolts: List[str]) -> Dict[str, Dict]:
        """
        Analyze trending topics across multiple submolts.

        Returns dict with submolt -> trending topics
        """
        trends = {}

        for submolt in submolts:
            try:
                data = client.get_submolt(submolt, sort='hot')
                posts_data = data.get('posts', [])
                posts = [moltbook_sdk.Post.from_dict(p) for p in posts_data]

                # Combine all content
                all_content = ' '.join(p.title + ' ' + p.content for p in posts)
                keywords = self.analyzer.extract_keywords(all_content, top_n=15)

                # Calculate average engagement
                avg_upvotes = sum(p.upvotes for p in posts) / len(posts) if posts else 0
                avg_comments = sum(p.comment_count for p in posts) / len(posts) if posts else 0

                trends[submolt] = {
                    'top_keywords': keywords,
                    'post_count': len(posts),
                    'avg_upvotes': avg_upvotes,
                    'avg_comments': avg_comments,
                    'hot_topics': [kw for kw, _ in keywords[:5]]
                }

            except moltbook_sdk.MoltbookAPIError as e:
                trends[submolt] = {'error': str(e)}

        return trends

    def find_best_posting_times(self, posts: List[moltbook_sdk.Post]) -> Dict:
        """
        Analyze posts to find best times to post.

        Returns dict with hour -> engagement stats
        """
        hourly_stats = defaultdict(lambda: {'upvotes': 0, 'comments': 0, 'count': 0})

        for post in posts:
            try:
                # Parse timestamp
                dt = datetime.fromisoformat(post.created_at.replace('+00:00', ''))
                hour = dt.hour
                day = dt.strftime('%A')

                hourly_stats[hour]['upvotes'] += post.upvotes
                hourly_stats[hour]['comments'] += post.comment_count
                hourly_stats[hour]['count'] += 1
            except (ValueError, AttributeError):
                continue

        # Calculate averages
        hourly_avg = {}
        for hour, stats in hourly_stats.items():
            if stats['count'] > 0:
                hourly_avg[hour] = {
                    'avg_upvotes': stats['upvotes'] / stats['count'],
                    'avg_comments': stats['comments'] / stats['count'],
                    'post_count': stats['count']
                }

        # Find best hours
        sorted_hours = sorted(hourly_avg.items(),
                             key=lambda x: x[1]['avg_upvotes'],
                             reverse=True)

        return {
            'hourly_stats': dict(sorted_hours[:10]),  # Top 10 hours
            'best_hours': [h for h, _ in sorted_hours[:3]],
            'total_analyzed': len(posts)
        }


class GrowthTracker:
    """Track agent growth and benchmark against others"""

    def __init__(self, client: moltbook_sdk.MoltbookClient):
        self.client = client
        self.analyzer = ContentAnalyzer()

    def analyze_agent_growth(self, agent_name: str) -> Dict:
        """
        Analyze an agent's content and growth patterns.

        Returns comprehensive growth analysis
        """
        try:
            profile = self.client.get_agent_profile(agent_name)
            agent = profile.get('agent', {})
            posts_data = profile.get('recentPosts', [])
            posts = [moltbook_sdk.Post.from_dict(p) for p in posts_data]

            # Basic stats
            total_upvotes = sum(p.upvotes for p in posts)
            total_comments = sum(p.comment_count for p in posts)
            avg_quality = sum(self.analyzer.calculate_content_quality(p)['score']
                             for p in posts) / len(posts) if posts else 0

            # Content analysis
            all_content = ' '.join(p.title + ' ' + p.content for p in posts)
            top_keywords = self.analyzer.extract_keywords(all_content)

            # Engagement rate
            engagement_rate = (total_upvotes + total_comments * 2) / len(posts) if posts else 0

            # Best performing posts
            sorted_posts = sorted(posts, key=lambda p: p.upvotes, reverse=True)
            top_posts = sorted_posts[:3]

            return {
                'agent_name': agent_name,
                'karma': agent.get('karma', 0),
                'followers': agent.get('follower_count', 0),
                'total_posts': len(posts),
                'total_upvotes': total_upvotes,
                'total_comments_received': total_comments,
                'avg_quality_score': avg_quality,
                'engagement_rate': engagement_rate,
                'top_keywords': top_keywords,
                'best_posts': [
                    {
                        'title': p.title,
                        'upvotes': p.upvotes,
                        'comments': p.comment_count,
                        'quality_score': self.analyzer.calculate_content_quality(p)['score']
                    }
                    for p in top_posts
                ],
                'submolts_posted_in': list(set(p.submolt for p in posts))
            }

        except moltbook_sdk.MoltbookAPIError as e:
            return {'error': str(e)}

    def benchmark_agents(self, agent_names: List[str]) -> Dict:
        """
        Compare multiple agents across key metrics.

        Returns benchmark analysis
        """
        analyses = {}

        for agent_name in agent_names:
            analyses[agent_name] = self.analyze_agent_growth(agent_name)

        # Calculate rankings
        valid_analyses = {k: v for k, v in analyses.items() if 'error' not in v}

        rankings = {
            'by_karma': sorted(valid_analyses.items(),
                              key=lambda x: x[1]['karma'],
                              reverse=True),
            'by_engagement_rate': sorted(valid_analyses.items(),
                                        key=lambda x: x[1]['engagement_rate'],
                                        reverse=True),
            'by_quality_score': sorted(valid_analyses.items(),
                                      key=lambda x: x[1]['avg_quality_score'],
                                      reverse=True)
        }

        return {
            'analyses': analyses,
            'rankings': rankings,
            'total_agents': len(agent_names)
        }

    def generate_content_recommendations(self, agent_name: str) -> List[str]:
        """
        Generate content recommendations based on agent's performance.

        Returns list of recommendations
        """
        analysis = self.analyze_agent_growth(agent_name)

        if 'error' in analysis:
            return ["Unable to generate recommendations"]

        recommendations = []

        # Quality-based recommendations
        if analysis['avg_quality_score'] < 50:
            recommendations.append(
                "📈 Improve content quality: Add code examples, technical depth, and structured explanations"
            )

        # Engagement-based recommendations
        if analysis['engagement_rate'] < 10:
            recommendations.append(
                "💬 Boost engagement: Ask questions in posts, use compelling titles, post in active submolts"
            )

        # Content variety
        if len(analysis.get('submolts_posted_in', [])) < 3:
            recommendations.append(
                "🔄 Diversify: Try posting in different submolts to reach new audiences"
            )

        # Top keyword suggestions
        if analysis['top_keywords']:
            top_kw = analysis['top_keywords'][0][0]
            recommendations.append(
                f"🎯 Leverage your strength: You have credibility on '{top_kw}' - create more content in this area"
            )

        # Timing recommendations (would need more data)
        recommendations.append(
            "⏰ Experiment with timing: Try posting at different times to find your sweet spot"
        )

        return recommendations


def display_growth_analysis(analysis: Dict):
    """Display growth analysis results"""
    if 'error' in analysis:
        print(f"❌ Error: {analysis['error']}")
        return

    print(f"\n{'=' * 70}")
    print(f"📊 GROWTH ANALYSIS: {analysis['agent_name']}")
    print('=' * 70)

    print(f"\n📈 Key Metrics:")
    print(f"  Karma: {analysis['karma']}")
    print(f"  Followers: {analysis['followers']}")
    print(f"  Total Posts: {analysis['total_posts']}")

    print(f"\n💬 Engagement:")
    print(f"  Total Upvotes: {analysis['total_upvotes']}")
    print(f"  Total Comments: {analysis['total_comments_received']}")
    print(f"  Engagement Rate: {analysis['engagement_rate']:.1f} per post")

    print(f"\n📝 Content Quality:")
    print(f"  Avg Quality Score: {analysis['avg_quality_score']:.1f}/100")

    print(f"\n🔑 Top Topics:")
    for kw, count in analysis['top_keywords'][:5]:
        print(f"  - {kw} ({count} mentions)")

    print(f"\n🏆 Best Performing Posts:")
    for i, post in enumerate(analysis['best_posts'], 1):
        print(f"  {i}. {post['title']}")
        print(f"     ⬆️ {post['upvotes']} | 💬 {post['comments']} | Quality: {post['quality_score']}/100")

    print(f"\n📂 Submolts: {', '.join(analysis.get('submolts_posted_in', []))}")


def display_benchmark(benchmark: Dict):
    """Display benchmark comparison"""
    print(f"\n{'=' * 70}")
    print(f"🏁 AGENT BENCHMARK ({benchmark['total_agents']} agents)")
    print('=' * 70)

    rankings = benchmark['rankings']

    print("\n🥇 By Karma:")
    for i, (name, data) in enumerate(rankings['by_karma'], 1):
        if 'error' not in data:
            print(f"  {i}. {name}: {data['karma']} karma")

    print("\n⚡ By Engagement Rate:")
    for i, (name, data) in enumerate(rankings['by_engagement_rate'][:5], 1):
        if 'error' not in data:
            print(f"  {i}. {name}: {data['engagement_rate']:.1f} avg engagement")

    print("\n✨ By Content Quality:")
    for i, (name, data) in enumerate(rankings['by_quality_score'][:5], 1):
        if 'error' not in data:
            print(f"  {i}. {name}: {data['avg_quality_score']:.1f}/100 quality score")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Analyze Moltbook trends and agent growth'
    )
    parser.add_argument(
        'agents',
        nargs='+',
        help='Agent name(s) to analyze'
    )
    parser.add_argument(
        '--mode',
        choices=['growth', 'benchmark', 'recommend', 'trends'],
        default='growth',
        help='Analysis mode'
    )
    parser.add_argument(
        '--submolts',
        help='Comma-separated list of submolts for trend analysis (for --mode trends)',
        default='buildlogs,general,tech,ai'
    )
    parser.add_argument(
        '--api-key',
        help='Moltbook API key',
        default=os.environ.get('MOLTBOOK_API_KEY')
    )

    args = parser.parse_args()

    client = moltbook_sdk.MoltbookClient(api_key=args.api_key)
    tracker = GrowthTracker(client)

    if args.mode == 'growth':
        for agent in args.agents:
            analysis = tracker.analyze_agent_growth(agent)
            display_growth_analysis(analysis)

    elif args.mode == 'benchmark':
        benchmark = tracker.benchmark_agents(args.agents)
        display_benchmark(benchmark)

    elif args.mode == 'recommend':
        for agent in args.agents:
            print(f"\n📋 Recommendations for {agent}:")
            recommendations = tracker.generate_content_recommendations(agent)
            for rec in recommendations:
                print(f"  {rec}")

    elif args.mode == 'trends':
        detector = TrendDetector()
        submolts = args.submolts.split(',')
        trends = detector.analyze_submolt_trends(client, submolts)

        print("\n🔥 TRENDING TOPICS BY SUBMOLT")
        print('=' * 70)

        for submolt, data in trends.items():
            if 'error' not in data:
                print(f"\nr/{submolt}:")
                print(f"  Posts: {data['post_count']}")
                print(f"  Avg Engagement: ⬆️{data['avg_upvotes']:.1f} | 💬{data['avg_comments']:.1f}")
                print(f"  Hot Topics: {', '.join(data['hot_topics'][:5])}")


if __name__ == "__main__":
    main()
