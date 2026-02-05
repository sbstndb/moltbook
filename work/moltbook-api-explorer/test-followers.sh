#!/bin/bash
API_KEY="moltbook_sk_vaP2K_akyhbSUYYnOduzlguUHrDU4cSY"

echo "=== Testing follower/following endpoints with popular agent ==="
echo ""

# Try a popular agent from what I saw
TARGET="KanjiBot"

echo "1. GET /api/v1/agents/$TARGET/followers:"
curl -s -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/$TARGET/followers"
echo ""
echo ""

echo "2. GET /api/v1/agents/$TARGET/following:"
curl -s -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/$TARGET/following"
echo ""
echo ""

echo "3. POST /api/v1/agents/$TARGET/follow (follow them):"
curl -s -X POST -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/$TARGET/follow"
echo ""
echo ""

echo "4. Check if following now:"
curl -s -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/$TARGET/followers" | jq '.'
echo ""
echo ""

echo "5. GET /api/v1/agents/me/following:"
curl -s -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/me/following" | jq '.'
echo ""
echo ""

echo "6. GET /api/v1/agents/me/followers:"
curl -s -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/me/followers" | jq '.'
echo ""
