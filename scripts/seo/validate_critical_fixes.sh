#!/bin/bash
# Critical SEO Fixes Validation Script

echo "🔍 Validating Critical SEO Fixes for drsayuj.info"
echo "=================================================="

# Test 1: 404 Redirect Fix
echo "1. Testing 404 redirect fix..."
REDIRECT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -I https://www.drsayuj.info/services/epilepsy-surgery)
REDIRECT_LOCATION=$(curl -s -I https://www.drsayuj.info/services/epilepsy-surgery | grep -i location | cut -d' ' -f2- | tr -d '
')

if [ "$REDIRECT_STATUS" = "301" ] && [[ "$REDIRECT_LOCATION" == *"epilepsy-surgery-hyderabad"* ]]; then
    echo "✅ Redirect fix: PASSED (301 to correct URL)"
else
    echo "❌ Redirect fix: FAILED (Status: $REDIRECT_STATUS, Location: $REDIRECT_LOCATION)"
fi

# Test 2: Canonical URL Fixes
echo "2. Testing canonical URL fixes..."
PATIENT_STORIES=(
    "/patient-stories"
    "/patient-stories/minimal-invasive-meningioma-resection"
    "/patient-stories/lumbar-miss-tlif-recovery"
    "/patient-stories/temporal-lobe-epilepsy-control"
    "/patient-stories/carpal-tunnel-day-care-success"
)

for page in "${PATIENT_STORIES[@]}"; do
    CANONICAL=$(curl -s "https://www.drsayuj.info$page" | grep -o '<link rel="canonical" href="[^"]*"' | cut -d'"' -f2)
    EXPECTED="https://www.drsayuj.info$page"
    
    if [ "$CANONICAL" = "$EXPECTED" ]; then
        echo "✅ Canonical fix for $page: PASSED"
    else
        echo "❌ Canonical fix for $page: FAILED (Got: $CANONICAL, Expected: $EXPECTED)"
    fi
done

# Test 3: Title Length Optimization
echo "3. Testing title length optimization..."
TITLE=$(curl -s https://www.drsayuj.info | grep -o '<title>[^<]*</title>' | sed 's/<[^>]*>//g')
TITLE_LENGTH=${#TITLE}

if [ $TITLE_LENGTH -le 60 ] && [ $TITLE_LENGTH -ge 50 ]; then
    echo "✅ Title length: PASSED ($TITLE_LENGTH characters)"
else
    echo "❌ Title length: FAILED ($TITLE_LENGTH characters, should be 50-60)"
fi

# Test 4: Meta Description Length Optimization
echo "4. Testing meta description length optimization..."
META_DESC=$(curl -s https://www.drsayuj.info | grep -o '<meta name="description" content="[^"]*"' | cut -d'"' -f4)
META_LENGTH=${#META_DESC}

if [ $META_LENGTH -le 160 ] && [ $META_LENGTH -ge 150 ]; then
    echo "✅ Meta description length: PASSED ($META_LENGTH characters)"
else
    echo "❌ Meta description length: FAILED ($META_LENGTH characters, should be 150-160)"
fi

echo "=================================================="
echo "Validation complete!"
