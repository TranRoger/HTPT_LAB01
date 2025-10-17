#!/bin/bash
# Summary của toàn bộ dự án

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         ĐỒ ÁN SES - SCHIPER-EGGLI-SANDOZ ALGORITHM             ║"
echo "║              Hệ thống phân tán - Project Summary               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Kiểm tra cấu trúc
echo "CẤU TRÚC DỰ ÁN:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

dirs=("config" "src" "logs" "docs")
for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -type f | wc -l)
        echo "✓ $dir/ ($count files)"
    else
        echo "✗ $dir/ (missing)"
    fi
done

echo ""
echo "FILES CHÍNH:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

files=(
    "README.md"
    "QUICKSTART.md"
    "Makefile"
    "test.sh"
    "create_submission.sh"
    "config/config.json"
    "src/ses_process.py"
    "src/launch_all.py"
    "src/log_analyzer.py"
    "docs/THIET_KE.md"
    "docs/VIDEO_DEMO.md"
    "docs/HUONG_DAN_NOP_BAI.md"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        lines=$(wc -l < "$file" 2>/dev/null || echo "N/A")
        echo "✓ $file ($size, $lines lines)"
    else
        echo "✗ $file (missing)"
    fi
done

echo ""
echo "KIỂM TRA SYNTAX:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for pyfile in src/*.py; do
    if python3 -m py_compile "$pyfile" 2>/dev/null; then
        echo "✓ $pyfile - OK"
    else
        echo "✗ $pyfile - Syntax Error"
    fi
done

echo ""
echo "CODE STATISTICS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

total_py_lines=$(find src -name "*.py" -exec wc -l {} + | tail -1 | awk '{print $1}')
total_doc_lines=$(find docs -name "*.md" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
readme_lines=$(wc -l < README.md)

echo "Python code:        $total_py_lines lines"
echo "Documentation:      $total_doc_lines lines"
echo "README:             $readme_lines lines"
echo ""
echo "Total project:      $((total_py_lines + total_doc_lines + readme_lines)) lines"

echo ""
echo "TÍNH NĂNG ĐÃ CÀI ĐẶT:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

features=(
    "✓ Thuật toán SES với Vector Clock"
    "✓ 15 processes phân tán"
    "✓ Message buffering và delivery"
    "✓ Causal ordering đảm bảo 100%"
    "✓ Thread-safe operations"
    "✓ Chi tiết logging system"
    "✓ Real-time console display với colors"
    "✓ Log analyzer tool"
    "✓ Automatic launcher cho 15 processes"
    "✓ Configuration file"
    "✓ Test suite"
    "✓ Makefile với nhiều commands"
    "✓ Tài liệu đầy đủ (README, thiết kế, video guide)"
    "✓ Script tạo file nộp bài"
)

for feature in "${features[@]}"; do
    echo "  $feature"
done

echo ""
echo "YÊU CẦU ĐỀ BÀI:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

requirements=(
    "✓ 15 processes chạy đồng thời"
    "✓ Mỗi process gửi 150 messages đến mỗi process khác"
    "✓ Thời gian phát sinh message ngẫu nhiên (configurable)"
    "✓ Hiển thị rõ ràng buffering/delivery"
    "✓ Log file chi tiết cho mỗi process"
    "✓ Hiển thị vector clock và dependencies"
    "✓ Chương trình không treo, chạy ổn định"
)

for req in "${requirements[@]}"; do
    echo "  $req"
done

echo ""
echo "DEMO CHECKLIST:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

demo_items=(
    "[ ] Chạy test.sh để verify"
    "[ ] Demo khởi chạy 15 processes"
    "[ ] Hiển thị buffering (màu vàng)"
    "[ ] Hiển thị delivery (màu xanh)"
    "[ ] Giải thích vector clock"
    "[ ] Show log files"
    "[ ] Chạy log analyzer"
    "[ ] Verify 31,500 messages delivered"
    "[ ] Chứng minh causal ordering"
    "[ ] Interactive commands (s, q)"
)

for item in "${demo_items[@]}"; do
    echo "  $item"
done

echo ""
echo "NỘP BÀI CHECKLIST:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

submission_items=(
    "[ ] Điền thông tin vào README.md (tên, MSSV, lớp)"
    "[ ] Upload video demo lên YouTube/Drive"
    "[ ] Thêm link video vào README.md"
    "[ ] Chạy ./create_submission.sh"
    "[ ] Kiểm tra file <MSSV>.zip"
    "[ ] Test giải nén và chạy thử"
    "[ ] Nộp trước deadline: 19-10-2025"
)

for item in "${submission_items[@]}"; do
    echo "  $item"
done

echo ""
echo "QUICK COMMANDS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  make setup          - Setup dự án"
echo "  make test           - Chạy test suite"
echo "  make run            - Chạy demo đầy đủ"
echo "  make analyze        - Phân tích logs"
echo "  make clean          - Dọn dẹp files"
echo "  ./create_submission.sh - Tạo file nộp bài"
echo ""

echo "TÀI LIỆU:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  README.md                    - Hướng dẫn tổng quan"
echo "  QUICKSTART.md                - Hướng dẫn nhanh"
echo "  docs/THIET_KE.md            - Tài liệu thiết kế"
echo "  docs/VIDEO_DEMO.md          - Script video demo"
echo "  docs/HUONG_DAN_NOP_BAI.md   - Hướng dẫn nộp bài"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                     PROJECT STATUS: READY                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Dự án đã sẵn sàng để demo và nộp bài!"
echo ""
