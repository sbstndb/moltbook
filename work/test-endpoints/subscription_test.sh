#!/bin/bash

API_KEY="moltbook_sk_vaP2K_akyhbSUYYnOduzlguUHrDU4cSY"
BASE_URL="https://www.moltbook.com"
TARGET_AGENT="ClaudeCode_GLM4_7"

echo "Testing Moltbook API with 'subscriptions' terminology..."
echo ""

# Test endpoints with subscriptions
declare -a ENDPOINTS=(
    "/api/v1/agents/me/subscriptions"
    "/api/v1/agents/$TARGET_AGENT/subscriptions"
    "/api/v1/subscriptions"
    "/api/v1/subscription"
    "/api/v1/me/subscriptions"
    "/api/v1/subscribe"
    "/api/v1/agents/me/following/subscriptions"
    "/api/v1/agents/$TARGET_AGENT/following"
    "/api/v1/following"
    "/api/v1/followers"
    "/api/v1/follow"
    "/api/v1/connections"
    "/api/v1/agents/me/connections"
    "/api/v1/friends"
    "/api/v1/agents/me/friends"
)

for endpoint in "${ENDPOINTS[@]}"; do
    echo -n "Testing GET: $endpoint ... "

    response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo "✓ SUCCESS ($http_code)"
        echo "Response: $body"
        echo ""
        echo "========================================="
        echo "FOUND WORKING ENDPOINT!"
        echo "========================================="
        echo "Endpoint: $endpoint"
        echo "HTTP Code: $http_code"
        echo ""
        echo "Full curl command:"
        echo "curl -X GET '$BASE_URL$endpoint' \\"
        echo "  -H 'Authorization: Bearer $API_KEY' \\"
        echo "  -H 'Content-Type: application/json'"
        echo "========================================="
        exit 0
    elif [ "$http_code" = "400" ] || [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
        echo "✗ Auth/Error ($http_code)"
    elif [ "$http_code" = "404" ]; then
        echo "✗ Not Found"
    elif [ "$http_code" = "405" ]; then
        echo "✗ Method Not Allowed"
    else
        echo "✗ ($http_code)"
    fi
done

echo ""
echo "Trying different base paths..."
for base in "/api" "/v1" ""; do
    for path in "subscriptions" "following" "followers" "connections"; do
        endpoint="$base/$path"
        echo -n "Testing: $endpoint ... "
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint" \
            -H "Authorization: Bearer $API_KEY")
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | head -n-1)

        if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
            echo "✓ SUCCESS ($http_code)"
            echo "Response: $body"
            echo ""
            echo "Found: $endpoint"
            exit 0
        else
            echo "✗ ($http_code)"
        fi
    done
done

echo ""
echo "✗ No working endpoints found"
exit 1
