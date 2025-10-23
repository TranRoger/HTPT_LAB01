# 📦 NỘP BÀI - HƯỚNG DẪN

Hướng dẫn chuẩn bị và nộp bài đồ án SES

---

## 📋 CHECKLIST TRƯỚC KHI NỘP

### ✅ Code & Documentation

- [ ] Code chạy được không lỗi
- [ ] Test với `make run-test`
- [ ] Verify với `make analyze`
- [ ] README.md đã điền đầy đủ thông tin:
  - [ ] Họ tên
  - [ ] MSSV
  - [ ] Lớp
  - [ ] Email

### ✅ Video Demo

- [ ] Video đã quay xong
- [ ] Video đã upload lên YouTube/Google Drive
- [ ] Link video đã public (không private)
- [ ] Đã thêm link vào README.md
- [ ] Video có giọng nói thuyết minh
- [ ] Video rõ ràng, không bị giật lag

### ✅ Log Files

- [ ] Đã chạy ít nhất 1 lần full demo
- [ ] Log files đầy đủ trong `logs/`
- [ ] Đã chạy `make analyze` và có kết quả

---

## 📝 CHUẨN BỊ FILE NỘP

### Bước 1: Cập nhật thông tin cá nhân

Mở file `README.md` và điền vào cuối file:

```markdown
## 👨‍💻 THÔNG TIN SINH VIÊN

- **Họ tên:** Nguyễn Văn A
- **MSSV:** 1234567
- **Lớp:** HTPT01
- **Email:** nguyenvana@student.edu.vn
```

### Bước 2: Thêm link video

```markdown
## 🎥 VIDEO DEMO

**Link video:** https://youtu.be/your-video-id

hoặc

**Link video:** https://drive.google.com/file/d/your-file-id/view
```

### Bước 3: Chạy full test và lưu logs

```bash
# Clean everything
make clean

# Run full demo
make run

# Wait for completion...

# Analyze
make analyze > RESULT.txt
```

### Bước 4: Tạo file ZIP

```bash
# Tạo file nộp bài (thay 1234567 bằng MSSV của bạn)
zip -r 1234567.zip \
  README.md \
  QUICKSTART.md \
  Makefile \
  config/ \
  src/ \
  logs/ \
  docs/ \
  RESULT.txt \
  -x "*.pyc" \
  -x "__pycache__/*" \
  -x ".git/*" \
  -x "*.aux" \
  -x "*.log" \
  -x "*.out"
```

**Hoặc dùng script tự động:**

```bash
./create_submission.sh 1234567
```

---

## 📁 CẤU TRÚC FILE NỘP

File `<MSSV>.zip` phải chứa:

```
<MSSV>.zip
├── README.md              # Có link video và thông tin sinh viên
├── QUICKSTART.md          # Hướng dẫn quick start
├── Makefile               # Automation commands
├── config/
│   └── config.json       # Cấu hình 15 processes
├── src/
│   ├── ses_process.py    # Core implementation
│   ├── launch_all.py     # Launcher
│   └── log_analyzer.py   # Log analyzer
├── logs/
│   ├── process_0.log     # Sample logs
│   ├── process_1.log
│   └── ...
├── docs/                 # Báo cáo (nếu có)
└── RESULT.txt            # Kết quả analyze (optional)
```

---

## 🎥 YÊU CẦU VIDEO DEMO

### Độ dài: 10-12 phút

### Nội dung bắt buộc:

1. **Giới thiệu (2 phút)**
   - Xin chào, giới thiệu bản thân (tên, MSSV)
   - Giới thiệu đồ án: Thuật toán SES
   - Giải thích ngắn gọn thuật toán

2. **Cấu trúc code (2 phút)**
   - Show cấu trúc thư mục
   - Giải thích các file chính:
     - `ses_process.py`: Core logic
     - `launch_all.py`: Launcher
     - `log_analyzer.py`: Analyzer
   - Show config.json

3. **Demo chạy chương trình (4 phút)**
   - Chạy: `make run`
   - Giải thích output đang xuất hiện:
     - Messages được gửi
     - Buffering (màu vàng)
     - Delivery (màu xanh)
   - Point out vector clock updates
   - Giải thích tại sao một số messages bị buffer

4. **Phân tích kết quả (2 phút)**
   - Chạy: `make analyze`
   - Giải thích output:
     - Total messages
     - Verification (31,500 messages)
     - Buffering statistics
   - Mở một log file để show chi tiết

5. **Kết luận (1 phút)**
   - Tổng kết kết quả
   - Chứng minh tính đúng đắn
   - Cảm ơn

### Tips quay video:

- ✅ Nói rõ ràng, không quá nhanh
- ✅ Screen resolution đủ lớn để đọc code
- ✅ Zoom in khi cần thiết
- ✅ Test âm thanh trước khi quay
- ✅ Có thể edit cắt ghép để video mượt hơn

---

## 🚀 SCRIPT TẠO FILE NỘP TỰ ĐỘNG

Tạo file `create_submission.sh`:

```bash
#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./create_submission.sh <MSSV>"
    echo "Example: ./create_submission.sh 1234567"
    exit 1
fi

MSSV=$1
OUTPUT="${MSSV}.zip"

echo "Creating submission file: $OUTPUT"

# Clean
make clean

# Create zip
zip -r "$OUTPUT" \
  README.md \
  QUICKSTART.md \
  Makefile \
  config/ \
  src/ \
  logs/ \
  docs/ \
  test_ses.py \
  -x "*.pyc" \
  -x "__pycache__/*" \
  -x ".git/*" \
  -x "docs/*.aux" \
  -x "docs/*.log" \
  -x "docs/*.out" \
  -x "docs/_minted/*"

echo ""
echo "✓ Created: $OUTPUT"
echo ""
echo "Next steps:"
echo "  1. Unzip and test: unzip -q $OUTPUT -d test_$MSSV && cd test_$MSSV"
echo "  2. Verify: make setup && make verify"
echo "  3. If OK, submit $OUTPUT"
echo ""
```

Cấp quyền và chạy:

```bash
chmod +x create_submission.sh
./create_submission.sh 1234567
```

---

## ✅ KIỂM TRA CUỐI CÙNG

Trước khi nộp, test lại file ZIP:

```bash
# Giải nén vào thư mục test
unzip 1234567.zip -d test_submission

# Vào thư mục test
cd test_submission

# Setup và verify
make setup
make verify

# Chạy quick test
make run-test

# Nếu OK thì có thể nộp!
```

---

## 📅 DEADLINE

**19-10-2025**

⚠️ **Lưu ý:** 
- Nộp trễ sẽ bị trừ điểm
- Kiểm tra kỹ trước khi nộp
- Backup file ZIP ở nhiều nơi

---

## 💯 TIÊU CHÍ CHẤM ĐIỂM

- **25%** - Tài liệu đi kèm, có link video demo
- **15%** - Trình bày log file
- **15%** - Phần hiển thị, giao tiếp người dùng
- **45%** - Tính đúng đắn của chương trình

### Tips để đạt điểm cao:

1. **Tài liệu (25%)**
   - README.md chi tiết, dễ hiểu
   - Video demo rõ ràng, có giọng nói
   - Giải thích thuật toán tốt

2. **Log file (15%)**
   - Log đầy đủ, chi tiết
   - Hiển thị rõ buffering/delivery
   - Vector clock được ghi log

3. **Hiển thị (15%)**
   - Console output có màu sắc
   - Thông tin rõ ràng, dễ đọc
   - Interactive commands (s, q)

4. **Tính đúng đắn (45%)**
   - 31,500 messages delivered đúng
   - Causal ordering đảm bảo 100%
   - Không bị crash, treo
   - Vector clock logic đúng

---

**Good luck! 🎓**
