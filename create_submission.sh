#!/bin/bash
# Script tự động tạo file nộp bài

if [ -z "$1" ]; then
    echo "Usage: ./create_submission.sh <MSSV>"
    echo "Example: ./create_submission.sh 1234567"
    exit 1
fi

MSSV=$1
OUTPUT="${MSSV}.zip"

echo "========================================"
echo "Creating submission file: $OUTPUT"
echo "========================================"
echo ""

# Clean
echo "Cleaning temporary files..."
make clean 2>/dev/null

# Check if README has student info
echo "Checking README.md..."
if ! grep -q "THÔNG TIN SINH VIÊN" README.md; then
    echo "⚠ WARNING: README.md chưa có thông tin sinh viên!"
    echo "Vui lòng điền thông tin vào README.md trước khi nộp."
    echo ""
fi

# Check if video link exists
if ! grep -q "youtu" README.md && ! grep -q "drive.google" README.md; then
    echo "⚠ WARNING: README.md chưa có link video!"
    echo "Vui lòng thêm link video vào README.md."
    echo ""
fi

# Create zip
echo "Creating ZIP file..."
zip -r "$OUTPUT" \
  README.md \
  QUICKSTART.md \
  SUBMISSION.md \
  Makefile \
  config/ \
  src/ \
  logs/README.md \
  test_ses.py \
  -x "*.pyc" \
  -x "__pycache__/*" \
  -x ".git/*" \
  -x "logs/*.log" \
  -x "docs/*.aux" \
  -x "docs/*.log" \
  -x "docs/*.out" \
  -x "docs/_minted/*" \
  > /dev/null

if [ $? -eq 0 ]; then
    SIZE=$(du -h "$OUTPUT" | cut -f1)
    echo ""
    echo "========================================"
    echo "✓ Successfully created: $OUTPUT ($SIZE)"
    echo "========================================"
    echo ""
    
    echo "Checklist before submission:"
    echo "  [ ] README.md has student information"
    echo "  [ ] README.md has video demo link"
    echo "  [ ] All code files are included"
    echo "  [ ] Test the ZIP file before submitting"
    echo ""
    
    echo "To test the submission:"
    echo "  mkdir test_$MSSV"
    echo "  unzip $OUTPUT -d test_$MSSV"
    echo "  cd test_$MSSV"
    echo "  make setup && make verify"
    echo "  make run-test"
    echo ""
else
    echo "✗ Failed to create ZIP file"
    exit 1
fi
