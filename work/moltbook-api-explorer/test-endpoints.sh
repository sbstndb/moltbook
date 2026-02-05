#!/bin/bash
API_KEY="moltbook_sk_vaP2K_akyhbSUYYnOduzlguUHrDU4cSY"
TARGET="ClaudeCode_GLM4_7"

echo "=== Testing Discovered Endpoints ==="
echo ""
echo "1. Agent Profile:"
curl -s -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/profile?name=$TARGET" | jq '.'
echo ""
echo "2. Agent Discover:"
curl -s -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/$TARGET/discover" | jq '.'
echo ""
echo "3. Agent Feed:"
curl -s -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/$TARGET/feed" | jq '.'
echo ""
echo "=== Testing Follow Endpoint Guesses ==="
echo ""
echo "4. GET /api/v1/agents/{name}/followers:"
curl -s -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/$TARGET/followers" | jq '.'
echo ""
echo "5. GET /api/v1/agents/{name}/following:"
curl -s -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/$TARGET/following" | jq '.'
echo ""
echo "6. POST /api/v1/agents/{name}/follow:"
curl -s -X POST -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/$TARGET/follow" | jq '.'
echo ""
echo "7. DELETE /api/v1/agents/{name}/follow:"
curl -s -X DELETE -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/$TARGET/follow" | jq '.'
echo ""
echo "8. POST /api/v1/agents/{name}/unfollow:"
curl -s -X POST -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/$TARGET/unfollow" | jq '.'
echo ""
echo "9. GET /api/v1/agents/{name}/subscribers:"
curl -s -H "Authorization: Bearer $API_KEY" "https://www.moltbook.com/api/v1/agents/$TARGET/subscribers" | jq '.'
