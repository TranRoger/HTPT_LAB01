# ĐỒ ÁN SES - THUẬT TOÁN SCHIPER-EGGLI-SANDOZ

**Môn học:** Hệ thống phân tán (HTPT)  
**Đề tài:** Cài đặt thuật toán SES để đảm bảo thứ tự nhân quả trong hệ thống phân tán  
**Deadline:** 19-10-2025

---

## MỤC LỤC

1. [Giới thiệu](#giới-thiệu)
2. [Cài đặt](#cài-đặt)
3. [Cấu trúc dự án](#cấu-trúc-dự-án)
4. [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
5. [Thuật toán SES](#thuật-toán-ses)
6. [Video Demo](#video-demo)
7. [Kết quả thực nghiệm](#kết-quả-thực-nghiệm)

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
chmod +x src/ses_process.py
chmod +x src/launch_all.py
chmod +x src/log_analyzer.py
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
python3 src/launch_all.py [số_message] [messages_per_minute]
```

**Ví dụ:**
```bash
# Mặc định: 150 messages, 100 messages/phút
python3 src/launch_all.py

# Custom: 200 messages, 50 messages/phút
python3 src/launch_all.py 200 50
```

### Cách 2: Chạy từng process riêng lẻ

**Terminal 1:**
```bash
python3 src/ses_process.py 0 150 100
```

**Terminal 2:**
```bash
python3 src/ses_process.py 1 150 100
```

**Terminal 3:**
```bash
python3 src/ses_process.py 2 150 100
```

... và tiếp tục cho đến process 14.

### Phân tích log files:

**Xem tổng quan tất cả processes:**
```bash
python3 src/log_analyzer.py
```

**Xem chi tiết một process cụ thể:**
```bash
python3 src/log_analyzer.py 0
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

## VIDEO DEMO

### Link video demo:
**[Video Demo trên YouTube/Drive]** (Thêm link sau khi quay)

### Nội dung video demo:

1. **Phần 1: Giới thiệu (2 phút)**
   - Giới thiệu đồ án và yêu cầu
   - Giải thích thuật toán SES
   - Cấu trúc dự án

2. **Phần 2: Demo chạy chương trình (5 phút)**
   - Khởi chạy 15 processes
   - Quan sát buffering và delivery
   - Giải thích vector clock
   - Hiển thị dependencies

3. **Phần 3: Phân tích log files (3 phút)**
   - Mở và giải thích log file
   - Chạy log analyzer
   - Thống kê kết quả

4. **Phần 4: Tính đúng đắn (2 phút)**
   - Chứng minh thứ tự nhân quả được đảm bảo
   - Kiểm tra số lượng messages
   - Kết luận

---

## KẾT QUẢ THỰC NGHIỆM

### Cấu hình test:
- 15 processes
- 150 messages/process
- 100 messages/phút
- Tổng: 15 × 14 × 150 = 31,500 messages

### Kết quả mong đợi:

| Process | Sent | Received | Delivered | Buffered |
|---------|------|----------|-----------|----------|
| P0      | 2100 | 2100     | 2100      | ~10-50   |
| P1      | 2100 | 2100     | 2100      | ~10-50   |
| ...     | ...  | ...      | ...       | ...      |
| P14     | 2100 | 2100     | 2100      | ~10-50   |

**Tổng:** 31,500 messages gửi = 31,500 messages nhận = 31,500 messages delivered ✓

### Quan sát buffering:
- Messages thường được buffer khi:
  - Process khởi động chậm hơn
  - Network delay không đồng đều
  - Messages đến không theo thứ tự
  
- Buffer size thường: 0-50 messages
- Max buffer size: ~100 messages (trong điều kiện tệ)

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

## THÔNG TIN LIÊN HỆ

**Sinh viên thực hiện:** [Tên của bạn]  
**MSSV:** [MSSV của bạn]  
**Email:** [Email của bạn]  
**Lớp:** [Lớp của bạn]

---

## LICENSE

Dự án này được tạo cho mục đích học tập trong môn Hệ thống phân tán.

---