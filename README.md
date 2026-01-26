# ĐỒ ÁN SES - THUẬT TOÁN SCHIPER-EGGLI-SANDOZ

**Đồ án cá nhân - Hệ thống phân tán**  
**Deadline:** 19-10-2025

---

## 📋 MỤC LỤC

1. [Giới thiệu](#-giới-thiệu)
2. [Yêu cầu đồ án](#-yêu-cầu-đồ-án)
3. [Cài đặt](#-cài-đặt)
4. [Cấu trúc dự án](#-cấu-trúc-dự-án)
5. [Hướng dẫn sử dụng](#-hướng-dẫn-sử-dụng)
6. [Thuật toán SES](#-thuật-toán-ses)
7. [Kết quả thực nghiệm](#-kết-quả-thực-nghiệm)
8. [Video Demo](#-video-demo)

---

## 🎯 GIỚI THIỆU

Dự án này cài đặt thuật toán **SES (Schiper-Eggli-Sandoz)** để đảm bảo **thứ tự nhân quả (causal ordering)** của các messages trong hệ thống phân tán.

### Tính năng chính:

✅ **15 processes** chạy đồng thời trên 1 hoặc nhiều máy  
✅ Mỗi process gửi **150 messages** đến mỗi process khác  
✅ **Vector Clock** theo dõi quan hệ nhân quả  
✅ **Message Buffering** tự động khi thiếu dependencies  
✅ **Causal Delivery** đảm bảo thứ tự đúng  
✅ **Detailed Logging** với màu sắc và timestamps  
✅ **Real-time Display** trạng thái buffer/delivery  
✅ **Log Analyzer** phân tích kết quả

---

## 📝 YÊU CẦU ĐỒ ÁN

### 1. Mô tả
- 15 processes chạy đồng thời
- Mỗi process gửi 150 messages đến 14 processes còn lại
- Thời gian phát sinh messages ngẫu nhiên (configurable)
- Tổng: **31,500 messages** (15 × 14 × 150)

### 2. Thiết kế
- Tuân thủ thuật toán SES
- Hiển thị rõ ràng buffering/delivery
- Ghi log chi tiết với:
  - Trạng thái message (buffer/delivery)
  - Timestamp của message
  - Vector clock cập nhật
  - Dependencies và lý do buffer

### 3. Demo
- 15 processes chạy cùng lúc
- Mỗi process có 14 threads gửi messages song song
- Configuration file cho IP, port, parameters
- Log file riêng cho mỗi process
- Không bị treo hay dừng giữa chừng

---

## ⚙️ CÀI ĐẶT

### Yêu cầu hệ thống:
- Python 3.7+
- Linux/Unix (khuyến nghị) hoặc Windows
- Chỉ sử dụng thư viện chuẩn Python (không cần pip install)

### Các bước cài đặt:

```bash
# 1. Clone repository
cd HTPT_LAB01

# 2. Kiểm tra Python
python3 --version

# 3. Setup project
make setup

# 4. Verify cài đặt
make verify
```

---

## 📁 CẤU TRÚC DỰ ÁN

```
HTPT_LAB01/
├── README.md                   # File này
├── Makefile                    # Automation commands
├── config/
│   └── config.json            # Cấu hình 15 processes
├── src/
│   ├── ses_process.py         # Core SES implementation
│   ├── launch_all.py          # Launcher cho 15 processes
│   └── log_analyzer.py        # Tool phân tích logs
├── logs/                      # Log files (auto-generated)
│   ├── process_0.log
│   ├── process_1.log
│   └── ...
└── docs/                      # Tài liệu báo cáo
```

---

## 🚀 HƯỚNG DẪN SỬ DỤNG

### Cách 1: Chạy Full Demo (Khuyến nghị)

```bash
# Chạy 15 processes với 150 messages mỗi process
make run

# Hoặc custom parameters
make run-custom MSGS=200 RATE=50
```

### Cách 2: Quick Test

```bash
# Chạy nhanh với 10 messages để test
make run-test
```

### Cách 3: Chạy từng process riêng

Mở 15 terminals và chạy:

```bash
# Terminal 1
make run-single PID=0 MSGS=150 RATE=100

# Terminal 2
make run-single PID=1 MSGS=150 RATE=100

# ... và tiếp tục cho đến PID=14
```

### Phân tích logs:

```bash
# Xem tổng quan tất cả processes
make analyze

# Xem chi tiết process 0
make analyze-process PID=0

# Xem log real-time
make tail PID=0

# Đếm messages
make count
```

### Tương tác khi chạy:

Khi process đang chạy:
- Nhấn **'s'** + Enter: Xem statistics
- Nhấn **'q'** + Enter: Thoát

---

## 🧮 THUẬT TOÁN SES

### Nguyên lý hoạt động:

**1. Vector Clock:**
- Mỗi process duy trì vector clock `VC[i]`
- `VC[i][i]`: Số sự kiện tại process i
- `VC[i][j]`: Process i biết về process j

**2. Gửi message:**
```
VC[i][i]++
Send message M with timestamp TS = VC[i]
```

**3. Nhận message M từ process j:**
```
Check delivery conditions:
  Điều kiện 1: TS[j] = VC[i][j] + 1
  Điều kiện 2: ∀k≠j: TS[k] ≤ VC[i][k]

If both conditions satisfied:
  VC[i] = max(VC[i], TS)
  VC[i][j]++
  Deliver message
Else:
  Buffer message
  Wait for dependencies
```

### Ví dụ minh họa:

```
Process 0 (VC=[1,0,0]) → Gửi M1 → Process 1
Process 1 nhận M1 với TS=[1,0,0]
  Kiểm tra: TS[0]=1, VC[1][0]=0
  → TS[0] = VC[1][0] + 1 ✓
  → Deliver ngay lập tức
  → Update: VC[1] = [1,1,0]

Process 2 (VC=[0,0,2]) → Gửi M2 → Process 1  
Process 1 nhận M2 với TS=[0,0,2]
  Kiểm tra: TS[2]=2, VC[1][2]=0
  → TS[2] ≠ VC[1][2] + 1 ✗
  → Buffer M2 (chờ messages từ P2)
```

### Hiển thị trong chương trình:

```
[P1] ✓ DELIVERED: Message 1 from P0 to P1
     Message VC: [1, 0, 0]
     Updated VC: [1, 1, 0]

[P1] ⊕ BUFFERED: Message 2 from P2 to P1
     Reason: Need P2 to advance from 0 to 1
     Buffer size: 1
```

---

## 📊 KẾT QUẢ THỰC NGHIỆM

### Cấu hình test:
- 15 processes
- 150 messages/process
- 100 messages/phút
- **Tổng: 31,500 messages**

### Kết quả mong đợi:

| Metric | Expected | Status |
|--------|----------|--------|
| Total Sent | 31,500 | ✅ |
| Total Received | 31,500 | ✅ |
| Total Delivered | 31,500 | ✅ |
| Causal Order | 100% | ✅ |

### Output mẫu:

```
SES ALGORITHM - LOG ANALYSIS
================================================================================

OVERALL STATISTICS
--------------------------------------------------------------------------------
Total messages sent:      31,500
Total messages received:  31,500
Total messages delivered: 31,500
Total messages buffered:  450
Total messages unbuffered: 450

VERIFICATION
--------------------------------------------------------------------------------
Expected total messages:  31,500
Actual delivered:         31,500
Status:                   ✓ SUCCESS - All messages delivered!
```

---

## 🎥 VIDEO DEMO

**Link video:** [Thêm link sau khi upload]

### Nội dung video (10-12 phút):

1. **Giới thiệu** (2 phút)
   - Giải thích đồ án và yêu cầu
   - Thuật toán SES overview

2. **Demo chạy** (5 phút)
   - Khởi chạy 15 processes
   - Quan sát buffering (màu vàng)
   - Quan sát delivery (màu xanh)
   - Giải thích vector clock

3. **Phân tích logs** (3 phút)
   - Mở log files
   - Chạy log analyzer
   - Verify tính đúng đắn

4. **Kết luận** (2 phút)
   - Tổng kết kết quả
   - Chứng minh causal ordering

---

## 🔧 COMMANDS REFERENCE

### Setup & Verify:
```bash
make setup          # Setup project
make verify         # Verify installation
```

### Running:
```bash
make run            # Full demo
make run-test       # Quick test
make run-custom MSGS=200 RATE=50  # Custom
make run-single PID=0 MSGS=150 RATE=100  # Single process
```

### Analysis:
```bash
make analyze        # Analyze all
make analyze-process PID=0  # Specific process
make count          # Count messages
make log-summary    # Summary
```

### Logs:
```bash
make logs           # List logs
make tail PID=0     # Tail log
```

### Maintenance:
```bash
make clean-logs     # Clean logs
make clean          # Clean all
make kill           # Kill processes
make check-ports    # Check ports
```

---

## 🐛 TROUBLESHOOTING

### Port already in use:
```bash
make kill
make check-ports
```

### Connection refused:
- Đảm bảo tất cả processes đã khởi động
- Chờ 2-3 giây sau khi start

### Messages không được delivered:
- Kiểm tra log files
- Verify vector clock logic
- Check network/firewall

---

## 📚 TÀI LIỆU THAM KHẢO

1. **Paper gốc:**
   - Schiper, E. G., Eggli, J., & Sandoz, A. (1989)
   - "A New Algorithm to Implement Causal Ordering"

2. **Slide bài giảng:**
   - Môn Hệ thống phân tán
   - Chương: Causal Ordering và Vector Clocks

---

## 👨‍💻 THÔNG TIN SINH VIÊN

- **Họ tên:** Trần Hùng Anh
- **MSSV:** 22120016
- **Lớp:** 22_4
- **Email:** anhth5659@gmail.com

---

## 📄 LICENSE

Dự án này được tạo cho mục đích học tập - Môn Hệ thống phân tán

---

**Made with ❤️ for HTPT Lab**
