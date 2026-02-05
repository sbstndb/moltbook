#!/bin/bash

# Moltbook API Endpoint Tester
# Test the discovered endpoints

API_KEY="${MOLTBOOK_API_KEY}"
BASE_URL="https://www.moltbook.com/api/v1"

if [ -z "$API_KEY" ]; then
    echo "❌ Error: MOLTBOOK_API_KEY environment variable not set"
    echo "Usage: MOLTBOOK_API_KEY=xxx ./test-endpoints.sh"
    exit 1
fi

echo "🦞 Testing Moltbook API Endpoints"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"

    echo -e "${BLUE}Testing: $name${NC}"
    echo "URL: $url"
    echo "Method: $method"

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url" \
            -H "Authorization: Bearer $API_KEY" \
            -H "Content-Type: application/json")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Authorization: Bearer $API_KEY" \
            -H "Content-Type: application/json" \
            -d "$3")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✅ Success ($http_code)${NC}"
        echo "Response preview:"
        echo "$body" | head -c 200
        echo "..."
    else
        echo -e "${RED}❌ Failed ($http_code)${NC}"
        echo "Response: $body"
    fi
    echo ""
}

# 1. Get own profile
test_endpoint "Get Own Profile" \
    "$BASE_URL/agents/me"

# 2. Get agent profile by name
test_endpoint "Get Agent Profile (ClaudeCode_GLM4_7)" \
    "$BASE_URL/agents/profile?name=ClaudeCode_GLM4_7"

# 3. Get agent feed
test_endpoint "Get Agent Feed (ClaudeCode_GLM4_7)" \
    "$BASE_URL/agents/ClaudeCode_GLM4_7/feed?sort=new&limit=10"

# 4. Get agent discovery data
test_endpoint "Get Agent Discovery (ClaudeCode_GLM4_7)" \
    "$BASE_URL/agents/ClaudeCode_GLM4_7/discover"

# 5. Get submolt with posts
test_endpoint "Get Submolt (general)" \
    "$BASE_URL/submolts/general?sort=hot"

# 6. Get global feed
test_endpoint "Get Global Feed" \
    "$BASE_URL/posts?sort=hot&limit=5"

echo "=================================="
echo "✅ Tests complete!"
