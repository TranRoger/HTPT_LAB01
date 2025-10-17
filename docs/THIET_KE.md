# TÀI LIỆU THIẾT KẾ - ĐỒ ÁN SES

## 1. KIẾN TRÚC HỆ THỐNG

### 1.1 Tổng quan kiến trúc

```
┌─────────────────────────────────────────────────────────┐
│           Hệ thống phân tán 15 processes                │
└─────────────────────────────────────────────────────────┘
                           │
      ┌────────────────────┼────────────────────┐
      │                    │                    │
   Process 0           Process 1    ...     Process 14
   ┌────────┐         ┌────────┐           ┌────────┐
   │VC: [..]│         │VC: [..]│           │VC: [..]│
   │Buffer  │◄───────►│Buffer  │◄─────────►│Buffer  │
   │Sender  │         │Sender  │           │Sender  │
   │Receiver│         │Receiver│           │Receiver│
   └────────┘         └────────┘           └────────┘
      :5000             :5001                 :5014
```

### 1.2 Các thành phần chính

#### **Process (SESProcess)**
- Mỗi process là một thực thể độc lập chạy trên một thread riêng
- Có địa chỉ IP và port riêng (localhost:5000-5014)
- Chức năng:
  - Gửi messages đến các process khác
  - Nhận và xử lý messages từ các process khác
  - Quản lý vector clock
  - Buffer messages chưa thể deliver
  - Ghi log chi tiết

#### **Vector Clock**
- Cấu trúc: Mảng integers có kích thước = số processes
- Mục đích: Theo dõi quan hệ nhân quả giữa các sự kiện
- Thread-safe với mutex lock

#### **Message**
- Cấu trúc:
  ```python
  {
    'sender_id': int,
    'receiver_id': int,
    'content': str,
    'timestamp': List[int],  # Vector clock
    'seq_num': int
  }
  ```

#### **Buffer**
- Lưu trữ messages chưa thể deliver
- Thread-safe với lock
- FIFO ordering

---

## 2. THIẾT KẾ THUẬT TOÁN SES

### 2.1 Cấu trúc dữ liệu

```python
class VectorClock:
    - process_id: int
    - clock: List[int]  # Vector clock array
    - lock: threading.Lock
    
    Methods:
    + increment()
    + update(received_clock)
    + get_clock()

class Message:
    - sender_id: int
    - receiver_id: int
    - content: str
    - timestamp: List[int]
    - seq_num: int
    
    Methods:
    + to_dict()
    + from_dict()

class SESProcess:
    - process_id: int
    - vector_clock: VectorClock
    - buffer: List[Message]
    - config: dict
    
    Methods:
    + can_deliver(msg)
    + deliver_message(msg)
    + handle_received_message(msg)
    + send_message(receiver_id, content)
```

### 2.2 Luồng hoạt động

#### **A. Gửi message**
```
1. Process i muốn gửi message
2. Increment VC[i][i]++
3. Tạo message với timestamp = VC[i]
4. Gửi qua socket tới process j
5. Log: "→ SENT"
```

#### **B. Nhận message**
```
1. Process j nhận message M từ process i
2. Log: "← RECEIVED"
3. Kiểm tra can_deliver(M):
   a. Nếu TRUE:
      - deliver_message(M)
      - Update VC
      - Log: "✓ DELIVERED"
   b. Nếu FALSE:
      - buffer.append(M)
      - Log: "⊕ BUFFERED"
4. try_deliver_buffered()
```

#### **C. Kiểm tra delivery (can_deliver)**
```python
def can_deliver(msg):
    # Condition 1: Message tiếp theo từ sender
    if msg.timestamp[sender] != VC[receiver][sender] + 1:
        return False
    
    # Condition 2: Không có dependency thiếu
    for k in range(num_processes):
        if k != sender:
            if msg.timestamp[k] > VC[receiver][k]:
                return False
    
    return True
```

#### **D. Deliver message**
```python
def deliver_message(msg):
    # Update vector clock
    for i in range(num_processes):
        if i != process_id:
            VC[i] = max(VC[i], msg.timestamp[i])
    
    VC[msg.sender_id] += 1
    
    # Process message
    delivered_messages.append(msg)
    
    # Log
    logger.info("✓ DELIVERED")
```

#### **E. Try deliver buffered messages**
```python
def try_deliver_buffered():
    delivered_any = True
    while delivered_any:
        delivered_any = False
        for msg in buffer:
            if can_deliver(msg):
                buffer.remove(msg)
                deliver_message(msg)
                delivered_any = True
                break
```

---

## 3. THIẾT KẾ COMMUNICATION

### 3.1 Socket Programming

#### **Server Side (Receiver)**
```python
# Khởi động server
server_socket = socket.socket(AF_INET, SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(20)

# Accept connections
while running:
    client_socket, addr = server_socket.accept()
    thread = Thread(target=handle_client, args=(client_socket,))
    thread.start()
```

#### **Client Side (Sender)**
```python
# Gửi message
sock = socket.socket(AF_INET, SOCK_STREAM)
sock.connect((receiver_host, receiver_port))
sock.sendall(json.dumps(message).encode())
sock.close()
```

### 3.2 Message Format

Messages được serialize thành JSON:
```json
{
  "sender_id": 0,
  "receiver_id": 1,
  "content": "Message 1 from P0 to P1",
  "timestamp": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  "seq_num": 1
}
```

### 3.3 Threading Model

Mỗi process có nhiều threads:
- **1 Server thread:** Lắng nghe incoming connections
- **N Client handler threads:** Xử lý mỗi connection (N = số connections đồng thời)
- **14 Sender threads:** Gửi messages tới 14 processes khác
- **1 Main thread:** Quản lý và hiển thị thống kê

```
Process i
├── Main Thread
│   └── Statistics & User Input
├── Server Thread
│   └── Accept connections
├── Handler Threads (dynamic)
│   ├── Thread 1: Handle connection from P0
│   ├── Thread 2: Handle connection from P2
│   └── ...
└── Sender Threads
    ├── Thread 1: Send to P0
    ├── Thread 2: Send to P1
    └── ...
```

---

## 4. LOGGING SYSTEM

### 4.1 Log Levels

- **DEBUG:** Chi tiết về mọi message (sent, received)
- **INFO:** Delivery và buffer events
- **WARNING:** Buffering với lý do
- **ERROR:** Lỗi network, exceptions

### 4.2 Log Format

```
[Timestamp] [Process-ID] [Level] Message
```

**Ví dụ:**
```
[2025-10-17 10:30:45.123456] [P0] [INFO] → SENT: Message 1 to P1, VC: [1,0,0,...]
[2025-10-17 10:30:45.234567] [P1] [INFO] ← RECEIVED: Message 1 from P0
[2025-10-17 10:30:45.234890] [P1] [INFO] ✓ DELIVERED: Message 1 from P0
[2025-10-17 10:30:45.345678] [P1] [WARNING] ⊕ BUFFERED: Message 3 from P2
[2025-10-17 10:30:45.345890] [P1] [WARNING]   └─ Waiting for message #1 from P2
```

### 4.3 Log Files

- **Location:** `logs/process_<id>.log`
- **Format:** Plain text
- **Size:** Không giới hạn (cho demo)
- **Rotation:** Không (cho demo, overwrite mỗi lần chạy)

---

## 5. CONFIGURATION

### 5.1 Config File Format

File: `config/config.json`

```json
{
  "processes": [
    {"id": 0, "host": "127.0.0.1", "port": 5000},
    {"id": 1, "host": "127.0.0.1", "port": 5001},
    ...
  ]
}
```

### 5.2 Parameters

- **host:** IP address (localhost cho single machine, IP thực cho multi-machine)
- **port:** Port number (5000-5014)
- **id:** Process identifier (0-14)

### 5.3 Runtime Parameters

Khi khởi chạy:
```bash
python3 ses_process.py <process_id> [num_messages] [messages_per_minute]
```

- **process_id:** 0-14 (required)
- **num_messages:** Số messages gửi cho mỗi process (default: 150)
- **messages_per_minute:** Tốc độ gửi (default: 100)

---

## 6. ĐẢM BẢO TÍNH ĐÚNG ĐẮN

### 6.1 Causal Ordering

**Định nghĩa:** Nếu `send(m1) → send(m2)` thì `deliver(m1) → deliver(m2)`

**Cài đặt:**
- Vector clock đảm bảo quan hệ happens-before
- Buffering messages vi phạm điều kiện delivery
- Unbuffering khi dependencies thỏa mãn

### 6.2 No Message Loss

**Đảm bảo:**
- TCP socket (reliable transport)
- Retry mechanism có thể thêm (không bắt buộc cho demo)
- Log tracking: sent = received = delivered

### 6.3 No Duplication

**Đảm bảo:**
- Sequence number cho mỗi message
- Không delivery message 2 lần
- Buffer check trước khi add

### 6.4 Test Cases

**Test 1: Sequential sending**
```
P0 gửi M1, M2, M3 đến P1 tuần tự
→ P1 phải deliver theo thứ tự M1, M2, M3
```

**Test 2: Concurrent sending**
```
P0 gửi M1 đến P1
P2 gửi M2 đến P1 (phụ thuộc M1)
→ P1 phải deliver M1 trước M2
```

**Test 3: Buffering**
```
P0 gửi M3 đến P1 (timestamp=[3,0,0])
P1 hiện tại VC=[0,0,0]
→ M3 phải được buffer
→ Khi P1 nhận M1, M2 từ P0, M3 được deliver
```

---

## 7. PERFORMANCE CONSIDERATIONS

### 7.1 Bottlenecks

- **Network latency:** TCP socket overhead
- **Buffering overhead:** Linear search trong buffer
- **Lock contention:** Vector clock và buffer locks

### 7.2 Optimizations

**Hiện tại:**
- Thread pool cho connections
- Lock granularity nhỏ
- Batch delivery từ buffer

**Có thể cải thiện:**
- Priority queue cho buffer (sort by timestamp)
- Message batching
- Asynchronous I/O
- Distributed deployment

### 7.3 Scalability

**Hiện tại:** 15 processes
**Scalability:**
- Vector clock size: O(N)
- Message overhead: O(N)
- Buffer check: O(N × buffer_size)

**Giới hạn:** ~100 processes với cài đặt hiện tại

---

## 8. ERROR HANDLING

### 8.1 Network Errors

```python
try:
    sock.connect((host, port))
    sock.sendall(data)
except ConnectionRefusedError:
    logger.error("Connection refused")
except socket.timeout:
    logger.error("Connection timeout")
except Exception as e:
    logger.error(f"Network error: {e}")
```

### 8.2 Thread Safety

- **Locks:** Vector clock, buffer, delivered messages
- **Thread-safe collections:** Threading.Lock
- **Atomic operations:** Increment, append

### 8.3 Graceful Shutdown

```python
try:
    process.run()
except KeyboardInterrupt:
    print("Shutting down...")
finally:
    process.stop()
    # Close sockets
    # Join threads
```

---

## 9. TESTING STRATEGY

### 9.1 Unit Tests

- Vector clock operations
- Message serialization/deserialization
- Delivery condition checking

### 9.2 Integration Tests

- Process communication
- Buffering và delivery
- Multiple processes

### 9.3 System Tests

- 15 processes full run
- Message counting
- Log verification

### 9.4 Verification

```bash
# Kiểm tra số messages
for i in {0..14}; do
  echo "Process $i:"
  grep "DELIVERED" logs/process_$i.log | wc -l
done

# Kết quả mong đợi: 2100 messages/process
```

---

## 10. FUTURE ENHANCEMENTS

### 10.1 Features

- [ ] Web-based monitoring dashboard
- [ ] Visualize vector clocks graphically
- [ ] Message replay capability
- [ ] Fault tolerance (process crash recovery)
- [ ] Dynamic process join/leave

### 10.2 Performance

- [ ] Message compression
- [ ] Protocol optimization
- [ ] Better buffer management
- [ ] Metrics collection

### 10.3 Deployment

- [ ] Docker containers
- [ ] Kubernetes orchestration
- [ ] Multi-machine setup automation
- [ ] Cloud deployment (AWS, GCP, Azure)

---

## 11. REFERENCES

### 11.1 Papers

1. Schiper, E. G., Eggli, J., & Sandoz, A. (1989). "A New Algorithm to Implement Causal Ordering"
2. Lamport, L. (1978). "Time, Clocks, and the Ordering of Events in a Distributed System"
3. Fidge, C. J. (1988). "Timestamps in Message-Passing Systems That Preserve the Partial Ordering"

### 11.2 Books

1. Distributed Systems: Principles and Paradigms (Tanenbaum & Van Steen)
2. Distributed Algorithms (Nancy Lynch)

### 11.3 Online Resources

- Wikipedia: Vector Clock
- Distributed Systems Course Notes
- Python Socket Programming Documentation

---

**Tài liệu thiết kế này mô tả chi tiết kiến trúc và cài đặt của đồ án SES.**
