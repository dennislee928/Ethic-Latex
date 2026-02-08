#!/bin/bash
#
# Test Email Provider Connectivity
#
# Usage:
#   ./test-provider.sh resend
#   ./test-provider.sh sendgrid
#   ./test-provider.sh mailgun
#   ./test-provider.sh smtp2go
#   ./test-provider.sh all
#

set -e

PROVIDER="${1:-all}"
TEST_FROM="${TEST_FROM:-test@yourdomain.com}"
TEST_TO="${TEST_TO:-test@yourdomain.com}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Email Provider Connectivity Test"
echo "========================================"
echo ""

# Test Resend
test_resend() {
    echo -n "Testing Resend... "

    if [ -z "$RESEND_API_KEY" ]; then
        echo -e "${RED}FAILED${NC} - RESEND_API_KEY not set"
        return 1
    fi

    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST https://api.resend.com/emails \
        -H "Authorization: Bearer $RESEND_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"from\": \"$TEST_FROM\",
            \"to\": \"$TEST_TO\",
            \"subject\": \"Test Email from Resend\",
            \"html\": \"<p>This is a test email.</p>\"
        }")

    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_CODE" -eq 200 ]; then
        EMAIL_ID=$(echo "$BODY" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        echo -e "${GREEN}SUCCESS${NC} - Email ID: $EMAIL_ID"
        return 0
    else
        echo -e "${RED}FAILED${NC} - HTTP $HTTP_CODE"
        echo "$BODY"
        return 1
    fi
}

# Test SendGrid
test_sendgrid() {
    echo -n "Testing SendGrid... "

    if [ -z "$SENDGRID_API_KEY" ]; then
        echo -e "${RED}FAILED${NC} - SENDGRID_API_KEY not set"
        return 1
    fi

    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST https://api.sendgrid.com/v3/mail/send \
        -H "Authorization: Bearer $SENDGRID_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"personalizations\": [{
                \"to\": [{\"email\": \"$TEST_TO\"}]
            }],
            \"from\": {\"email\": \"$TEST_FROM\"},
            \"subject\": \"Test Email from SendGrid\",
            \"content\": [{
                \"type\": \"text/html\",
                \"value\": \"<p>This is a test email.</p>\"
            }]
        }")

    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_CODE" -eq 202 ]; then
        echo -e "${GREEN}SUCCESS${NC} - Email accepted (HTTP 202)"
        return 0
    else
        echo -e "${RED}FAILED${NC} - HTTP $HTTP_CODE"
        echo "$BODY"
        return 1
    fi
}

# Test Mailgun
test_mailgun() {
    echo -n "Testing Mailgun... "

    if [ -z "$MAILGUN_API_KEY" ] || [ -z "$MAILGUN_DOMAIN" ]; then
        echo -e "${RED}FAILED${NC} - MAILGUN_API_KEY or MAILGUN_DOMAIN not set"
        return 1
    fi

    REGION="${MAILGUN_REGION:-us}"
    if [ "$REGION" = "eu" ]; then
        API_URL="https://api.eu.mailgun.net/v3"
    else
        API_URL="https://api.mailgun.net/v3"
    fi

    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/$MAILGUN_DOMAIN/messages" \
        -u "api:$MAILGUN_API_KEY" \
        -F from="$TEST_FROM" \
        -F to="$TEST_TO" \
        -F subject="Test Email from Mailgun" \
        -F html="<p>This is a test email.</p>")

    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_CODE" -eq 200 ]; then
        MESSAGE_ID=$(echo "$BODY" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        echo -e "${GREEN}SUCCESS${NC} - Message ID: $MESSAGE_ID"
        return 0
    else
        echo -e "${RED}FAILED${NC} - HTTP $HTTP_CODE"
        echo "$BODY"
        return 1
    fi
}

# Test SMTP2Go
test_smtp2go() {
    echo -n "Testing SMTP2Go... "

    if [ -z "$SMTP2GO_API_KEY" ]; then
        echo -e "${RED}FAILED${NC} - SMTP2GO_API_KEY not set"
        return 1
    fi

    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST https://api.smtp2go.com/v3/email/send \
        -H "Content-Type: application/json" \
        -d "{
            \"api_key\": \"$SMTP2GO_API_KEY\",
            \"to\": [\"<$TEST_TO>\"],
            \"sender\": \"$TEST_FROM\",
            \"subject\": \"Test Email from SMTP2Go\",
            \"html_body\": \"<p>This is a test email.</p>\"
        }")

    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_CODE" -eq 200 ]; then
        SUCCEEDED=$(echo "$BODY" | grep -o '"succeeded":[0-9]*' | cut -d':' -f2)
        FAILED=$(echo "$BODY" | grep -o '"failed":[0-9]*' | cut -d':' -f2)

        if [ "$SUCCEEDED" -eq 1 ]; then
            EMAIL_ID=$(echo "$BODY" | grep -o '"email_id":"[^"]*"' | cut -d'"' -f4)
            echo -e "${GREEN}SUCCESS${NC} - Email ID: $EMAIL_ID"
            return 0
        else
            echo -e "${RED}FAILED${NC} - $FAILED recipients failed"
            echo "$BODY"
            return 1
        fi
    else
        echo -e "${RED}FAILED${NC} - HTTP $HTTP_CODE"
        echo "$BODY"
        return 1
    fi
}

# Run tests
if [ "$PROVIDER" = "all" ]; then
    echo "Testing all providers..."
    echo ""

    PASSED=0
    FAILED=0

    test_resend && PASSED=$((PASSED+1)) || FAILED=$((FAILED+1))
    test_sendgrid && PASSED=$((PASSED+1)) || FAILED=$((FAILED+1))
    test_mailgun && PASSED=$((PASSED+1)) || FAILED=$((FAILED+1))
    test_smtp2go && PASSED=$((PASSED+1)) || FAILED=$((FAILED+1))

    echo ""
    echo "========================================"
    echo "Results: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}"
    echo "========================================"

    [ $FAILED -eq 0 ] && exit 0 || exit 1
else
    case "$PROVIDER" in
        resend)
            test_resend
            ;;
        sendgrid)
            test_sendgrid
            ;;
        mailgun)
            test_mailgun
            ;;
        smtp2go)
            test_smtp2go
            ;;
        *)
            echo "Unknown provider: $PROVIDER"
            echo "Usage: $0 {resend|sendgrid|mailgun|smtp2go|all}"
            exit 1
            ;;
    esac
fi
