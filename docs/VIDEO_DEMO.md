# VIDEO DEMO - HƯỚNG DẪN VÀ SCRIPT

## 📹 THÔNG TIN VIDEO

**Thời lượng dự kiến:** 12-15 phút  
**Định dạng:** MP4, 1080p  
**Platform upload:** YouTube (Unlisted) hoặc Google Drive  
**Link video:** [Thêm link sau khi upload]

---

## 🎬 SCRIPT DEMO

### PHẦN 1: GIỚI THIỆU (2 phút)

**[Scene: Màn hình desktop, mở slide hoặc README]**

> Xin chào, em là [Tên - MSSV], hôm nay em xin được trình bày đồ án cài đặt thuật toán SES trong môn Hệ thống phân tán.

**[Hiển thị đề bài]**

> Đề bài yêu cầu:
> - Cài đặt 15 processes chạy đồng thời
> - Mỗi process gửi 150 messages cho mỗi process khác
> - Hiển thị rõ ràng việc buffering và delivery
> - Ghi log chi tiết

**[Hiển thị diagram thuật toán SES]**

> Thuật toán SES sử dụng Vector Clock để đảm bảo thứ tự nhân quả của messages.
> Nguyên lý cơ bản:
> - Mỗi process duy trì một vector clock
> - Message chỉ được deliver khi thỏa mãn điều kiện nhân quả
> - Messages vi phạm sẽ được buffer cho đến khi dependencies đầy đủ

**[Hiển thị cấu trúc project]**

> Dự án của em bao gồm:
> - ses_process.py: Core implementation
> - config.json: Configuration cho 15 processes
> - launch_all.py: Script để khởi chạy tất cả processes
> - log_analyzer.py: Tool phân tích kết quả

---

### PHẦN 2: DEMO CODE (3 phút)

**[Mở VSCode, hiển thị ses_process.py]**

> Đầu tiên, em xin giới thiệu cấu trúc code chính.

**[Scroll đến VectorClock class]**

> Đây là class VectorClock, dùng để theo dõi quan hệ nhân quả:
> - increment(): Tăng clock khi gửi message
> - update(): Cập nhật clock khi nhận message
> - Thread-safe với lock

**[Scroll đến can_deliver method]**

> Đây là hàm kiểm tra xem message có thể deliver không:
> - Điều kiện 1: Message timestamp[sender] = VC[receiver][sender] + 1
> - Điều kiện 2: Với mọi process khác, timestamp <= VC[receiver]
> - Nếu vi phạm bất kỳ điều kiện nào, message sẽ được buffer

**[Scroll đến deliver_message method]**

> Khi deliver message:
> - Update vector clock bằng cách lấy max của từng phần tử
> - Tăng clock của sender
> - Ghi log chi tiết
> - Hiển thị trên console với màu sắc

**[Hiển thị config.json]**

> File config chứa thông tin 15 processes:
> - Process ID từ 0 đến 14
> - Mỗi process có host và port riêng
> - Ở đây em chạy trên localhost với port 5000-5014

---

### PHẦN 3: DEMO CHẠY CHƯƠNG TRÌNH (5 phút)

**[Terminal, hiển thị pwd và ls]**

```bash
pwd  # /path/to/HTPT_LAB01
ls -la
```

> Bây giờ em sẽ chạy chương trình. Em sử dụng script launch_all.py để khởi động cả 15 processes cùng lúc.

**[Chạy launch_all.py]**

```bash
python3 src/launch_all.py 150 100
```

> Ở đây:
> - 150 là số messages mỗi process gửi cho mỗi process khác
> - 100 là tốc độ 100 messages/phút

**[Quan sát các terminal windows mở ra]**

> Như các bạn thấy, 15 processes đã được khởi động, mỗi process trong một terminal riêng.

**[Focus vào một terminal, ví dụ Process 0]**

> Hãy quan sát Process 0:

**[Chỉ vào console output]**

> - Màu xanh: Message được deliver thành công
> - Màu vàng: Message bị buffer
> - Mỗi dòng hiển thị Vector Clock và lý do

**[Scroll log, chỉ vào một buffered message]**

> Ví dụ ở đây, message từ P3 bị buffer vì:
> "Waiting for message #1 from P3 (got #2)"
> Nghĩa là Process 0 nhận message số 2 từ P3, nhưng chưa nhận message số 1
> Theo thuật toán SES, message phải được deliver theo thứ tự

**[Đợi một chút, chỉ vào khi message được unbuffer]**

> Và khi message #1 đến, message #2 được unbuffer và deliver:
> "⚡ UNBUFFERED: Message 2 from P3"
> "✓ DELIVERED: Message 2 from P3"

**[Chuyển sang Process khác]**

> Process khác cũng hoạt động tương tự, tất cả đều đảm bảo thứ tự nhân quả.

---

### PHẦN 4: PHÂN TÍCH LOG FILES (3 phút)

**[Đợi chương trình chạy xong hoặc Ctrl+C để dừng]**

> Sau khi chạy xong, ta có thể phân tích log files.

**[Mở thư mục logs]**

```bash
ls -lh logs/
```

> Mỗi process có một log file riêng, kích thước tùy thuộc vào số lượng messages.

**[Mở một log file]**

```bash
head -30 logs/process_0.log
```

> Log file ghi lại mọi sự kiện:
> - Thời gian chính xác đến microsecond
> - Process ID và level (INFO, WARNING, ERROR)
> - Chi tiết về message: nội dung, vector clock, sender, receiver
> - Lý do buffering nếu có

**[Chạy log_analyzer]**

```bash
python3 src/log_analyzer.py
```

> Tool phân tích log cung cấp thống kê tổng quan:
> - Tổng số messages sent, received, delivered
> - Thống kê từng process
> - Số lượng messages bị buffer

**[Chỉ vào output]**

> Như các bạn thấy:
> - Tổng messages sent: 31,500 (15 × 14 × 150)
> - Tổng messages received: 31,500
> - Tổng messages delivered: 31,500
> - Điều này chứng minh không có message nào bị mất

**[Chạy với specific process]**

```bash
python3 src/log_analyzer.py 0
```

> Ta cũng có thể xem chi tiết một process cụ thể:
> - Số messages gửi/nhận/deliver từng process khác
> - Danh sách buffering events
> - Vector clock cuối cùng

---

### PHẦN 5: CHỨNG MINH TÍNH ĐÚNG ĐẮN (2 phút)

**[Terminal, chạy verification commands]**

> Bây giờ em sẽ chứng minh tính đúng đắn của chương trình.

**[Kiểm tra số lượng messages delivered]**

```bash
for i in {0..14}; do
  count=$(grep "DELIVERED" logs/process_$i.log | wc -l)
  echo "Process $i: $count messages delivered"
done
```

> Mỗi process phải deliver đúng 2,100 messages:
> - 14 processes khác × 150 messages = 2,100

**[Tất cả đều show 2100]**

> Perfect! Tất cả processes đều deliver đúng số lượng.

**[Kiểm tra causal ordering]**

> Về causal ordering, em có thể chứng minh qua log:

```bash
grep -A 2 "BUFFERED.*from P5" logs/process_0.log | head -20
```

> Ở đây ta thấy:
> - Message bị buffer khi điều kiện không thỏa mãn
> - Lý do buffer rất rõ ràng: "Waiting for message #X"
> - Sau đó message được unbuffer đúng thứ tự

**[Hiển thị một ví dụ cụ thể từ log]**

> Ví dụ cụ thể:
> 1. P0 nhận message #5 từ P2
> 2. Nhưng P0 mới chỉ có message #3 từ P2
> 3. → Message #5 bị buffer
> 4. Khi P0 nhận #4, nó được deliver
> 5. Sau đó #5 được unbuffer và deliver
> 
> Đây chính là causal ordering!

---

### PHẦN 6: TÍNH NĂNG BỔ SUNG (1 phút)

**[Chạy một process riêng lẻ]**

```bash
python3 src/ses_process.py 0 10 50
```

> Chương trình cũng hỗ trợ chạy từng process riêng lẻ để dễ debug.

**[Trong khi chạy, nhấn 's']**

```
> s
```

> Nhấn 's' để xem statistics real-time:
> - Vector clock hiện tại
> - Số messages đã gửi/nhận/deliver
> - Buffer size, max buffer size

**[Nhấn 'q']**

```
> q
```

> Nhấn 'q' để thoát gracefully.

---

### PHẦN 7: KẾT LUẬN (1 phút)

**[Quay lại slide hoặc summary]**

> Tóm lại, đồ án của em đã:
> 
> ✅ Cài đặt đầy đủ thuật toán SES với vector clock
> ✅ 15 processes chạy đồng thời, gửi 150 messages cho nhau
> ✅ Hiển thị rõ ràng buffering và delivery với màu sắc
> ✅ Log file chi tiết với timestamp và lý do buffer
> ✅ Đảm bảo causal ordering 100%
> ✅ Không mất message, không duplicate
> ✅ Cung cấp tools phân tích và verification

> Các đặc điểm nổi bật:
> - Thread-safe với proper locking
> - Real-time console display với colors
> - Chi tiết log từng sự kiện
> - Dễ dàng config và extend
> - Có thể chạy trên nhiều máy thật (chỉ cần đổi IP trong config)

> Em xin cảm ơn thầy và các bạn đã theo dõi!

---

## 📝 CHECKLIST TRƯỚC KHI QUAY

### Chuẩn bị:
- [ ] Clean workspace (xóa logs cũ)
- [ ] Test chạy thử trước 2-3 lần
- [ ] Chuẩn bị script và câu nói
- [ ] Kiểm tra micro, âm thanh rõ ràng
- [ ] Screen resolution: 1080p
- [ ] Font size đủ lớn để đọc
- [ ] Terminal colors rõ ràng

### Trong khi quay:
- [ ] Nói chậm rãi, rõ ràng
- [ ] Giải thích mỗi bước đang làm gì
- [ ] Point out các điểm quan trọng
- [ ] Không nói quá nhanh hoặc quá chậm
- [ ] Tránh um... ah... nhiều lần

### Sau khi quay:
- [ ] Review video, check âm thanh/hình ảnh
- [ ] Add subtitle nếu cần
- [ ] Upload lên YouTube/Drive
- [ ] Set permission phù hợp
- [ ] Copy link vào README.md
- [ ] Test link có mở được không

---

## 🎥 SOFTWARE ĐỀ XUẤT

### Screen Recording:
- **Linux:** SimpleScreenRecorder, OBS Studio
- **Windows:** OBS Studio, Camtasia
- **Mac:** QuickTime, OBS Studio

### Video Editing (optional):
- DaVinci Resolve (free)
- OpenShot
- Kdenlive

### Cài đặt OBS Studio (khuyến nghị):

```bash
# Ubuntu/Debian
sudo apt install obs-studio

# Fedora
sudo dnf install obs-studio

# Arch
sudo pacman -S obs-studio
```

**OBS Settings:**
- Output: Recording
- Format: MP4
- Encoder: x264
- Rate Control: CBR
- Bitrate: 6000 Kbps
- Keyframe: 2s
- Preset: veryfast
- Audio: 192 Kbps

---

## 📊 VIDEO STRUCTURE

```
00:00 - 02:00  │ Giới thiệu đề bài và thuật toán
02:00 - 05:00  │ Giải thích code
05:00 - 10:00  │ Demo chạy chương trình
10:00 - 13:00  │ Phân tích log files
13:00 - 15:00  │ Chứng minh tính đúng đắn
15:00 - 16:00  │ Kết luận
```

---

**Chúc bạn quay video thành công! 🎬**
