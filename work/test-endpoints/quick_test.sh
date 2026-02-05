#!/bin/bash

API_KEY="moltbook_sk_vaP2K_akyhbSUYYnOduzlguUHrDU4cSY"
BASE_URL="https://www.moltbook.com"
TARGET_AGENT="ClaudeCode_GLM4_7"

# Array of endpoints to test
declare -a ENDPOINTS=(
    "/api/v1/agents/me/following"
    "/api/v1/agents/me/followers"
    "/api/v1/agents/$TARGET_AGENT/following"
    "/api/v1/agents/$TARGET_AGENT/followers"
    "/api/v1/me/following"
    "/api/v1/me/followers"
    "/api/v1/following"
    "/api/v1/followers"
    "/api/v1/social/following"
    "/api/v1/social/followers"
    "/api/v1/follow/following"
    "/api/v1/follow/followers"
    "/api/v1/user/following"
    "/api/v1/user/followers"
    "/api/v1/connections/following"
    "/api/v1/connections/followers"
    "/api/agents/me/following"
    "/api/agents/me/followers"
    "/agents/me/following"
    "/agents/me/followers"
    "/following"
    "/followers"
)

echo "Testing Moltbook API endpoints..."
echo "Target: $TARGET_AGENT"
echo ""

SUCCESS=0

for endpoint in "${ENDPOINTS[@]}"; do
    echo -n "Testing: $endpoint ... "

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
        echo "Response: $body"
        echo ""
        echo "Full curl command:"
        echo "curl -X GET '$BASE_URL$endpoint' \\"
        echo "  -H 'Authorization: Bearer $API_KEY' \\"
        echo "  -H 'Content-Type: application/json'"
        echo "========================================="
        SUCCESS=1
        break
    elif [ "$http_code" = "400" ] || [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
        echo "✗ ($http_code) - Auth/Error"
        echo "Response: $body"
    elif [ "$http_code" = "404" ]; then
        echo "✗ Not Found (404)"
    elif [ "$http_code" = "405" ]; then
        echo "✗ Method Not Allowed (405)"
    else
        echo "✗ ($http_code)"
    fi
done

if [ $SUCCESS -eq 0 ]; then
    echo ""
    echo "No 200 response found. Let me try with different approaches..."

    # Try without /api/v1 prefix
    echo ""
    echo "Trying without /api/v1 prefix..."
    for endpoint in "/following" "/followers" "/me/following" "/me/followers"; do
        echo -n "Testing: $endpoint ... "
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint" \
            -H "Authorization: Bearer $API_KEY")

        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | head -n-1)

        if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
            echo "✓ SUCCESS ($http_code)"
            echo "Response: $body"
            SUCCESS=1
            break
        else
            echo "✗ ($http_code)"
        fi
    done
fi

if [ $SUCCESS -eq 0 ]; then
    echo ""
    echo "Trying POST requests..."
    for endpoint in "/api/v1/following" "/api/v1/followers"; do
        echo -n "Testing POST: $endpoint ... "
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint" \
            -X POST \
            -H "Authorization: Bearer $API_KEY" \
            -H "Content-Type: application/json" \
            -d '{}')

        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | head -n-1)

        if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
            echo "✓ SUCCESS ($http_code)"
            echo "Response: $body"
            SUCCESS=1
            break
        else
            echo "✗ ($http_code)"
        fi
    done
fi

echo ""
if [ $SUCCESS -eq 1 ]; then
    echo "✓ Found working endpoint(s)!"
    exit 0
else
    echo "✗ No working endpoints found"
    exit 1
fi
