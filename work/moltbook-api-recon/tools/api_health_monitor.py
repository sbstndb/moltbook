#!/usr/bin/env python3
"""
Moltbook API Health Monitor

Monitors undocumented endpoints to detect changes/removals.
Alerts when endpoints stop working or return unexpected data.

Author: ClaudeCode_GLM4_7
Date: 2026-02-05
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any

# Add tools directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import moltbook_sdk


# Undocumented endpoints to monitor
MONITORED_ENDPOINTS = [
    {
        'name': 'Agent Profile (with posts)',
        'endpoint': '/agents/profile?name=ClaudeCode_GLM4_7',
        'critical': True,
        'description': 'Main endpoint for retrieving agent posts'
    },
    {
        'name': 'Agent Feed',
        'endpoint': '/agents/ClaudeCode_GLM4_7/feed',
        'critical': True,
        'description': 'Personalized feed endpoint'
    },
    {
        'name': 'Agent Discover',
        'endpoint': '/agents/ClaudeCode_GLM4_7/discover',
        'critical': False,
        'description': 'Analytics and recommendations'
    },
    {
        'name': 'Submolt with sorting',
        'endpoint': '/submolts/general?sort=hot',
        'critical': True,
        'description': 'Submolt posts with sort parameter'
    }
]


class HealthCheckResult:
    """Result of a single health check"""

    def __init__(self, endpoint_info: Dict[str, Any]):
        self.info = endpoint_info
        self.status = None  # 'ok', 'failed', 'degraded'
        self.response_time = None
        self.error = None
        self.data = None
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.info['name'],
            'endpoint': self.info['endpoint'],
            'critical': self.info['critical'],
            'status': self.status,
            'response_time': self.response_time,
            'error': str(self.error) if self.error else None,
            'timestamp': self.timestamp
        }


def check_endpoint(client: moltbook_sdk.MoltbookClient, endpoint_info: Dict[str, Any]) -> HealthCheckResult:
    """
    Check a single endpoint's health.

    Args:
        client: MoltbookClient instance
        endpoint_info: Endpoint configuration dict

    Returns:
        HealthCheckResult with status
    """
    result = HealthCheckResult(endpoint_info)

    try:
        import time
        start = time.time()

        # Make request
        endpoint_path = endpoint_info['endpoint']
        data = client._request(endpoint_path)

        result.response_time = round((time.time() - start) * 1000, 2)  # ms
        result.data = data

        # Check response structure
        if data.get('success'):
            result.status = 'ok'
        else:
            result.status = 'degraded'
            result.error = "Response indicates failure"

    except moltbook_sdk.MoltbookAPIError as e:
        result.status = 'failed'
        result.error = str(e)

    except Exception as e:
        result.status = 'failed'
        result.error = f"Unexpected error: {e}"

    return result


def run_health_check(api_key: str = None, save_to_file: bool = True) -> List[HealthCheckResult]:
    """
    Run health checks on all monitored endpoints.

    Args:
        api_key: Optional API key
        save_to_file: Whether to save results to JSON file

    Returns:
        List of HealthCheckResult objects
    """
    print("🔍 Moltbook API Health Monitor")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Monitoring {len(MONITORED_ENDPOINTS)} endpoints\n")

    client = moltbook_sdk.MoltbookClient(api_key=api_key)
    results = []

    for endpoint_info in MONITORED_ENDPOINTS:
        result = check_endpoint(client, endpoint_info)
        results.append(result)

        # Display result
        status_icon = {
            'ok': '✅',
            'degraded': '⚠️',
            'failed': '❌'
        }.get(result.status, '❓')

        print(f"{status_icon} {result.info['name']}")
        print(f"   Endpoint: {result.info['endpoint']}")
        print(f"   Status: {result.status.upper()}")

        if result.response_time:
            print(f"   Response time: {result.response_time}ms")

        if result.error:
            print(f"   Error: {result.error}")

        if result.data and result.status == 'ok':
            # Quick data validation
            if 'recentPosts' in result.data:
                post_count = len(result.data.get('recentPosts', []))
                print(f"   Posts returned: {post_count}")
            if 'agent' in result.data:
                agent_name = result.data.get('agent', {}).get('name', 'N/A')
                print(f"   Agent: {agent_name}")

        print()

    # Summary
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    ok_count = sum(1 for r in results if r.status == 'ok')
    failed_count = sum(1 for r in results if r.status == 'failed')
    degraded_count = sum(1 for r in results if r.status == 'degraded')

    print(f"✅ OK: {ok_count}/{len(results)}")
    print(f"❌ Failed: {failed_count}/{len(results)}")
    print(f"⚠️  Degraded: {degraded_count}/{len(results)}")

    # Critical failures
    critical_failures = [
        r for r in results
        if r.status in ['failed', 'degraded'] and r.info['critical']
    ]

    if critical_failures:
        print("\n🚨 CRITICAL FAILURES:")
        for r in critical_failures:
            print(f"   - {r.info['name']}: {r.error}")
    else:
        print("\n✅ All critical endpoints operational")

    # Save results
    if save_to_file:
        save_results(results)

    return results


def save_results(results: List[HealthCheckResult]):
    """Save health check results to JSON file"""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')

    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    # Save to timestamped file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'health_check_{timestamp}.json')

    with open(log_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': [r.to_dict() for r in results],
            'summary': {
                'total': len(results),
                'ok': sum(1 for r in results if r.status == 'ok'),
                'failed': sum(1 for r in results if r.status == 'failed'),
                'degraded': sum(1 for r in results if r.status == 'degraded')
            }
        }, f, indent=2)

    print(f"\n📝 Results saved to: {log_file}")


def compare_with_previous(current_results: List[HealthCheckResult]) -> bool:
    """
    Compare current results with previous health check log.

    Returns True if there are any changes (new failures).
    """
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')

    if not os.path.exists(log_dir):
        return False

    # Find most recent log file
    log_files = sorted([
        f for f in os.listdir(log_dir)
        if f.startswith('health_check_') and f.endswith('.json')
    ], reverse=True)

    if len(log_files) < 2:  # Need at least 2 files to compare
        return False

    # Load previous results (second most recent)
    previous_file = os.path.join(log_dir, log_files[1])

    try:
        with open(previous_file, 'r') as f:
            previous_data = json.load(f)

        # Compare statuses
        previous_statuses = {
            r['endpoint']: r['status']
            for r in previous_data['results']
        }

        changes = []
        for current in current_results:
            prev_status = previous_statuses.get(current.info['endpoint'])
            if prev_status and prev_status != current.status:
                changes.append({
                    'endpoint': current.info['name'],
                    'from': prev_status,
                    'to': current.status
                })

        if changes:
            print("\n🔄 CHANGES DETECTED:")
            for change in changes:
                print(f"   {change['endpoint']}: {change['from']} → {change['to']}")
            return True

        return False

    except Exception as e:
        print(f"\n⚠️  Could not compare with previous run: {e}")
        return False


def continuous_monitor(interval_minutes: int = 30, api_key: str = None):
    """
    Run continuous monitoring with specified interval.

    Args:
        interval_minutes: Minutes between checks
        api_key: Optional API key
    """
    import time

    print(f"🔄 Starting continuous monitoring (interval: {interval_minutes} min)")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            run_health_check(api_key=api_key, save_to_file=True)

            print(f"\n⏰ Next check in {interval_minutes} minutes...")
            print("Press Ctrl+C to stop\n")

            time.sleep(interval_minutes * 60)

    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Monitor Moltbook API endpoint health'
    )
    parser.add_argument(
        '--api-key',
        help='Moltbook API key (optional)',
        default=None
    )
    parser.add_argument(
        '--no-save',
        help='Do not save results to file',
        action='store_true'
    )
    parser.add_argument(
        '--continuous',
        help='Run continuous monitoring',
        action='store_true'
    )
    parser.add_argument(
        '--interval',
        help='Minutes between checks (for continuous mode)',
        type=int,
        default=30
    )

    args = parser.parse_args()

    if args.continuous:
        continuous_monitor(args.interval, args.api_key)
    else:
        run_health_check(api_key=args.api_key, save_to_file=not args.no_save)


if __name__ == "__main__":
    main()
