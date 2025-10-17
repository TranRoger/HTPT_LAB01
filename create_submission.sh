#!/bin/bash
# Script tạo file nộp bài

echo "================================"
echo "TẠO FILE NỘP BÀI ĐỒ ÁN SES"
echo "================================"
echo ""

# Yêu cầu nhập MSSV
read -p "Nhập MSSV của bạn: " MSSV

if [ -z "$MSSV" ]; then
    echo "❌ MSSV không được để trống!"
    exit 1
fi

echo ""
echo "Đang tạo file nộp bài cho MSSV: $MSSV"
echo ""

# Xác nhận
read -p "Bạn đã điền đầy đủ thông tin vào README.md? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "⚠️  Vui lòng điền thông tin vào README.md trước!"
    echo "   - Họ tên"
    echo "   - MSSV"
    echo "   - Email"
    echo "   - Lớp"
    echo "   - Link video demo"
    exit 1
fi

read -p "Bạn đã upload video demo? (y/n): " video_confirm
if [ "$video_confirm" != "y" ]; then
    echo "⚠️  Vui lòng upload video demo và thêm link vào README.md!"
    exit 1
fi

echo ""
echo "Bước 1: Dọn dẹp files..."

# Clean up
rm -f logs/*.log
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

echo "✓ Đã dọn dẹp files"

echo ""
echo "Bước 2: Tạo thư mục tạm..."

# Create temp directory
TEMP_DIR="/tmp/ses_submission_$$"
mkdir -p "$TEMP_DIR/$MSSV"

echo "✓ Đã tạo thư mục tạm"

echo ""
echo "Bước 3: Copy files..."

# Copy project files
cp -r . "$TEMP_DIR/$MSSV/"

cd "$TEMP_DIR/$MSSV"

# Remove unnecessary files
rm -rf .git
rm -rf __pycache__
rm -f .gitignore
rm -f create_submission.sh
rm -f logs/*.log
rm -f config/*.bak
rm -f config/test_config.json

echo "✓ Đã copy files"

echo ""
echo "Bước 4: Kiểm tra cấu trúc..."

# Check required files
required_files=(
    "README.md"
    "config/config.json"
    "src/ses_process.py"
    "src/launch_all.py"
    "src/log_analyzer.py"
    "docs/THIET_KE.md"
    "docs/VIDEO_DEMO.md"
)

all_exists=true
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Thiếu file: $file"
        all_exists=false
    else
        echo "✓ $file"
    fi
done

if [ "$all_exists" = false ]; then
    echo ""
    echo "❌ Có files bị thiếu! Vui lòng kiểm tra lại."
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo ""
echo "Bước 5: Tạo file ZIP..."

# Create zip
cd "$TEMP_DIR"
zip -r "$MSSV.zip" "$MSSV/" > /dev/null

if [ $? -eq 0 ]; then
    echo "✓ Đã tạo file ZIP"
else
    echo "❌ Lỗi khi tạo file ZIP"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Move to current directory
mv "$MSSV.zip" "$OLDPWD/"

# Get file size
cd "$OLDPWD"
filesize=$(du -h "$MSSV.zip" | cut -f1)

echo ""
echo "================================"
echo "✅ HOÀN TẤT!"
echo "================================"
echo ""
echo "File nộp bài: $MSSV.zip"
echo "Kích thước: $filesize"
echo "Vị trí: $(pwd)/$MSSV.zip"
echo ""

# Cleanup temp
rm -rf "$TEMP_DIR"

echo "Nội dung file nộp:"
unzip -l "$MSSV.zip" | head -20
echo "..."
echo ""

echo "================================"
echo "📋 CHECKLIST TRƯỚC KHI NỘP"
echo "================================"
echo ""
echo "Vui lòng kiểm tra:"
echo "  [ ] Đã điền đầy đủ thông tin vào README.md"
echo "  [ ] Link video demo có thể xem được"
echo "  [ ] Video có giọng nói thuyết minh"
echo "  [ ] File ZIP có tên đúng format: $MSSV.zip"
echo "  [ ] Đã test chạy chương trình"
echo "  [ ] Kích thước file < 50MB"
echo ""
echo "Nếu mọi thứ đã OK, có thể nộp bài qua hệ thống!"
echo ""
