#!/usr/bin/env python3
"""
Smart Poster Demo - Showcasing all features

This demonstrates the capabilities of the Moltbook Smart Poster:
- Template-based post creation
- Quality checking
- Submolt recommendations
- Dry-run posting
- Batch operations

Author: ClaudeCode_GLM4_7
Date: 2026-02-05
"""

import sys
sys.path.insert(0, '/home/sbstndbs/moltbook/work/moltbook-api-recon/tools')

from smart_poster import SmartPoster, PostDraft, POST_TEMPLATES


def print_section(title):
    """Print a section header"""
    print("\n" + "="*60)
    print(title)
    print("="*60)


def demo_templates():
    """Show available templates"""
    print_section("📋 Available Templates")

    for key, tmpl in POST_TEMPLATES.items():
        print(f"\n  • {key:12} - {tmpl['description']}")
        print(f"    Title: {tmpl['title_format']}")


def demo_template_creation():
    """Demonstrate creating a post from template"""
    print_section("🎨 Template Creation Demo")

    poster = SmartPoster()

    # Create a TIL post
    draft = poster.create_from_template(
        'til',
        topic='Moltbook API',
        main_learning='Undocumented endpoints can be discovered via JS reverse engineering',
        context='Found agent profile endpoint by analyzing Next.js bundles',
        resource1='https://www.moltbook.com/api/v1',
        resource2='Project: moltbook-api-recon'
    )

    print(f"\n✓ Created TIL post:")
    print(f"  Title: {draft.title}")
    print(f"  Submolt: {draft.submolt}")
    print(f"  Content preview: {draft.content[:100]}...")


def demo_quality_check():
    """Demonstrate quality checking"""
    print_section("🔍 Quality Check Demo")

    poster = SmartPoster()

    # Good post
    good_draft = PostDraft(
        title="Rust Ownership Explained",
        content="""## What is Ownership?

Ownership is Rust's key feature for memory safety.

### Three Rules
1. Each value has one owner
2. Only one owner at a time
3. Owner is dropped when out of scope

```rust
let s = String::from("hello");  // s owns the string
let s2 = s;                      // s2 now owns it
// s is no longer valid
```

This prevents data races at compile time!""",
        submolt="programming"
    )

    # Bad post
    bad_draft = PostDraft(
        title="Hi",
        content="Short",
        submolt="general"
    )

    print("\n✓ Good Post:")
    report = poster.check_quality(good_draft)
    print(f"  Score: {report.score}/100")
    print(f"  Issues: {report.issues if report.issues else 'None'}")
    print(f"  Suggestions: {len(report.suggestions)}")

    print("\n✗ Bad Post:")
    report = poster.check_quality(bad_draft)
    print(f"  Score: {report.score}/100")
    print(f"  Issues: {', '.join(report.issues)}")


def demo_submolt_recommendations():
    """Demonstrate submolt recommendations"""
    print_section("📁 Submolt Recommendations Demo")

    poster = SmartPoster()

    drafts = [
        PostDraft(
            title="Learning Python async/await",
            content="Python's async programming model explained with examples",
            submolt="general"
        ),
        PostDraft(
            title="My ML project update",
            content="Training progress on my neural network",
            submolt="general"
        ),
        PostDraft(
            title="Building a Rust compiler",
            content="Day 45 of writing a compiler in Rust",
            submolt="general"
        )
    ]

    for draft in drafts:
        report = poster.check_quality(draft)
        print(f"\n  Title: {draft.title}")
        print(f"  Current: r/{draft.submolt}")
        if report.recommended_submolts:
            print(f"  Suggested: {', '.join(set(report.recommended_submolts))}")


def demo_dry_run():
    """Demonstrate dry-run posting"""
    print_section("🔍 Dry-Run Posting Demo")

    poster = SmartPoster()

    draft = PostDraft(
        title="Test Post",
        content="This is a test post in dry-run mode",
        submolt="general"
    )

    result = poster.post_with_fallback(draft, dry_run=True)

    print(f"\n✓ Dry-run complete:")
    print(f"  Success: {result['success']}")
    print(f"  Method: {result['method']}")
    print(f"  Post ID: {result['response']['id']}")
    print(f"  Quality Score: {result['response']['quality_score']}")


def demo_batch_operations():
    """Demonstrate batch posting"""
    print_section("📦 Batch Operations Demo")

    poster = SmartPoster()

    drafts = [
        PostDraft(
            title=f"Batch Post {i}",
            content=f"Content for batch post number {i}",
            submolt="general"
        )
        for i in range(1, 4)
    ]

    print(f"\n✓ Created {len(drafts)} drafts for batch posting")
    print(f"  Delay between posts: 30 minutes (respects rate limits)")

    # Dry-run the batch
    results = poster.post_batch(drafts, dry_run=True)

    print(f"\n✓ Batch dry-run complete:")
    print(f"  Total: {len(results)}")
    print(f"  Successful: {sum(1 for r in results if r['success'])}")


def main():
    """Run all demos"""
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║        🦞 Moltbook Smart Poster - Feature Demo             ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    demo_templates()
    demo_template_creation()
    demo_quality_check()
    demo_submolt_recommendations()
    demo_dry_run()
    demo_batch_operations()

    print_section("✅ Demo Complete")

    print("""
Ready to use Smart Poster!

Try these commands:

  # Interactive wizard
  python tools/smart_poster.py --interactive

  # Quick post
  python tools/smart_poster.py --quick --title "Test" --content "Hello"

  # Template post
  python tools/smart_poster.py --template til

  # Dry-run (test without posting)
  python tools/smart_poster.py --dry-run --title "Test" --content "Testing"

For more info: tools/SMART_POSTER_README.md
    """)


if __name__ == "__main__":
    main()
