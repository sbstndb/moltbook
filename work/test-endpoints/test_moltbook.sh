#!/bin/bash

API_KEY="moltbook_sk_vaP2K_akyhbSUYYnOduzlguUHrDU4cSY"
BASE_URL="https://www.moltbook.com/api/v1"
TARGET_AGENT="ClaudeCode_GLM4_7"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TOTAL_TESTS=0
SUCCESS_TESTS=0

# Test function
test_endpoint() {
    local endpoint="$1"
    local method="${2:-GET}"
    local use_auth="${3:-true}"
    local description="$4"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -e "\n${YELLOW}Test #$TOTAL_TESTS: $method $endpoint${NC}"
    echo "Description: $description"

    # Build curl command
    local curl_cmd="curl -s -w '\nHTTP_STATUS:%{http_code}' -X $method"

    if [ "$use_auth" = true ]; then
        curl_cmd="$curl_cmd -H 'Authorization: Bearer $API_KEY'"
    fi

    curl_cmd="$curl_cmd '$BASE_URL$endpoint'"

    # Execute and capture response
    response=$(eval $curl_cmd)
    http_code=$(echo "$response" | grep -o 'HTTP_STATUS:[0-9]*' | cut -d: -f2)
    body=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*//')

    echo "HTTP Status: $http_code"
    echo "Response: $body"

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✓ SUCCESS!${NC}"
        SUCCESS_TESTS=$((SUCCESS_TESTS + 1))
        echo "========================================="
        echo "WORKING ENDPOINT FOUND!"
        echo "========================================="
        echo "Endpoint: $endpoint"
        echo "Method: $method"
        echo "Auth: $use_auth"
        echo "Full command: curl -X $method -H 'Authorization: Bearer $API_KEY' '$BASE_URL$endpoint'"
        echo "========================================="
        return 0
    else
        echo -e "${RED}✗ Failed${NC}"
        return 1
    fi
}

echo "========================================="
echo "Moltbook API Endpoint Testing"
echo "Target: $TARGET_AGENT"
echo "========================================="

# Test different URL patterns
URL_PATTERNS=(
    "/agents/me/following"
    "/agents/me/followers"
    "/agents/$TARGET_AGENT/following"
    "/agents/$TARGET_AGENT/followers"
    "/agents/$TARGET_AGENT/connections/following"
    "/agents/$TARGET_AGENT/connections/followers"
    "/me/following"
    "/me/followers"
    "/follow/following"
    "/follow/followers"
    "/following"
    "/followers"
    "/api/v1/following"
    "/api/v1/followers"
    "/social/following"
    "/social/followers"
    "/user/following"
    "/user/followers"
    "/users/$TARGET_AGENT/following"
    "/users/$TARGET_AGENT/followers"
    "/profile/$TARGET_AGENT/following"
    "/profile/$TARGET_AGENT/followers"
    "/u/$TARGET_AGENT/following"
    "/u/$TARGET_AGENT/followers"
    "/agent/following"
    "/agent/followers"
)

# Test with query params
PARAMS=(
    ""
    "?format=json"
    "?limit=100"
    "?offset=0"
    "?agent_name=$TARGET_AGENT"
    "?username=$TARGET_AGENT"
)

# HTTP methods
METHODS=("GET" "POST" "OPTIONS" "HEAD")

# Test all combinations
for pattern in "${URL_PATTERNS[@]}"; do
    for param in "${PARAMS[@]}"; do
        endpoint="$pattern$param"
        test_endpoint "$endpoint" "GET" true "With auth, GET"
        if [ $SUCCESS_TESTS -gt 0 ]; then
            break 2
        fi
    done
done

# If no success yet, try without auth and different methods
if [ $SUCCESS_TESTS -eq 0 ]; then
    echo -e "\n${YELLOW}No success yet, trying without auth and different methods...${NC}"

    for pattern in "${URL_PATTERNS[@]}"; do
        for method in "${METHODS[@]}"; do
            if [ "$method" != "GET" ]; then
                test_endpoint "$pattern" "$method" true "$method with auth"
                if [ $SUCCESS_TESTS -gt 0 ]; then
                    break 2
                fi

                test_endpoint "$pattern" "$method" false "$method without auth"
                if [ $SUCCESS_TESTS -gt 0 ]; then
                    break 2
                fi
            fi
        done
    done
fi

# If still no success, try more variations
if [ $SUCCESS_TESTS -eq 0 ]; then
    echo -e "\n${YELLOW}Still no success, trying more variations...${NC}"

    # Try with different base paths
    BASE_VARIATIONS=(
        ""
        "/api"
        "/api/v1"
        "/v1"
    )

    for base in "${BASE_VARIATIONS[@]}"; do
        test_endpoint "$base/following" "GET" true "Base: $base/following"
        if [ $SUCCESS_TESTS -gt 0 ]; then
            break
        fi
        test_endpoint "$base/followers" "GET" true "Base: $base/followers"
        if [ $SUCCESS_TESTS -gt 0 ]; then
            break
        fi
    done
fi

echo -e "\n========================================="
echo "Testing Complete!"
echo "Total tests run: $TOTAL_TESTS"
echo "Successful endpoints found: $SUCCESS_TESTS"
echo "========================================="

if [ $SUCCESS_TESTS -eq 0 ]; then
    echo -e "${RED}No working endpoints found${NC}"
    exit 1
else
    echo -e "${GREEN}Found working endpoint(s)!${NC}"
    exit 0
fi
