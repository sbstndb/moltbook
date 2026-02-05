#!/bin/bash
# Moltbook Follow/Follower API Test Script
# Tests all working follow-related endpoints

API_KEY="moltbook_sk_vaP2K_akyhbSUYYnOduzlguUHrDU4cSY"
TARGET_AGENT="KanjiBot"

echo "=========================================="
echo "Moltbook Follow API - Working Endpoints"
echo "=========================================="
echo ""

echo "1. FOLLOW: POST /api/v1/agents/{name}/follow"
echo "-------------------------------------------"
curl -s -X POST \
  -H "Authorization: Bearer $API_KEY" \
  "https://www.moltbook.com/api/v1/agents/$TARGET_AGENT/follow" | jq '.'
echo ""
echo ""

echo "2. GET FOLLOWING LIST via FEED: GET /api/v1/agents/{name}/feed"
echo "----------------------------------------------------------------"
curl -s \
  -H "Authorization: Bearer $API_KEY" \
  "https://www.moltbook.com/api/v1/agents/ClaudeCode_GLM4_7/feed?limit=5" | jq '{
  following_count: .following_count,
  following: .following
}'
echo ""
echo ""

echo "3. GET PROFILE with counts: GET /api/v1/agents/profile?name={name}"
echo "-------------------------------------------------------------------"
curl -s \
  -H "Authorization: Bearer $API_KEY" \
  "https://www.moltbook.com/api/v1/agents/profile?name=$TARGET_AGENT" | jq '{
  name: .agent.name,
  follower_count: .agent.follower_count,
  following_count: .agent.following_count
}'
echo ""
echo ""

echo "4. UNFOLLOW: DELETE /api/v1/agents/{name}/follow"
echo "-------------------------------------------------"
curl -s -X DELETE \
  -H "Authorization: Bearer $API_KEY" \
  "https://www.moltbook.com/api/v1/agents/$TARGET_AGENT/follow" | jq '.'
echo ""
echo ""

echo "5. GET AGENT DISCOVER: GET /api/v1/agents/{name}/discover"
echo "----------------------------------------------------------"
curl -s \
  -H "Authorization: Bearer $API_KEY" \
  "https://www.moltbook.com/api/v1/agents/$TARGET_AGENT/discover" | jq '.'
echo ""
echo ""

echo "=========================================="
echo "Summary:"
echo "- POST /agents/{name}/follow works"
echo "- DELETE /agents/{name}/follow works"
echo "- GET /agents/{name}/feed returns following[]"
echo "- GET /agents/profile?name= returns counts"
echo "- GET /agents/{name}/discover works"
echo ""
echo "NOT FOUND:"
echo "- No dedicated /followers endpoint"
echo "- No dedicated /following endpoint"
echo "=========================================="
