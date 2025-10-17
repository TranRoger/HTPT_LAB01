# HƯỚNG DẪN NỘP BÀI

## 📦 CHUẨN BỊ NỘP BÀI

### 1. Thông tin cần điền vào README.md

Mở file `README.md` và điền thông tin của bạn vào phần "THÔNG TIN LIÊN HỆ":

```markdown
## 👨‍💻 THÔNG TIN LIÊN HỆ

**Sinh viên thực hiện:** Nguyễn Văn A  
**MSSV:** 1234567  
**Email:** nguyenvana@student.hcmus.edu.vn  
**Lớp:** KHMT2021
```

### 2. Quay video demo

1. Làm theo hướng dẫn trong file `docs/VIDEO_DEMO.md`
2. Upload video lên YouTube (Unlisted) hoặc Google Drive
3. Copy link và paste vào `README.md` tại phần "Video Demo"

### 3. Kiểm tra lần cuối

Chạy test script để đảm bảo mọi thứ hoạt động:

```bash
chmod +x test.sh
./test.sh
```

Hoặc sử dụng Makefile:

```bash
make setup
make test
```

### 4. Tạo file nén

#### Cách 1: Sử dụng script tự động

Tạo file `create_submission.sh`:

```bash
#!/bin/bash
# Tạo file nộp bài

MSSV="1234567"  # ⚠️ THAY BẰNG MSSV CỦA BẠN

echo "Creating submission package for MSSV: $MSSV"

# Clean up
make clean

# Create submission directory
mkdir -p /tmp/$MSSV

# Copy all files
cp -r . /tmp/$MSSV/

# Remove unnecessary files
cd /tmp/$MSSV
rm -rf .git
rm -rf __pycache__
rm -f create_submission.sh
rm -f .gitignore
rm -f logs/*.log

# Create zip
cd /tmp
zip -r $MSSV.zip $MSSV/

# Move to original directory
mv $MSSV.zip ~/Documents/HOC-TAP/HTPT/HTPT_LAB01/

echo "✓ Created: $MSSV.zip"
```

Chạy script:

```bash
chmod +x create_submission.sh
./create_submission.sh
```

#### Cách 2: Thủ công

```bash
# Thay YOUR_MSSV bằng MSSV của bạn
cd ..
zip -r YOUR_MSSV.zip HTPT_LAB01/ \
    -x "HTPT_LAB01/.git/*" \
    -x "HTPT_LAB01/__pycache__/*" \
    -x "HTPT_LAB01/logs/*.log" \
    -x "HTPT_LAB01/.gitignore"
```

---

## 📋 CHECKLIST TRƯỚC KHI NỘP

### Thông tin cá nhân:
- [ ] Đã điền tên, MSSV, email, lớp vào README.md
- [ ] MSSV trên file nén trùng với MSSV thật

### Tài liệu:
- [ ] README.md đầy đủ và rõ ràng
- [ ] Link video demo đã được thêm vào README.md
- [ ] Video demo có thể xem được (test link)
- [ ] Video có giọng nói thuyết minh của sinh viên
- [ ] docs/THIET_KE.md đầy đủ
- [ ] docs/VIDEO_DEMO.md có script và hướng dẫn

### Code:
- [ ] src/ses_process.py hoạt động đúng
- [ ] src/launch_all.py có thể khởi chạy 15 processes
- [ ] src/log_analyzer.py phân tích được logs
- [ ] config/config.json đúng format
- [ ] Code có comments đầy đủ

### Testing:
- [ ] Đã chạy test.sh thành công
- [ ] Đã test chạy 15 processes
- [ ] Kiểm tra số lượng messages (31,500 total)
- [ ] Verify causal ordering từ logs
- [ ] Không có lỗi crash hoặc deadlock

### Files nộp:
- [ ] File nén đúng format: <MSSV>.zip
- [ ] Kích thước file hợp lý (< 50MB, không chứa video trong zip)
- [ ] Có thể giải nén và chạy được

---

## 📁 CẤU TRÚC FILE NỘP

File nén `<MSSV>.zip` phải chứa:

```
<MSSV>.zip
└── HTPT_LAB01/
    ├── README.md                 ✅ REQUIRED - Có link video demo
    ├── config/
    │   └── config.json          ✅ REQUIRED
    ├── src/
    │   ├── ses_process.py       ✅ REQUIRED
    │   ├── launch_all.py        ✅ REQUIRED
    │   └── log_analyzer.py      ✅ REQUIRED
    ├── docs/
    │   ├── THIET_KE.md         ✅ REQUIRED - Tài liệu thiết kế
    │   └── VIDEO_DEMO.md       ✅ REQUIRED - Script video
    ├── logs/                    ⚠️  EMPTY (không nộp log files)
    ├── Makefile                 ✅ RECOMMENDED
    ├── test.sh                  ✅ RECOMMENDED
    └── requirements.txt         ✅ RECOMMENDED
```

### ⚠️ KHÔNG NỘP:
- `.git/` directory
- `__pycache__/` directories
- `*.pyc` files
- `logs/*.log` files (quá lớn)
- `.gitignore`
- Video file (chỉ nộp link)

---

## 🎥 VIDEO DEMO YÊU CẦU

### Nội dung bắt buộc:

1. **Giới thiệu (25%):**
   - Tên, MSSV, lớp
   - Đề tài và yêu cầu
   - Giải thích thuật toán SES

2. **Demo chương trình (45%):**
   - Chạy 15 processes
   - Hiển thị buffering/delivery
   - Giải thích vector clock
   - Hiển thị log files

3. **Phân tích kết quả (15%):**
   - Số lượng messages
   - Thống kê buffering
   - Verify causal ordering

4. **Tính đúng đắn (15%):**
   - Chứng minh không mất message
   - Chứng minh causal ordering
   - Kiểm tra log files

### Yêu cầu kỹ thuật:

- **Thời lượng:** 10-15 phút
- **Định dạng:** MP4 hoặc AVI
- **Resolution:** 720p trở lên
- **Audio:** Rõ ràng, giọng nói của sinh viên
- **Platform:** YouTube (Unlisted) hoặc Google Drive (Anyone with link)

### Upload và chia sẻ:

**YouTube:**
```
1. Upload video
2. Set visibility: Unlisted
3. Copy link
4. Paste vào README.md
```

**Google Drive:**
```
1. Upload video
2. Right click → Share → Get link
3. Set: Anyone with the link can view
4. Copy link
5. Paste vào README.md
```

---

## ✅ NỘP BÀI

### Nộp qua hệ thống:

1. Đăng nhập vào hệ thống nộp bài của trường
2. Chọn môn "Hệ thống phân tán"
3. Chọn bài "Đồ án SES"
4. Upload file `<MSSV>.zip`
5. Xác nhận thông tin
6. Submit

### Nộp qua email (nếu có yêu cầu):

```
To: [email của giảng viên]
Subject: [HTPT] Nộp đồ án SES - MSSV: <MSSV> - Tên: <Họ tên>

Thân gửi Thầy/Cô,

Em là [Họ tên], MSSV: [MSSV], lớp [Lớp].
Em xin gửi Thầy/Cô bài nộp đồ án SES.

Link video demo: [Link]
File đính kèm: <MSSV>.zip

Em xin cảm ơn.

Trân trọng,
[Tên]
```

### Deadline:

⏰ **19-10-2025**

⚠️ **LƯU Ý:** Nộp trễ có thể bị trừ điểm!

---

## 🆘 HỖ TRỢ

### Nếu gặp vấn đề:

1. **Lỗi kỹ thuật:**
   - Kiểm tra lại test.sh
   - Xem logs để debug
   - Tham khảo docs/THIET_KE.md

2. **Câu hỏi về đề bài:**
   - Liên hệ trợ giảng
   - Hỏi trên diễn đàn môn học

3. **Vấn đề nộp bài:**
   - Liên hệ phòng đào tạo
   - Email giảng viên

### Thông tin liên hệ:

- **Giảng viên:** [Email]
- **Trợ giảng:** [Email]
- **Diễn đàn:** [Link]

---

## 📊 TIÊU CHÍ CHẤM ĐIỂM

### Phân bổ điểm:

| Tiêu chí | Điểm | Ghi chú |
|----------|------|---------|
| Tài liệu đi kèm, link video demo | 25% | README, docs, video |
| Trình bày log file | 15% | Chi tiết, rõ ràng |
| Hiển thị, giao tiếp người dùng | 15% | Console UI, colors |
| Tính đúng đắn của chương trình | 45% | Algorithm correctness |

### Chi tiết:

**1. Tài liệu (25%):**
- README.md đầy đủ: 10%
- Video demo chất lượng: 10%
- Tài liệu thiết kế: 5%

**2. Log file (15%):**
- Log chi tiết các sự kiện: 7%
- Buffering reason rõ ràng: 5%
- Format dễ đọc: 3%

**3. Hiển thị (15%):**
- Console output với colors: 7%
- Real-time updates: 5%
- Interactive commands: 3%

**4. Tính đúng đắn (45%):**
- Causal ordering đúng: 20%
- Không mất messages: 10%
- Buffer/delivery logic đúng: 10%
- Chạy ổn định không crash: 5%

---

**Chúc bạn hoàn thành tốt đồ án! 🎓**
