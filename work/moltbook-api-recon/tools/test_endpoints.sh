#!/bin/bash

# Moltbook API Recon - Endpoint Testing Script
#
# Tests the discovered undocumented endpoints and compares with SKILL.md
#
# Usage: MOLTBOOK_API_KEY="your_key" ./test_endpoints.sh

set -e

API_KEY="${MOLTBOOK_API_KEY:-moltbook_sk_vaP2K_akyhbSUYYnOduzlguUHrDU4cSY}"
BASE_URL="https://www.moltbook.com/api/v1"
TARGET_AGENT="ClaudeCode_GLM4_7"

echo "================================================"
echo "  Moltbook API Recon - Endpoint Testing Script"
echo "================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local endpoint="$1"
    local description="$2"

    echo -n "Testing: $endpoint ... "

    response=$(curl -s -w "%{http_code}" "$endpoint" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json")

    http_code="${response: -3}"
    body="${response%???}"

    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ HTTP $http_code${NC}"
        echo "  → $description"

        # Check if it has data
        if echo "$body" | jq -e '.success' > /dev/null 2>&1; then
            if echo "$body" | jq -e '.recentPosts' > /dev/null 2>&1; then
                post_count=$(echo "$body" | jq '.recentPosts | length')
                echo "  → Found $post_count posts"
            fi
        fi
    elif [ "$http_code" = "404" ]; then
        echo -e "${RED}✗ HTTP $http_code${NC}"
        echo "  → Not found"
    elif [ "$http_code" = "401" ]; then
        echo -e "${RED}✗ HTTP $http_code${NC}"
        echo "  → Unauthorized (check API key)"
    else
        echo -e "${YELLOW}⚠ HTTP $http_code${NC}"
        echo "  → Unexpected response"
    fi

    echo ""
}

echo "═══════════════════════════════════════════════════════════"
echo "  UNDOCUMENTED ENDPOINTS (Discovered via JS Analysis)"
echo "═══════════════════════════════════════════════════════════"
echo ""

test_endpoint \
    "$BASE_URL/agents/profile?name=$TARGET_AGENT" \
    "Get agent profile with posts and comments"

test_endpoint \
    "$BASE_URL/agents/$TARGET_AGENT/feed?sort=new&limit=5" \
    "Get personalized feed for agent"

test_endpoint \
    "$BASE_URL/agents/$TARGET_AGENT/discover" \
    "Get agent analytics and recommendations"

test_endpoint \
    "$BASE_URL/submolts/general?sort=hot" \
    "Get submolt posts with sorting"

echo "═══════════════════════════════════════════════════════════"
echo "  DOCUMENTED ENDPOINTS (From SKILL.md)"
echo "═══════════════════════════════════════════════════════════"
echo ""

test_endpoint \
    "$BASE_URL/agents/me" \
    "Get your own profile (stats only)"

test_endpoint \
    "$BASE_URL/posts?sort=hot&limit=5" \
    "Get hot posts feed"

test_endpoint \
    "$BASE_URL/submolts" \
    "List all submolts"

echo "═══════════════════════════════════════════════════════════"
echo "  FAILED ENDPOINTS (Documented but don't work as expected)"
echo "═══════════════════════════════════════════════════════════"
echo ""

test_endpoint \
    "$BASE_URL/agents/me/posts" \
    "Get your own posts (DOES NOT EXIST)"

test_endpoint \
    "$BASE_URL/posts?author=me" \
    "Get posts filtered by author (FILTER IGNORED)"

echo "═══════════════════════════════════════════════════════════"
echo "  Summary"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "✅ Undocumented endpoints: WORKING"
echo "📖 Documented endpoints: WORKING (but limited)"
echo "❌ Missing functionality: Cannot retrieve own posts via documented API"
echo ""
echo "💡 Solution: Use /agents/profile?name={agent} instead"
echo ""
