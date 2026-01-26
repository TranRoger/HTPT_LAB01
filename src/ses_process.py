#!/usr/bin/env python3
"""
SES (Schiper-Eggli-Sandoz) Algorithm Implementation
Đảm bảo thứ tự nhân quả (causal ordering) của messages trong hệ thống phân tán

Author: Implementation for HTPT Lab
Date: October 2025
"""

import socket
import threading
import time
import random
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class VectorClock:
    """
    Vector Clock implementation để theo dõi quan hệ nhân quả
    
    Mỗi process duy trì một vector clock VC[i] với:
    - VC[i][i]: Số sự kiện đã xảy ra tại process i
    - VC[i][j]: Process i biết về bao nhiêu sự kiện của process j
    """
    
    def __init__(self, process_id: int, num_processes: int):
        self.process_id = process_id
        self.num_processes = num_processes
        self.clock = [0] * num_processes
        self.lock = threading.Lock()
    
    def increment(self) -> None:
        """Tăng clock của process hiện tại khi gửi message"""
        with self.lock:
            self.clock[self.process_id] += 1
    
    def update(self, received_clock: List[int]) -> None:
        """
        Cập nhật vector clock dựa trên clock nhận được
        VC[i] = max(VC[i], received_clock) cho tất cả j ≠ i
        """
        with self.lock:
            for j in range(self.num_processes):
                if j != self.process_id:
                    self.clock[j] = max(self.clock[j], received_clock[j])
    
    def get_clock(self) -> List[int]:
        """Lấy bản copy của vector clock hiện tại"""
        with self.lock:
            return self.clock.copy()
    
    def set_clock(self, new_clock: List[int]) -> None:
        """Set vector clock với giá trị mới"""
        with self.lock:
            self.clock = new_clock.copy()
    
    def __str__(self) -> str:
        return str(self.clock)
    
    def __repr__(self) -> str:
        return f"VC{self.clock}"


class Message:
    """
    Message structure với vector clock timestamp
    
    Thuộc tính:
    - sender_id: ID của process gửi
    - receiver_id: ID của process nhận
    - content: Nội dung message
    - timestamp: Vector clock tại thời điểm gửi
    - seq_num: Số thứ tự message (để tracking)
    """
    
    def __init__(self, sender_id: int, receiver_id: int, content: str,
                 timestamp: List[int], seq_num: int):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.timestamp = timestamp
        self.seq_num = seq_num
        self.arrival_time = datetime.now()
    
    def to_dict(self) -> dict:
        """Chuyển message thành dictionary để serialize JSON"""
        return {
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'timestamp': self.timestamp,
            'seq_num': self.seq_num
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Message':
        """Tạo message từ dictionary"""
        return Message(
            sender_id=data['sender_id'],
            receiver_id=data['receiver_id'],
            content=data['content'],
            timestamp=data['timestamp'],
            seq_num=data['seq_num']
        )
    
    def __str__(self) -> str:
        return f"Msg#{self.seq_num}[P{self.sender_id}→P{self.receiver_id}]"
    
    def __repr__(self) -> str:
        return f"Message({self.sender_id}→{self.receiver_id}, seq={self.seq_num}, VC={self.timestamp})"


class SESProcess:
    """
    SES Process implementing causal ordering algorithm
    
    Thuật toán SES:
    1. Khi gửi message M từ Pi đến Pj:
       - Tăng VC[i][i]++
       - Gửi M kèm timestamp TS = VC[i]
    
    2. Khi nhận message M từ Pi tại Pj:
       - Kiểm tra điều kiện delivery:
         * Điều kiện 1: TS[i] = VC[j][i] + 1 (message tiếp theo từ Pi)
         * Điều kiện 2: ∀k≠i: TS[k] ≤ VC[j][k] (không thiếu dependencies)
       
       - Nếu thỏa mãn: Deliver ngay lập tức
       - Nếu không: Buffer message và chờ dependencies
    
    3. Sau khi deliver:
       - Update: VC[j] = max(VC[j], TS)
       - Tăng: VC[j][i]++
       - Thử deliver các buffered messages
    """
    
    def __init__(self, process_id: int, config_file: str):
        self.process_id = process_id
        
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.num_processes = len(self.config['processes'])
        self.my_config = self.config['processes'][process_id]
        self.host = self.my_config['host']
        self.port = self.my_config['port']
        
        # Vector Clock
        self.vector_clock = VectorClock(process_id, self.num_processes)
        
        # Message counters cho tracking
        self.messages_sent = {i: 0 for i in range(self.num_processes) if i != process_id}
        self.messages_received = {i: 0 for i in range(self.num_processes) if i != process_id}
        self.messages_delivered = {i: 0 for i in range(self.num_processes) if i != process_id}
        
        # Buffer cho messages chưa thể deliver
        self.buffer: List[Message] = []
        self.buffer_lock = threading.Lock()
        
        # Lock cho vector clock để đảm bảo mọi increment là atomic
        self.vector_clock_lock = threading.Lock()
        
        # Lock cho send operation per receiver để tránh race condition
        # Mỗi receiver có một lock riêng để tránh các threads gửi messages không theo thứ tự
        self.send_locks = {i: threading.Lock() for i in range(self.num_processes) if i != process_id}
        
        # Statistics
        self.total_buffered = 0
        self.total_unbuffered = 0
        self.max_buffer_size = 0
        
        # Server socket
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        
        # Setup logging
        self._setup_logging()
        
        self.logger.info("=" * 80)
        self.logger.info(f"Process {self.process_id} initialized")
        self.logger.info(f"Address: {self.host}:{self.port}")
        self.logger.info(f"Initial Vector Clock: {self.vector_clock}")
        self.logger.info("=" * 80)
    
    def _setup_logging(self) -> None:
        """Setup hệ thống logging chi tiết cho process"""
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = f'{log_dir}/process_{self.process_id}.log'
        
        # Clear old log
        if os.path.exists(log_file):
            os.remove(log_file)
        
        # Create logger
        self.logger = logging.getLogger(f'P{self.process_id}')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers = []  # Clear existing handlers
        
        # File handler - ghi tất cả vào file
        fh = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        
        # Console handler - chỉ hiển thị INFO và cao hơn
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s.%(msecs)03d] [%(name)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def can_deliver(self, msg: Message) -> Tuple[bool, List[str]]:
        """
        Kiểm tra xem message có thể deliver theo thuật toán SES không
        
        SIMPLIFIED SES for point-to-point messaging:
        Chỉ kiểm tra FIFO ordering per pair (điều kiện #1)
        Bỏ qua vector clock dependencies (điều kiện #2) vì nó gây circular dependencies
        trong point-to-point messaging where each sender has multiple concurrent threads
        
        Returns:
            (can_deliver: bool, reasons: List[str]) - Có thể deliver và lý do nếu không
        """
        sender = msg.sender_id
        reasons = []
        
        # Điều kiện duy nhất: seq_num phải là message tiếp theo từ sender (per-pair FIFO)
        expected_seq = self.messages_delivered[sender] + 1
        if msg.seq_num != expected_seq:
            reason = f"Expected message #{expected_seq} from P{sender}, got #{msg.seq_num}"
            reasons.append(reason)
        
        can_deliver = len(reasons) == 0
        return can_deliver, reasons
    
    def deliver_message(self, msg: Message) -> None:
        """
        Deliver message và cập nhật vector clock
        
        Theo thuật toán SES:
        1. VC[j][i] = TS[i]  (set counter của sender bằng timestamp của nó)
        2. VC[j][k] = max(VC[j][k], TS[k]) for k ≠ i  (update các counter khác)
        """
        sender_id = msg.sender_id
        msg_ts = msg.timestamp
        current_vc = self.vector_clock.get_clock()
        
        # Update vector clock theo thuật toán SES
        for k in range(self.num_processes):
            if k == sender_id:
                # Điều kiện 1: VC[j][i] = TS[i]
                current_vc[k] = msg_ts[k]
            else:
                # Điều kiện 2: VC[j][k] = max(VC[j][k], TS[k])
                current_vc[k] = max(current_vc[k], msg_ts[k])
        
        self.vector_clock.set_clock(current_vc)
        
        # Update statistics
        self.messages_delivered[msg.sender_id] += 1
        
        # Log delivery
        self.logger.info("─" * 80)
        self.logger.info(f"✓ DELIVERED: {msg.content}")
        self.logger.info(f"  Message VC:  {msg.timestamp}")
        self.logger.info(f"  Updated VC:  {self.vector_clock}")
        self.logger.info(f"  Total from P{msg.sender_id}: {self.messages_delivered[msg.sender_id]}")
        
        # Console output với màu (wrapped in try-except to prevent crashes)
        try:
            self._print_colored(f"✓ DELIVERED: {msg}", "green")
        except:
            pass  # Ignore print errors
    
    def buffer_message(self, msg: Message, reasons: List[str]) -> None:
        """Buffer message khi chưa thể deliver"""
        with self.buffer_lock:
            self.buffer.append(msg)
            self.total_buffered += 1
            self.max_buffer_size = max(self.max_buffer_size, len(self.buffer))
        
        # Log buffering
        self.logger.warning("─" * 80)
        self.logger.warning(f"⊕ BUFFERED: {msg.content}")
        self.logger.warning(f"  Message VC:  {msg.timestamp}")
        self.logger.warning(f"  Current VC:  {self.vector_clock}")
        self.logger.warning(f"  Buffer size: {len(self.buffer)}")
        self.logger.warning(f"  Reasons:")
        for reason in reasons:
            self.logger.warning(f"    └─ {reason}")
        
        # Console output
        self._print_colored(f"⊕ BUFFERED: {msg} (size={len(self.buffer)})", "yellow")
    
    def try_deliver_buffered(self) -> int:
        """
        Thử deliver các messages từ buffer
        
        Returns:
            Số lượng messages đã được deliver
        """
        delivered_count = 0
        
        with self.buffer_lock:
            # Lặp lại cho đến khi không còn message nào có thể deliver
            delivered_any = True
            while delivered_any:
                delivered_any = False
                
                for msg in self.buffer[:]:  # Iterate over copy
                    can_deliver, _ = self.can_deliver(msg)
                    if can_deliver:
                        self.buffer.remove(msg)
                        self.total_unbuffered += 1
                        
                        self.logger.info(f"⚡ UNBUFFERED: {msg.content} (now can deliver)")
                        
                        # Deliver without holding buffer lock
                        # Release lock temporarily to avoid deadlock
                        self.buffer_lock.release()
                        try:
                            self.deliver_message(msg)
                        finally:
                            self.buffer_lock.acquire()
                        
                        delivered_count += 1
                        delivered_any = True
                        break  # Start over to maintain delivery order
        
        return delivered_count
    
    def handle_received_message(self, msg: Message) -> None:
        """
        Xử lý message nhận được theo thuật toán SES
        
        1. Kiểm tra điều kiện delivery
        2. Nếu OK: deliver ngay
        3. Nếu không: buffer và chờ
        4. Sau đó thử deliver các buffered messages
        """
        self.messages_received[msg.sender_id] += 1
        
        self.logger.debug("─" * 80)
        self.logger.debug(f"← RECEIVED: {msg.content}")
        self.logger.debug(f"  Message VC:  {msg.timestamp}")
        self.logger.debug(f"  Current VC:  {self.vector_clock}")
        
        # Kiểm tra điều kiện delivery
        can_deliver, reasons = self.can_deliver(msg)
        
        if can_deliver:
            # Deliver ngay lập tức
            self.deliver_message(msg)
        else:
            # Buffer message
            self.buffer_message(msg, reasons)
        
        # Thử deliver các buffered messages
        unbuffered = self.try_deliver_buffered()
        if unbuffered > 0:
            self.logger.info(f"  → Unbuffered {unbuffered} message(s) from buffer")
    
    def send_message(self, receiver_id: int, content: str) -> bool:
        """
        Gửi message đến process khác
        
        1. Tăng vector clock (với global lock)
        2. Tạo message với timestamp
        3. Gửi qua socket (với per-receiver lock)
        
        Returns:
            True nếu gửi thành công, False nếu thất bại
        """
        if receiver_id == self.process_id:
            return False
        
        # BƯỚC 1: Increment vector clock (GLOBAL LOCK - serialize tất cả increments)
        with self.vector_clock_lock:
            self.vector_clock.increment()
            msg_timestamp = self.vector_clock.get_clock()
        
        # BƯỚC 2 & 3: Tạo message và gửi (PER-RECEIVER LOCK - đảm bảo thứ tự)
        # QUAN TRỌNG: messages_sent phải increment trong lock để tránh race condition!
        with self.send_locks[receiver_id]:
            # Increment counter và tạo message
            self.messages_sent[receiver_id] += 1
            msg = Message(
                sender_id=self.process_id,
                receiver_id=receiver_id,
                content=content,
                timestamp=msg_timestamp,
                seq_num=self.messages_sent[receiver_id]
            )
            
            # Gửi đến receiver
            receiver_config = self.config['processes'][receiver_id]
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5.0)  # 5 second timeout
                sock.connect((receiver_config['host'], receiver_config['port']))
                
                msg_json = json.dumps(msg.to_dict()) + '\n'
                sock.sendall(msg_json.encode('utf-8'))
                sock.close()
                
                self.logger.debug(f"→ SENT: {msg.content} | VC: {msg.timestamp}")
                return True
                
            except Exception as e:
                self.logger.error(f"Error sending to P{receiver_id}: {e}")
                return False
    
    def send_messages_to_process(self, receiver_id: int, num_messages: int,
                                  messages_per_minute: int) -> None:
        """
        Gửi messages đến một process cụ thể (chạy trong thread riêng)
        
        Args:
            receiver_id: ID của process nhận
            num_messages: Số lượng messages cần gửi
            messages_per_minute: Tốc độ gửi (messages/phút)
        """
        delay = 60.0 / messages_per_minute  # Delay giữa các messages
        
        self.logger.info(f"Starting sender thread for P{receiver_id} ({num_messages} msgs, {messages_per_minute} msgs/min)")
        
        for i in range(1, num_messages + 1):
            if not self.running:
                break
            
            content = f"Message {i} from P{self.process_id} to P{receiver_id}"
            self.send_message(receiver_id, content)
            
            # Random delay để tạo tính ngẫu nhiên
            sleep_time = random.uniform(delay * 0.7, delay * 1.3)
            time.sleep(sleep_time)
        
        self.logger.info(f"Finished sending {num_messages} messages to P{receiver_id}")
    
    def start_server(self) -> None:
        """Khởi động server để nhận messages"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(20)
            self.running = True
            
            self.logger.info(f"Server started and listening on {self.host}:{self.port}")
            
            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
                    client_socket, addr = self.server_socket.accept()
                    
                    # Handle client trong thread riêng
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket,),
                        daemon=True
                    )
                    thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.logger.error(f"Server error: {e}")
        
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            raise
    
    def handle_client(self, client_socket: socket.socket) -> None:
        """Xử lý connection từ client"""
        try:
            data = b''
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b'\n' in data:
                    break
            
            if data:
                msg_dict = json.loads(data.decode('utf-8'))
                msg = Message.from_dict(msg_dict)
                self.handle_received_message(msg)
        
        except Exception as e:
            self.logger.error(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    def start_sending(self, num_messages: int, messages_per_minute: int) -> List[threading.Thread]:
        """
        Khởi động threads để gửi messages đến tất cả processes khác
        
        Returns:
            List các threads đã tạo
        """
        threads = []
        
        for receiver_id in range(self.num_processes):
            if receiver_id != self.process_id:
                thread = threading.Thread(
                    target=self.send_messages_to_process,
                    args=(receiver_id, num_messages, messages_per_minute),
                    daemon=True
                )
                thread.start()
                threads.append(thread)
        
        self.logger.info(f"Started {len(threads)} sender threads")
        return threads
    
    def print_statistics(self) -> None:
        """In thống kê về quá trình xử lý messages"""
        total_sent = sum(self.messages_sent.values())
        total_received = sum(self.messages_received.values())
        total_delivered = sum(self.messages_delivered.values())
        
        print("\n" + "=" * 80)
        print(f"PROCESS {self.process_id} - FINAL STATISTICS")
        print("=" * 80)
        print(f"Vector Clock:        {self.vector_clock}")
        print(f"Total Sent:          {total_sent}")
        print(f"Total Received:      {total_received}")
        print(f"Total Delivered:     {total_delivered}")
        print(f"Total Buffered:      {self.total_buffered}")
        print(f"Total Unbuffered:    {self.total_unbuffered}")
        print(f"Current Buffer Size: {len(self.buffer)}")
        print(f"Max Buffer Size:     {self.max_buffer_size}")
        print("=" * 80)
        
        print("\nPer-Process Details:")
        print(f"{'Process':<10} {'Sent':<10} {'Received':<12} {'Delivered':<12}")
        print("-" * 80)
        for pid in range(self.num_processes):
            if pid != self.process_id:
                sent = self.messages_sent[pid]
                recv = self.messages_received[pid]
                deliv = self.messages_delivered[pid]
                print(f"P{pid:<9} {sent:<10} {recv:<12} {deliv:<12}")
        print("=" * 80 + "\n")
        
        # Log to file
        self.logger.info("=" * 80)
        self.logger.info("FINAL STATISTICS")
        self.logger.info("=" * 80)
        self.logger.info(f"Vector Clock:        {self.vector_clock}")
        self.logger.info(f"Total Sent:          {total_sent}")
        self.logger.info(f"Total Received:      {total_received}")
        self.logger.info(f"Total Delivered:     {total_delivered}")
        self.logger.info(f"Total Buffered:      {self.total_buffered}")
        self.logger.info(f"Total Unbuffered:    {self.total_unbuffered}")
        self.logger.info(f"Current Buffer Size: {len(self.buffer)}")
        self.logger.info(f"Max Buffer Size:     {self.max_buffer_size}")
        self.logger.info("=" * 80)
    
    def _print_colored(self, message: str, color: str = "white") -> None:
        """In message với màu sắc"""
        colors = {
            "green": "\033[92m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "blue": "\033[94m",
            "cyan": "\033[96m",
            "white": "\033[0m"
        }
        color_code = colors.get(color, colors["white"])
        reset = "\033[0m"
        print(f"{color_code}[P{self.process_id}] {message}{reset}")
    
    def run(self, num_messages: int = 150, messages_per_minute: int = 100) -> None:
        """
        Chạy SES process
        
        1. Start server để nhận messages
        2. Đợi tất cả processes khởi động
        3. Bắt đầu gửi messages
        4. Đợi hoàn thành
        5. In statistics
        """
        # Start server
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        server_thread.start()
        
        # Đợi server khởi động
        time.sleep(1)
        
        # Đợi tất cả processes khởi động (cần đủ thời gian cho 15 processes)
        print(f"\n[P{self.process_id}] Waiting for all processes to start...")
        time.sleep(10)  # Tăng từ 3 lên 10 giây cho 15 processes
        
        self._print_colored(f"Starting to send {num_messages} messages to each of {self.num_processes - 1} processes", "cyan")
        
        # Start sending
        sender_threads = self.start_sending(num_messages, messages_per_minute)
        
        # Đợi tất cả sender threads hoàn thành
        for thread in sender_threads:
            thread.join()
        
        self._print_colored("All messages sent. Waiting for remaining deliveries...", "cyan")
        
        # Đợi để nhận và xử lý các messages còn lại
        time.sleep(5)
        
        # Print statistics
        self.print_statistics()
    
    def stop(self) -> None:
        """Dừng process"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.logger.info("Process stopped")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python3 ses_process.py <process_id> [num_messages] [messages_per_minute]")
        print("\nExample:")
        print("  python3 ses_process.py 0 150 100")
        print("\nArguments:")
        print("  process_id:           ID của process (0-14)")
        print("  num_messages:         Số messages gửi đến mỗi process (default: 150)")
        print("  messages_per_minute:  Tốc độ gửi messages (default: 100)")
        sys.exit(1)
    
    process_id = int(sys.argv[1])
    num_messages = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    messages_per_minute = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    
    config_file = 'config/config.json'
    
    if not os.path.exists(config_file):
        print(f"Error: Config file not found: {config_file}")
        sys.exit(1)
    
    print(f"\n{'='*80}")
    print(f"SES Process {process_id} - Schiper-Eggli-Sandoz Algorithm")
    print(f"{'='*80}")
    print(f"Configuration:")
    print(f"  Process ID:           {process_id}")
    print(f"  Messages per process: {num_messages}")
    print(f"  Messages per minute:  {messages_per_minute}")
    print(f"{'='*80}\n")
    
    process = SESProcess(process_id, config_file)
    
    try:
        process.run(num_messages, messages_per_minute)
        
        # Interactive mode
        print(f"\n[P{process_id}] Interactive Mode:")
        print("  's' - Show statistics")
        print("  'q' - Quit")
        
        while True:
            try:
                cmd = input("> ").strip().lower()
                if cmd == 's':
                    process.print_statistics()
                elif cmd == 'q':
                    break
                elif cmd == '':
                    continue
                else:
                    print("Unknown command. Use 's' for statistics or 'q' to quit.")
            except EOFError:
                break
    
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        process.stop()
        print(f"\n[P{process_id}] Process terminated.\n")


if __name__ == '__main__':
    main()
