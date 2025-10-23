# ĐỒ ÁN SES - THUẬT TOÁN SCHIPER-EGGLI-SANDOZ

---

## MỤC LỤC

1. [Giới thiệu](#giới-thiệu)
2. [Cài đặt](#cài-đặt)
3. [Cấu trúc dự án](#cấu-trúc-dự-án)
4. [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
5. [Thuật toán SES](#thuật-toán-ses)

---

## GIỚI THIỆU

Dự án này cài đặt thuật toán **SES (Schiper-Eggli-Sandoz)** để đảm bảo thứ tự nhân quả (causal ordering) của các thông điệp trong hệ thống phân tán.

### Yêu cầu đồ án:
- 15 processes chạy đồng thời
- Mỗi process gửi 150 messages đến mỗi process khác
- Thời gian phát sinh message ngẫu nhiên (có thể điều chỉnh)
- Hiển thị rõ ràng buffering và delivery của messages
- Log file chi tiết cho mỗi process
- Hiển thị vector clock và dependencies

### Tính năng chính:
- **Vector Clock:** Theo dõi quan hệ nhân quả giữa các sự kiện
- **Message Buffering:** Lưu trữ messages chưa thể deliver
- **Causal Delivery:** Đảm bảo messages được deliver theo đúng thứ tự nhân quả
- **Detailed Logging:** Ghi log chi tiết về mọi sự kiện
- **Real-time Display:** Hiển thị trạng thái real-time với màu sắc

---

## CÀI ĐẶT

### Yêu cầu hệ thống:
- Python 3.7 trở lên
- Linux/Unix (khuyến nghị) hoặc Windows
- Các gói Python chuẩn (socket, threading, json, logging)

### Các bước cài đặt:

1. **Clone hoặc tải dự án:**
```bash
cd HTPT_LAB01
```

2. **Kiểm tra Python:**
```bash
python3 --version
```

3. **Cấp quyền thực thi (Linux/Unix):**
```bash
make setup
```

4. **Không cần cài đặt thêm dependencies** - dự án chỉ sử dụng thư viện chuẩn của Python!

---

## CẤU TRÚC DỰ ÁN

```
HTPT_LAB01/
├── README.md                 # File này
├── config/
│   └── config.json          # Cấu hình 15 processes (IP, port)
├── src/
│   ├── ses_process.py       # Core - Cài đặt thuật toán SES
│   ├── launch_all.py        # Script khởi chạy tất cả processes
│   └── log_analyzer.py      # Tool phân tích log files
├── logs/                    # Thư mục chứa log files (tự động tạo)
│   ├── process_0.log
│   ├── process_1.log
│   └── ...
└── docs/                    # Tài liệu bổ sung
    ├── THIET_KE.md         # Tài liệu thiết kế
    └── VIDEO_DEMO.md       # Link và hướng dẫn video demo
```

---

## HƯỚNG DẪN SỬ DỤNG

### Cách 1: Chạy tất cả 15 processes cùng lúc (Khuyến nghị)

```bash
make run
# or
make run-custom MSGS=[số_message] RATE=[messages_per_minute]
```

**Ví dụ:**
```bash
# Mặc định: 150 messages, 100 messages/phút
make run

# Custom: 200 messages, 50 messages/phút
make run-custom MSGS=200 RATE=50
```

### Cách 2: Chạy từng process riêng lẻ

**Terminal 1:**
```bash
make run-single PROC=0 MSGS=150 RATE=100
```

**Terminal 2:**
```bash
make run-single PROC=1 MSGS=150 RATE=100
```

**Terminal 3:**
```bash
make run-single PROC=2 MSGS=150 RATE=100
```

... và tiếp tục cho đến process 14.

### Phân tích log files:

**Xem tổng quan tất cả processes:**
```bash
make analyze
```

**Xem chi tiết một process cụ thể:**
```bash
make analyze-process PROC=0
```

### Tương tác trong khi chạy:

Khi một process đang chạy, bạn có thể:
- Nhấn **'s'** + Enter: Xem thống kê hiện tại
- Nhấn **'q'** + Enter: Thoát chương trình

---

## THUẬT TOÁN SES

### Nguyên lý hoạt động:

Thuật toán SES sử dụng **Vector Clock** để theo dõi quan hệ nhân quả:

1. **Vector Clock:** Mỗi process duy trì một vector clock `VC[i]`
   - `VC[i][i]`: Số sự kiện đã xảy ra tại process i
   - `VC[i][j]`: Process i biết về bao nhiêu sự kiện của process j

2. **Gửi message:**
   - Tăng `VC[i][i]++`
   - Gửi message kèm timestamp `TS = VC[i]`

3. **Nhận message M từ process j:**
   - Kiểm tra điều kiện delivery:
     - **Điều kiện 1:** `TS[j] = VC[i][j] + 1` (message tiếp theo từ j)
     - **Điều kiện 2:** `∀k≠j: TS[k] ≤ VC[i][k]` (không có dependencies thiếu)
   
4. **Nếu có thể deliver:**
   - Update vector clock: `VC[i] = max(VC[i], TS)`
   - `VC[i][j]++`
   - Deliver message
   
5. **Nếu không thể deliver:**
   - Buffer message
   - Chờ đến khi dependencies được thỏa mãn

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
  → Buffer M2 (chờ M từ P2 với seq 1)
```

### Hiển thị trong chương trình:

```
[P1] ✓ DELIVERED: Message 1 from P0 to P1 (màu xanh)
     Message VC: [1, 0, 0]
     Updated VC: [1, 1, 0]

[P1] ⊕ BUFFERED: Message 2 from P2 to P1 (màu vàng)
     Reason: Waiting for message #1 from P2 (got #2)
     Buffer size: 1
```

---

## KIỂM TRA VÀ DEBUG

### Xem log real-time:

```bash
# Terminal riêng để theo dõi log
tail -f logs/process_0.log
```

### Kiểm tra số lượng messages:

```bash
# Đếm số DELIVERED messages
grep "DELIVERED" logs/process_0.log | wc -l

# Đếm số BUFFERED messages
grep "BUFFERED" logs/process_0.log | wc -l
```

### Kiểm tra network ports:

```bash
# Xem các port đang sử dụng
netstat -an | grep 500[0-9]

# Hoặc
ss -tuln | grep 500[0-9]
```

---

## XỬ LÝ LỖI THƯỜNG GẶP

### Lỗi: "Address already in use"
```bash
# Kill process đang dùng port
lsof -ti:5000 | xargs kill -9
```

### Lỗi: "Connection refused"
- Đảm bảo tất cả processes đã khởi động
- Chờ 2-3 giây sau khi khởi động

### Lỗi: Messages không được delivered
- Kiểm tra log file xem lý do buffer
- Xác nhận vector clock logic
- Đảm bảo network không bị block

---

## TÀI LIỆU THAM KHẢO

1. **Paper gốc:** 
   - Schiper, E. G., Eggli, J., & Sandoz, A. (1989). 
   - "A New Algorithm to Implement Causal Ordering"

2. **Tài liệu bài giảng:**
   - Slide bài giảng môn Hệ thống phân tán
   - Chương: Causal Ordering và Vector Clocks

3. **Source code:**
   - Xem chi tiết trong thư mục `src/`
   - Comments đầy đủ trong code

---