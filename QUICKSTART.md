# QUICK START GUIDE

## Chạy nhanh trong 3 bước

### 1. Cài đặt
```bash
make setup
```

### 2. Chạy chương trình
```bash
make run
```

### 3. Xem kết quả
```bash
make analyze
```

---

## Các lệnh thường dùng

### Chạy chương trình:
```bash
# Chạy đầy đủ 15 processes, 150 messages
make run

# Chạy test nhanh với 10 messages
make run-test

# Chạy với tham số custom
make run-custom MSGS=200 RATE=50
```

### Phân tích kết quả:
```bash
# Xem tổng quan
make analyze

# Xem chi tiết process 0
make analyze-process PROC=0

# Xem tóm tắt
make log-summary

# Đếm messages
make count
```

### Xem logs:
```bash
# Liệt kê log files
make logs

# Theo dõi real-time log của process 0
make tail PROC=0
```

### Maintenance:
```bash
# Chạy test suite
make test

# Xóa logs
make clean-logs

# Dọn dẹp toàn bộ
make clean

# Kill tất cả processes đang chạy
make kill

# Kiểm tra ports
make check-ports
```

---

## Demo cho trợ giảng

### Chuẩn bị:
```bash
cd HTPT_LAB01
make clean
make setup
```

### Demo 1: Chạy đầy đủ (recommended)
```bash
make run
```
- Quan sát 15 terminal windows
- Chỉ ra buffering (màu vàng) và delivery (màu xanh)
- Giải thích vector clock

### Demo 2: Phân tích logs
```bash
make analyze
```
- Hiển thị thống kê tổng quan
- Số messages sent/received/delivered
- Số messages buffered

### Demo 3: Chi tiết một process
```bash
make analyze-process PROC=0
```
- Xem chi tiết process 0
- Danh sách buffering events

### Demo 4: Verify tính đúng đắn
```bash
# Kiểm tra mỗi process deliver 2100 messages
for i in {0..14}; do
  count=$(grep -c "DELIVERED" logs/process_$i.log)
  echo "Process $i: $count messages"
done

# Kết quả phải là: 2100 cho mỗi process
```

---

## Xử lý lỗi nhanh

### Lỗi: Port already in use
```bash
make kill
make clean
# Đợi 2-3 giây
make run
```

### Lỗi: Permission denied
```bash
make setup
```

### Lỗi: Connection refused
```bash
# Đảm bảo tất cả processes đã start
# Chờ 2-3 giây sau khi launch_all.py
```

---

## Đọc thêm

- **README.md**: Hướng dẫn đầy đủ
- **docs/THIET_KE.md**: Tài liệu thiết kế chi tiết
- **docs/VIDEO_DEMO.md**: Script cho video demo
- **docs/HUONG_DAN_NOP_BAI.md**: Hướng dẫn nộp bài

---

## Tips

1. **Chạy test trước khi demo:**
   ```bash
   make test
   ```

2. **Xem log real-time khi chạy:**
   ```bash
   # Terminal 1: Chạy chương trình
   make run
   
   # Terminal 2: Xem log
   make tail PROC=0
   ```

3. **Kiểm tra kết quả nhanh:**
   ```bash
   make count
   make log-summary
   ```

4. **Clean trước mỗi lần chạy:**
   ```bash
   make clean-logs
   ```

---