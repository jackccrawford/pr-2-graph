#!/bin/bash

# TIN Node Graph Integration Test Suite
# Tests all new endpoints for Phase 1 integration

echo "🧪 TIN Node Graph Integration Test Suite"
echo "========================================"

BASE_URL="http://localhost:7700"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"
    
    echo -e "\n${BLUE}Testing: $name${NC}"
    
    if [ "$method" = "POST" ]; then
        if [ -n "$data" ]; then
            response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" "$BASE_URL$endpoint")
        else
            response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$BASE_URL$endpoint")
        fi
    else
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$BASE_URL$endpoint")
    fi
    
    http_code=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo "$response" | sed -e 's/HTTPSTATUS:.*//g')
    
    if [ "$http_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} - HTTP $http_code"
        echo "Response: $(echo "$body" | jq -c . 2>/dev/null || echo "$body")"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} - Expected HTTP $expected_status, got $http_code"
        echo "Response: $body"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Start tests
echo "Starting TIN Node Graph integration tests..."

# Test 1: Health check
test_endpoint "Health Check" "GET" "/health" "" 200

# Test 2: List analyses (should be empty initially)
test_endpoint "List Analyses (Empty)" "GET" "/api/tin-graph/analyses" "" 200

# Test 3: Create analysis with simple data
SIMPLE_DATA='{"title": "Simple Test PR", "pr_number": 1, "repository": "test/simple", "comments": [{"id": "1", "author": "alice", "body": "Initial comment", "created_at": "2025-01-01T00:00:00Z"}]}'
if test_endpoint "Create Simple Analysis" "POST" "/api/tin-graph/analyze" "$SIMPLE_DATA" 200; then
    # Extract analysis ID from response
    ANALYSIS_ID=$(echo "$body" | jq -r '.analysis_id')
    echo "Created analysis ID: $ANALYSIS_ID"
    
    # Test 4: Get specific analysis
    test_endpoint "Get Specific Analysis" "GET" "/api/tin-graph/analysis/$ANALYSIS_ID" "" 200
    
    # Test 5: Get visualization data
    test_endpoint "Get Visualization Data" "GET" "/api/tin-graph/visualization/$ANALYSIS_ID" "" 200
fi

# Test 6: List analyses (should have one now)
test_endpoint "List Analyses (With Data)" "GET" "/api/tin-graph/analyses" "" 200

# Test 7: Create analysis with complex data
COMPLEX_DATA='{"title": "Complex Test PR", "pr_number": 2, "repository": "test/complex", "comments": [{"id": "1", "author": "alice", "body": "I found an issue with the authentication system", "created_at": "2025-01-01T00:00:00Z"}, {"id": "2", "author": "bob", "body": "I can help fix that. Let me create a solution", "created_at": "2025-01-01T01:00:00Z"}, {"id": "3", "author": "charlie", "body": "Great work! This breakthrough will help the whole team", "created_at": "2025-01-01T02:00:00Z"}]}'
if test_endpoint "Create Complex Analysis" "POST" "/api/tin-graph/analyze" "$COMPLEX_DATA" 200; then
    COMPLEX_ANALYSIS_ID=$(echo "$body" | jq -r '.analysis_id')
    echo "Created complex analysis ID: $COMPLEX_ANALYSIS_ID"
    
    # Test visualization for complex data
    test_endpoint "Get Complex Visualization" "GET" "/api/tin-graph/visualization/$COMPLEX_ANALYSIS_ID" "" 200
fi

# Test 8: Test with TIN docs PR data
test_endpoint "TIN Docs PR Test" "POST" "/api/tin-graph/test-tin-docs" "" 200

# Test 9: Error handling - non-existent analysis
test_endpoint "Non-existent Analysis" "GET" "/api/tin-graph/analysis/non-existent-id" "" 404

# Test 10: Error handling - non-existent visualization
test_endpoint "Non-existent Visualization" "GET" "/api/tin-graph/visualization/non-existent-id" "" 404

# Final results
echo -e "\n🏁 Test Results"
echo "==============="
echo -e "${GREEN}✅ Passed: $TESTS_PASSED${NC}"
echo -e "${RED}❌ Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! TIN Node Graph integration is working correctly.${NC}"
    exit 0
else
    echo -e "\n${RED}💥 Some tests failed. Please check the output above.${NC}"
    exit 1
fi
