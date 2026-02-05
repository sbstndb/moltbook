#!/bin/bash
API_KEY="moltbook_sk_vaP2K_akyhbSUYYnOduzlguUHrDU4cSY"

echo "=== Testing alternative patterns ==="
echo ""

echo "1. GET /api/v1/agents/me (full profile):"
curl -s -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/me" | jq '.'
echo ""
echo ""

echo "2. GET /api/v1/agents/me/following:"
curl -s -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/me/following" | jq '.'
echo ""
echo ""

echo "3. GET /api/v1/agents/me/followers:"
curl -s -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/me/followers" | jq '.'
echo ""
echo ""

echo "4. POST /api/v1/follow (with body):"
curl -s -X POST -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" -d '{"target":"KanjiBot"}' "https://www.moltbook.com/api/v1/follow" | jq '.'
echo ""
echo ""

echo "5. POST /api/v1/agents/me/follow (with body):"
curl -s -X POST -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" -d '{"target":"KanjiBot"}' "https://www.moltbook.com/api/v1/agents/me/follow" | jq '.'
echo ""
echo ""

echo "6. Follow via /api/v1/agents/KanjiBot/follow:"
curl -s -X POST -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/KanjiBot/follow" | jq '.'
echo ""
echo ""

echo "7. Check following status via /api/v1/agents/me:"
curl -s -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/me" | jq '.following_count, .follower_count'
echo ""
