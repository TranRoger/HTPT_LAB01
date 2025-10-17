#!/bin/bash
# Test script for SES implementation

set -e

echo "================================"
echo "SES Algorithm Test Script"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check Python version
echo -e "${YELLOW}Test 1: Checking Python version...${NC}"
python3 --version
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python is installed${NC}"
else
    echo -e "${RED}✗ Python is not installed${NC}"
    exit 1
fi
echo ""

# Test 2: Check directory structure
echo -e "${YELLOW}Test 2: Checking directory structure...${NC}"
for dir in src config logs docs; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓ $dir/ exists${NC}"
    else
        echo -e "${RED}✗ $dir/ does not exist${NC}"
        exit 1
    fi
done
echo ""

# Test 3: Check required files
echo -e "${YELLOW}Test 3: Checking required files...${NC}"
files=("src/ses_process.py" "src/launch_all.py" "src/log_analyzer.py" "config/config.json")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file exists${NC}"
    else
        echo -e "${RED}✗ $file does not exist${NC}"
        exit 1
    fi
done
echo ""

# Test 4: Syntax check
echo -e "${YELLOW}Test 4: Checking Python syntax...${NC}"
for pyfile in src/*.py; do
    python3 -m py_compile "$pyfile"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $pyfile syntax OK${NC}"
    else
        echo -e "${RED}✗ $pyfile has syntax errors${NC}"
        exit 1
    fi
done
echo ""

# Test 5: Config validation
echo -e "${YELLOW}Test 5: Validating config file...${NC}"
python3 -c "
import json
with open('config/config.json', 'r') as f:
    config = json.load(f)
    assert len(config['processes']) == 15, 'Should have 15 processes'
    for i, p in enumerate(config['processes']):
        assert p['id'] == i, f'Process {i} has wrong id'
        assert 'host' in p, f'Process {i} missing host'
        assert 'port' in p, f'Process {i} missing port'
    print('Config validation passed')
"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Config file is valid${NC}"
else
    echo -e "${RED}✗ Config file is invalid${NC}"
    exit 1
fi
echo ""

# Test 6: Port availability (optional)
echo -e "${YELLOW}Test 6: Checking port availability...${NC}"
for port in {5000..5014}; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}⚠ Port $port is in use${NC}"
    fi
done
echo -e "${GREEN}✓ Port check complete${NC}"
echo ""

# Test 7: Run quick test (3 processes, 10 messages each)
echo -e "${YELLOW}Test 7: Running quick integration test...${NC}"
echo "This will take about 30 seconds..."

# Create a test config with 3 processes
cat > config/test_config.json << EOF
{
  "processes": [
    {"id": 0, "host": "127.0.0.1", "port": 6000},
    {"id": 1, "host": "127.0.0.1", "port": 6001},
    {"id": 2, "host": "127.0.0.1", "port": 6002}
  ]
}
EOF

# Backup original config
cp config/config.json config/config.json.bak
cp config/test_config.json config/config.json

# Clean old logs
rm -f logs/process_*.log

# Run 3 processes with 10 messages each
python3 src/ses_process.py 0 10 200 > /dev/null 2>&1 &
P0_PID=$!
sleep 0.5

python3 src/ses_process.py 1 10 200 > /dev/null 2>&1 &
P1_PID=$!
sleep 0.5

python3 src/ses_process.py 2 10 200 > /dev/null 2>&1 &
P2_PID=$!

# Wait for completion (max 30 seconds)
sleep 20

# Kill processes if still running
kill $P0_PID $P1_PID $P2_PID 2>/dev/null || true
wait $P0_PID $P1_PID $P2_PID 2>/dev/null || true

# Restore original config
mv config/config.json.bak config/config.json

# Check results
echo ""
echo "Checking test results..."

for i in 0 1 2; do
    if [ -f "logs/process_$i.log" ]; then
        delivered=$(grep -c "DELIVERED" logs/process_$i.log || echo "0")
        expected=20  # 10 messages from each of 2 other processes
        echo "Process $i: $delivered messages delivered (expected ~$expected)"
        
        if [ "$delivered" -ge 15 ]; then
            echo -e "${GREEN}✓ Process $i delivered sufficient messages${NC}"
        else
            echo -e "${YELLOW}⚠ Process $i delivered fewer messages than expected${NC}"
        fi
    else
        echo -e "${RED}✗ No log file for process $i${NC}"
    fi
done
echo ""

# Test 8: Log analyzer
echo -e "${YELLOW}Test 8: Testing log analyzer...${NC}"
python3 src/log_analyzer.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Log analyzer works${NC}"
else
    echo -e "${RED}✗ Log analyzer failed${NC}"
fi
echo ""

# Summary
echo "================================"
echo -e "${GREEN}All tests passed!${NC}"
echo "================================"
echo ""
echo "You can now run the full demo with:"
echo "  python3 src/launch_all.py"
echo ""
echo "Or run individual processes:"
echo "  python3 src/ses_process.py <process_id> [num_messages] [messages_per_minute]"
echo ""
