# 🚀 QUICK START GUIDE - SES Algorithm

Hướng dẫn nhanh để chạy demo thuật toán SES trong 5 phút!

---

## ⚡ QUICK START (3 bước)

### Bước 1: Setup
```bash
make setup
```

### Bước 2: Run Demo
```bash
make run
```

### Bước 3: Analyze
```bash
make analyze
```

🎉 **Done!** Bạn đã chạy thành công thuật toán SES với 15 processes!

---

## 📖 CHI TIẾT TỪNG BƯỚC

### 1️⃣ Setup Project (lần đầu tiên)

```bash
# Cấp quyền thực thi và tạo thư mục
make setup

# Verify cài đặt
make verify
```

**Output mong đợi:**
```
✓ Python OK
✓ Config OK
✓ ses_process.py OK
✓ logs/ OK
```

---

### 2️⃣ Chạy Demo

**Option A: Full Demo (khuyến nghị cho lần đầu)**
```bash
make run
```
- 15 processes
- 150 messages mỗi process
- Tổng: 31,500 messages
- Thời gian: ~5-7 phút

**Option B: Quick Test (để test nhanh)**
```bash
make run-test
```
- 15 processes
- 10 messages mỗi process
- Tổng: 2,100 messages
- Thời gian: ~30 giây

**Option C: Custom Parameters**
```bash
make run-custom MSGS=50 RATE=200
```
- MSGS: số messages gửi đến mỗi process
- RATE: số messages/phút

---

### 3️⃣ Quan sát kết quả

**Real-time monitoring:**
```bash
# Xem log của process 0
make tail PID=0

# Hoặc
tail -f logs/process_0.log
```

**Trong log bạn sẽ thấy:**
- 🟢 `✓ DELIVERED`: Message được deliver ngay
- 🟡 `⊕ BUFFERED`: Message bị buffer (chờ dependencies)
- ⚡ `⚡ UNBUFFERED`: Message được lấy từ buffer để deliver

---

### 4️⃣ Phân tích kết quả

**Xem tổng quan:**
```bash
make analyze
```

**Output:**
```
OVERALL STATISTICS
--------------------------------------------------
Total messages sent:      31,500
Total messages received:  31,500
Total messages delivered: 31,500
Status:                   ✓ SUCCESS - All messages delivered!
```

**Xem chi tiết một process:**
```bash
make analyze-process PID=0
```

**Đếm nhanh:**
```bash
make count
```

---

## 🎯 DEMO CHO TRỢ GIẢNG

### Scenario 1: Demo đầy đủ (10 phút)

```bash
# 1. Clean up
make clean

# 2. Setup
make setup && make verify

# 3. Chạy demo
make run

# Chờ hoàn thành...

# 4. Analyze
make analyze

# 5. Xem chi tiết
make analyze-process PID=0
make tail PID=1
```

### Scenario 2: Demo nhanh (2 phút)

```bash
# Quick test
make run-test

# Analyze ngay
make analyze
```

---

## 💡 TIPS & TRICKS

### Xem logs trong khi chạy:
```bash
# Terminal 1: Run
make run

# Terminal 2: Monitor
watch -n 1 'make log-summary'

# Terminal 3: Tail log
make tail PID=0
```

### Nếu có lỗi port đang được dùng:
```bash
make kill
make check-ports
```

### Chạy lại từ đầu:
```bash
make clean
make setup
make run
```

---

## 📊 HIỂU OUTPUT

### Console Output:

```
[P0] ✓ DELIVERED: Msg#1[P1→P0]
```
- `P0`: Process đang xử lý
- `✓ DELIVERED`: Trạng thái (màu xanh)
- `Msg#1`: Message số 1
- `P1→P0`: Từ P1 đến P0

```
[P0] ⊕ BUFFERED: Msg#5[P2→P0] (size=3)
```
- `⊕ BUFFERED`: Message bị buffer (màu vàng)
- `size=3`: Có 3 messages trong buffer

### Log File Format:

```
[2025-10-23 10:30:45.123] [P0] [INFO] ✓ DELIVERED: Message 1 from P1 to P0
  Message VC:  [2, 1, 0, 0, 0, ...]
  Updated VC:  [2, 2, 0, 0, 0, ...]
  Total from P1: 1
```

---

## 🔧 TROUBLESHOOTING

### Problem: Port already in use
**Solution:**
```bash
make kill
```

### Problem: Permission denied
**Solution:**
```bash
make setup
chmod +x src/*.py
```

### Problem: No module found
**Solution:**
Project chỉ dùng Python standard library, không cần pip install gì!

### Problem: Processes không start
**Solution:**
```bash
# Check Python version (cần 3.7+)
python3 --version

# Verify config
cat config/config.json
```

---

## 📝 CHECKLIST DEMO

Trước khi demo cho trợ giảng:

- [ ] `make clean` - Dọn dẹp
- [ ] `make setup` - Setup lại
- [ ] `make verify` - Verify OK
- [ ] `make run` - Chạy demo
- [ ] Chờ hoàn thành (~5-7 phút)
- [ ] `make analyze` - Phân tích kết quả
- [ ] `make count` - Verify số lượng
- [ ] Mở vài log files để giải thích
- [ ] Giải thích vector clock
- [ ] Giải thích buffering/delivery

---

## 🎥 CHUẨN BỊ VIDEO DEMO

### Script ghi video:

1. **Intro (30s)**
   - "Xin chào, em là [tên], MSSV [số]"
   - "Đây là đồ án SES Algorithm"

2. **Giải thích (2 phút)**
   - Show slide/giấy giải thích thuật toán
   - Vector clock, causal ordering
   - Buffer và delivery

3. **Demo code (3 phút)**
   - Show cấu trúc project: `tree`
   - Show config.json
   - Show một phần code chính

4. **Demo chạy (3 phút)**
   - `make run`
   - Explain output đang xuất hiện
   - Point out buffering events

5. **Phân tích (2 phút)**
   - `make analyze`
   - Explain kết quả
   - Verify tính đúng đắn

6. **Outro (30s)**
   - Tổng kết
   - Cảm ơn

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề:

1. Check README.md đầy đủ
2. Run `make help` để xem commands
3. Check log files trong `logs/`
4. Google error message

---

**Good luck! 🚀**
