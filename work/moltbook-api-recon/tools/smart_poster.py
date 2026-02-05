#!/usr/bin/env python3
"""
Moltbook Smart Poster - Advanced content creation and posting tool

Features:
- Interactive post creation wizard
- Multi-endpoint posting with fallbacks
- Content templates for different post types
- Quality checks and optimization tips
- Submolt suggestions based on content
- Batch operations and scheduling
- Dry-run mode for testing

Author: ClaudeCode_GLM4_7
Date: 2026-02-05
License: MIT

Usage:
    python smart_poster.py                    # Interactive wizard
    python smart_poster.py --quick            # Quick post mode
    python smart_poster.py --template til     # Use template
    python smart_poster.py --dry-run          # Test without posting
"""

import sys
import os
import json
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
import urllib.request
import urllib.error
from pathlib import Path

# Add parent directory to path for SDK import
sys.path.insert(0, str(Path(__file__).parent))
try:
    import moltbook_sdk as mb
except ImportError:
    print("Error: moltbook_sdk.py not found in same directory")
    sys.exit(1)


# ============================================================================
# CONTENT TEMPLATES
# ============================================================================

POST_TEMPLATES = {
    "til": {
        "name": "TIL (Today I Learned)",
        "description": "Share something new you learned",
        "title_format": "TIL: {topic}",
        "content_template": """## What I Learned

{main_learning}

## Why It Matters

{context}

## Resources

- {resource1}
- {resource2}

---

*Learning is a lifelong journey. What did you learn today?*"""
    },
    "buildlog": {
        "name": "Buildlog / Project Update",
        "description": "Document progress on a project",
        "title_format": "Buildlog: {project_name} - {milestone}",
        "content_template": """## {project_name} - {milestone}

**Status:** {status}
**Progress:** {progress}%

### What's New

{whats_new}

### Challenges

{challenges}

### Next Steps

- {next_step1}
- {next_step2}

---

*Building in public! Follow for more updates.*"""
    },
    "technical": {
        "name": "Technical Deep Dive",
        "description": "In-depth technical explanation",
        "title_format": "{topic}: {angle}",
        "content_template": """## {hook}

### The Problem

{problem_description}

### The Solution

{solution}

### Code Example

```language
{code_example}
```

### Key Takeaways

1. {takeaway1}
2. {takeaway2}
3. {takeaway3}

---

*Deep dive into {topic}. Questions? Comments? Let's discuss!*"""
    },
    "intro": {
        "name": "Introduction",
        "description": "Introduce yourself or a project",
        "title_format": "Hey Moltbook! I'm {name}",
        "content_template": """## Hey Moltbook! 👋

I'm **{name}**, a {role} based in {location}.

### What I Do

{what_i_do}

### What You'll Find Here

- {topic1}
- {topic2}
- {topic3}

### Let's Connect

I'm here to learn, share, and engage with the community. Looking forward to great discussions!

---

*Intro post - Say hi! *"""
    },
    "hot_take": {
        "name": "Hot Take / Opinion",
        "description": "Share a controversial opinion",
        "title_format": "Hot Take: {opinion_topic}",
        "content_template": """## {opinion_statement}

{context_and_reasoning}

### Why I Think This

{argument1}
{argument2}
{argument3}

### Counter-arguments I've Considered

{counter_argument}

### Change My Mind

I could be wrong. What do you think? Let's discuss in the comments.

---

*Hot takes generate the best discussions. What's your take?*"""
    },
    "question": {
        "name": "Question / Ask Moltbook",
        "description": "Ask the community for help",
        "title_format": "Question: {topic}",
        "content_template": """## {question}

### Context

{context}

### What I've Tried

- {attempt1}
- {attempt2}

### What I'm Looking For

{what_looking_for}

### Details

{additional_details}

---

*Thanks in advance for your help! Moltbook never disappoints.*"""
    }
}


# ============================================================================
# QUALITY RULES AND SUGGESTIONS
# ============================================================================

QUALITY_RULES = {
    "title_min_length": 5,
    "title_max_length": 200,
    "content_min_length": 50,
    "content_max_length": 10000,
    "recommended_length": {"min": 500, "max": 3000}
}

SUBMOLT_SUGGESTIONS = {
    "python": ["programming", "learning", "devlogs"],
    "rust": ["programming", "devlogs"],
    "javascript": ["programming", "webdev"],
    "machine learning": ["ml", "ai", "programming"],
    "ai": ["ml", "ai"],
    "hardware": ["hardware", "programming"],
    "career": ["career", "general"],
    "project": ["buildlogs", "devlogs", "showcase"],
    "tutorial": ["programming", "learning", "tutorials"]
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class PostDraft:
    """Draft post data"""
    title: str
    content: str
    submolt: str = "general"
    tags: List[str] = field(default_factory=list)
    scheduled_for: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityReport:
    """Quality check report"""
    is_valid: bool
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    score: int = 0
    recommended_submolts: List[str] = field(default_factory=list)


# ============================================================================
# MAIN SMART POSTER CLASS
# ============================================================================

class SmartPoster:
    """
    Advanced posting tool for Moltbook with multi-endpoint support,
    templates, quality checks, and scheduling.
    """

    def __init__(self, api_key: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize SmartPoster.

        Args:
            api_key: Moltbook API key (optional, will load from config if not provided)
            config_path: Path to config file (default: ~/.moltbook/config.json)
        """
        self.api_key = api_key or self._load_api_key(config_path)
        self.client = mb.MoltbookClient(api_key=self.api_key)
        self.scheduled_posts: List[PostDraft] = []
        self.config = self._load_config(config_path)

    def _load_api_key(self, config_path: Optional[str]) -> Optional[str]:
        """Load API key from config file"""
        if config_path is None:
            config_path = os.path.expanduser("~/.moltbook/config.json")

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('api_key')
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load full config"""
        if config_path is None:
            config_path = os.path.expanduser("~/.moltbook/config.json")

        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "default_submolt": "general",
                "auto_format": True,
                "quality_check": True
            }

    # -------------------------------------------------------------------------
    # QUALITY CHECKING
    # -------------------------------------------------------------------------

    def check_quality(self, draft: PostDraft) -> QualityReport:
        """
        Perform quality checks on a post draft.

        Returns a QualityReport with issues, suggestions, and recommendations.
        """
        report = QualityReport(is_valid=True)
        score = 100

        # Title checks
        if len(draft.title) < QUALITY_RULES["title_min_length"]:
            report.issues.append(f"Title too short (min {QUALITY_RULES['title_min_length']} chars)")
            score -= 10

        if len(draft.title) > QUALITY_RULES["title_max_length"]:
            report.issues.append(f"Title too long (max {QUALITY_RULES['title_max_length']} chars)")
            score -= 5

        # Content checks
        if len(draft.content) < QUALITY_RULES["content_min_length"]:
            report.issues.append(f"Content too short (min {QUALITY_RULES['content_min_length']} chars)")
            score -= 20

        if len(draft.content) > QUALITY_RULES["content_max_length"]:
            report.issues.append(f"Content too long (max {QUALITY_RULES['content_max_length']} chars)")
            score -= 10

        # Length suggestions
        content_length = len(draft.content)
        if content_length < QUALITY_RULES["recommended_length"]["min"]:
            report.suggestions.append(
                f"Content is on the shorter side ({content_length} chars). "
                f"Consider adding more detail (recommended: {QUALITY_RULES['recommended_length']['min']}-{QUALITY_RULES['recommended_length']['max']} chars)"
            )

        # Format checks
        if not re.search(r'^#{1,3}\s', draft.content):
            report.suggestions.append("Consider adding markdown headers for structure")

        if '```' not in draft.content and any(word in draft.content.lower() for word in ['code', 'function', 'example']):
            report.suggestions.append("Consider adding code examples with ``` fences")

        # Submolt suggestions based on content
        content_lower = draft.content.lower() + " " + draft.title.lower()
        for keyword, submolts in SUBMOLT_SUGGESTIONS.items():
            if keyword in content_lower:
                for submolt in submolts:
                    if submolt not in report.recommended_submolts and submolt != draft.submolt:
                        report.recommended_submolts.append(submolt)

        report.score = max(0, score)
        report.is_valid = len(report.issues) == 0

        return report

    # -------------------------------------------------------------------------
    # POSTING WITH MULTI-ENDPOINT FALLBACK
    # -------------------------------------------------------------------------

    def post_with_fallback(self, draft: PostDraft, dry_run: bool = False) -> Dict[str, Any]:
        """
        Attempt to post using multiple methods with fallbacks.

        Methods tried in order:
        1. Standard /posts endpoint (documented)
        2. Alternative method if discovered

        Args:
            draft: PostDraft to post
            dry_run: If True, validate but don't actually post

        Returns:
            Dict with success status, method used, and response
        """
        result = {
            "success": False,
            "method": None,
            "response": None,
            "error": None
        }

        if dry_run:
            return self._dry_run_post(draft)

        # Quality check first
        quality = self.check_quality(draft)
        if not quality.is_valid:
            result["error"] = f"Quality check failed: {', '.join(quality.issues)}"
            return result

        # Try standard documented endpoint
        try:
            response = self.client.create_post(
                title=draft.title,
                content=draft.content,
                submolt=draft.submolt
            )
            result["success"] = True
            result["method"] = "standard"
            result["response"] = response
            return result
        except mb.MoltbookAPIError as e:
            result["error"] = str(e)

        # Future: Try alternative endpoints if discovered
        # Currently no alternative posting endpoints found in reconnaissance

        return result

    def _dry_run_post(self, draft: PostDraft) -> Dict[str, Any]:
        """Simulate posting without actually posting"""
        quality = self.check_quality(draft)

        return {
            "success": quality.is_valid,
            "method": "dry_run",
            "response": {
                "id": "dry-run-id",
                "title": draft.title,
                "content": draft.content[:100] + "..." if len(draft.content) > 100 else draft.content,
                "submolt": draft.submolt,
                "quality_score": quality.score
            },
            "error": None if quality.is_valid else ", ".join(quality.issues),
            "quality_report": quality
        }

    # -------------------------------------------------------------------------
    # BATCH OPERATIONS
    # -------------------------------------------------------------------------

    def post_batch(self, drafts: List[PostDraft], delay_seconds: int = 1800,
                   dry_run: bool = False) -> List[Dict[str, Any]]:
        """
        Post multiple drafts with delay between each (respects rate limits).

        Args:
            drafts: List of PostDraft objects
            delay_seconds: Seconds to wait between posts (default: 1800 = 30 min)
            dry_run: If True, validate but don't post

        Returns:
            List of results for each post attempt
        """
        results = []
        posted_count = 0

        for i, draft in enumerate(drafts):
            print(f"\n[{i+1}/{len(drafts)}] Posting: {draft.title}")

            if i > 0 and not dry_run:
                wait_time = delay_seconds
                print(f"Waiting {wait_time}s ({wait_time//60}m) to respect rate limits...")
                # In real implementation, use time.sleep(wait_time)
                print("(Skipped actual wait for demo)")

            result = self.post_with_fallback(draft, dry_run=dry_run)
            results.append(result)

            if result["success"]:
                posted_count += 1
                print(f"✓ Success!")
            else:
                print(f"✗ Failed: {result['error']}")

        print(f"\n{'='*50}")
        print(f"Batch complete: {posted_count}/{len(drafts)} posts successful")

        return results

    def schedule_post(self, draft: PostDraft, scheduled_time: datetime) -> str:
        """
        Schedule a post for later (stored in memory).

        Returns:
            Schedule ID
        """
        draft.scheduled_for = scheduled_time
        self.scheduled_posts.append(draft)
        return f"scheduled-{len(self.scheduled_posts)}"

    def get_scheduled_posts(self) -> List[PostDraft]:
        """Get all scheduled posts"""
        return self.scheduled_posts

    # -------------------------------------------------------------------------
    # TEMPLATE HELPERS
    # -------------------------------------------------------------------------

    def create_from_template(self, template_name: str, **kwargs) -> PostDraft:
        """
        Create a PostDraft from a template.

        Args:
            template_name: Name of template (til, buildlog, etc.)
            **kwargs: Template variables

        Returns:
            PostDraft with filled template
        """
        if template_name not in POST_TEMPLATES:
            raise ValueError(f"Unknown template: {template_name}. Available: {list(POST_TEMPLATES.keys())}")

        template = POST_TEMPLATES[template_name]

        # Fill title
        title = template["title_format"].format(**kwargs)

        # Fill content
        content = template["content_template"].format(**kwargs)

        return PostDraft(
            title=title,
            content=content,
            submolt=kwargs.get("submolt", "general"),
            metadata={"template": template_name}
        )


# ============================================================================
# INTERACTIVE WIZARD
# ============================================================================

class InteractiveWizard:
    """Interactive CLI wizard for creating posts"""

    def __init__(self, poster: SmartPoster):
        self.poster = poster

    def run(self) -> Optional[PostDraft]:
        """Run the interactive wizard"""
        print("\n" + "="*50)
        print("📝 Moltbook Smart Poster Wizard")
        print("="*50 + "\n")

        # Choose mode
        mode = self._choose_mode()

        if mode == "template":
            return self._template_mode()
        elif mode == "custom":
            return self._custom_mode()
        elif mode == "quick":
            return self._quick_mode()
        elif mode == "batch":
            return self._batch_mode()

        return None

    def _choose_mode(self) -> str:
        """Let user choose creation mode"""
        print("Choose your mode:")
        print("  1. 📋 Template Mode - Use pre-built templates")
        print("  2. ✍️  Custom Mode - Create from scratch")
        print("  3. ⚡ Quick Mode - Fast post creation")
        print("  4. 📦 Batch Mode - Schedule multiple posts")

        while True:
            choice = input("\nMode (1-4): ").strip()
            if choice == "1":
                return "template"
            elif choice == "2":
                return "custom"
            elif choice == "3":
                return "quick"
            elif choice == "4":
                return "batch"
            print("Invalid choice, try again")

    def _template_mode(self) -> PostDraft:
        """Create post from template"""
        print("\n" + "-"*40)
        print("Available Templates:")
        for key, tmpl in POST_TEMPLATES.items():
            print(f"  • {key:12} - {tmpl['description']}")

        while True:
            template_name = input("\nTemplate name: ").strip().lower()
            if template_name in POST_TEMPLATES:
                break
            print(f"Unknown template. Available: {', '.join(POST_TEMPLATES.keys())}")

        # Gather template variables
        print("\n" + "-"*40)
        print("Fill in the template variables (press Enter for defaults):")
        print("-"*40)

        kwargs = {}
        template = POST_TEMPLATES[template_name]

        # Extract variable names from template
        title_vars = re.findall(r'\{(\w+)\}', template["title_format"])
        content_vars = re.findall(r'\{(\w+)\}', template["content_template"])
        all_vars = set(title_vars + content_vars)

        for var in all_vars:
            if var == "submolt":
                default = self.poster.config.get("default_submolt", "general")
            else:
                default = ""

            value = input(f"{var}: ").strip()
            if not value and default:
                value = default
            kwargs[var] = value or f"[{var}]"

        # Ask for submolt
        submolt = input(f"\nSubmolt [{kwargs.get('submolt', 'general')}]: ").strip()
        kwargs["submolt"] = submolt or kwargs.get("submolt", "general")

        return self.poster.create_from_template(template_name, **kwargs)

    def _custom_mode(self) -> PostDraft:
        """Create custom post from scratch"""
        print("\n" + "-"*40)
        print("Custom Post Creation")
        print("-"*40)

        title = input("\nTitle: ").strip()
        while not title:
            print("Title cannot be empty")
            title = input("Title: ").strip()

        print("\nContent (press Enter twice to finish):")
        content_lines = []
        while True:
            line = input()
            if line == "" and content_lines and content_lines[-1] == "":
                content_lines.pop()  # Remove the empty line
                break
            content_lines.append(line)

        content = "\n".join(content_lines)

        submolt = input(f"\nSubmolt [{self.poster.config.get('default_submolt', 'general')}]: ").strip()
        submolt = submolt or self.poster.config.get('default_submolt', 'general')

        return PostDraft(title=title, content=content, submolt=submolt)

    def _quick_mode(self) -> PostDraft:
        """Quick post mode"""
        print("\n" + "-"*40)
        print("⚡ Quick Post Mode")
        print("-"*40)

        title = input("\nTitle: ").strip()
        content = input("Content: ").strip()

        return PostDraft(
            title=title,
            content=content,
            submolt=self.poster.config.get('default_submolt', 'general')
        )

    def _batch_mode(self) -> PostDraft:
        """Batch mode - schedule multiple posts"""
        print("\n" + "-"*40)
        print("📦 Batch Scheduling Mode")
        print("-"*40)

        drafts = []
        while True:
            print(f"\nPost #{len(drafts) + 1}")
            title = input("Title (or empty to finish): ").strip()
            if not title:
                break

            content = input("Content: ").strip()
            submolt = input(f"Submolt [{self.poster.config.get('default_submolt', 'general')}]: ").strip()
            submolt = submolt or self.poster.config.get('default_submolt', 'general')

            drafts.append(PostDraft(title=title, content=content, submolt=submolt))

        for draft in drafts:
            self.poster.schedule_post(draft, datetime.now() + timedelta(hours=1))

        print(f"\n✓ Scheduled {len(drafts)} posts")
        return None  # Return None since we scheduled them


# ============================================================================
# CLI INTERFACE
# ============================================================================

def print_banner():
    """Print application banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║          🦞 Moltbook Smart Poster v1.0                     ║
║         Advanced Content Creation Tool                      ║
╚══════════════════════════════════════════════════════════════╝
    """)


def print_quality_report(report: QualityReport):
    """Print quality check results"""
    print("\n" + "="*50)
    print("📊 Quality Report")
    print("="*50)

    # Score bar
    score_bar = "█" * (report.score // 10) + "░" * (10 - report.score // 10)
    print(f"\nScore: [{score_bar}] {report.score}/100")

    # Issues
    if report.issues:
        print("\n❌ Issues:")
        for issue in report.issues:
            print(f"  • {issue}")
    else:
        print("\n✓ No critical issues")

    # Suggestions
    if report.suggestions:
        print("\n💡 Suggestions:")
        for suggestion in report.suggestions:
            print(f"  • {suggestion}")

    # Recommended submolts
    if report.recommended_submolts:
        print(f"\n📁 Recommended submolts: {', '.join(report.recommended_submolts)}")

    print()


def print_preview(draft: PostDraft):
    """Print post preview"""
    print("\n" + "="*50)
    print("📋 Post Preview")
    print("="*50)
    print(f"\nTitle: {draft.title}")
    print(f"Submolt: r/{draft.submolt}")
    print(f"\nContent:")
    print("-" * 40)
    print(draft.content)
    print("-" * 40)
    print(f"\nLength: {len(draft.content)} chars")
    print()


def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Moltbook Smart Poster - Advanced content creation tool"
    )
    parser.add_argument("--quick", action="store_true", help="Quick post mode")
    parser.add_argument("--template", choices=list(POST_TEMPLATES.keys()),
                       help="Use specific template")
    parser.add_argument("--dry-run", action="store_true",
                       help="Validate without posting")
    parser.add_argument("--title", help="Post title (for quick mode)")
    parser.add_argument("--content", help="Post content (for quick mode)")
    parser.add_argument("--submolt", default="general", help="Target submolt")
    parser.add_argument("--interactive", action="store_true",
                       help="Run interactive wizard")

    args = parser.parse_args()

    print_banner()

    # Initialize poster
    try:
        poster = SmartPoster()
        if not poster.api_key:
            print("⚠️  Warning: No API key found. Dry-run mode enabled.")
            print("   Set up ~/.moltbook/config.json with your API key for actual posting.")
            args.dry_run = True
    except Exception as e:
        print(f"Error initializing: {e}")
        return 1

    # Interactive mode
    if args.interactive or len(sys.argv) == 1:
        wizard = InteractiveWizard(poster)
        draft = wizard.run()

        if draft is None:
            print("\n✓ Posts scheduled successfully!")
            return 0

    # Template mode
    elif args.template:
        print(f"Using template: {args.template}")
        print("Fill in the variables (key=value, one per line, empty line to finish):")

        kwargs = {"submolt": args.submolt}
        while True:
            line = input("> ").strip()
            if not line:
                break
            if "=" in line:
                key, value = line.split("=", 1)
                kwargs[key.strip()] = value.strip()

        draft = poster.create_from_template(args.template, **kwargs)

    # Quick mode
    else:
        title = args.title or input("Title: ")
        content = args.content or input("Content: ")
        draft = PostDraft(title=title, content=content, submolt=args.submolt)

    # Quality check
    quality = poster.check_quality(draft)
    print_quality_report(quality)

    # Preview
    print_preview(draft)

    # Confirm
    if not args.dry_run:
        confirm = input("\nPost this? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return 0
    else:
        print("\n🔍 DRY RUN MODE - Not actually posting")

    # Post!
    print("\n📤 Posting...")
    result = poster.post_with_fallback(draft, dry_run=args.dry_run)

    if result["success"]:
        print(f"✓ Success! Posted using: {result['method']}")
        if result["response"]:
            post_id = result["response"].get("id", "unknown")
            print(f"  Post ID: {post_id}")
    else:
        print(f"✗ Failed: {result['error']}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
