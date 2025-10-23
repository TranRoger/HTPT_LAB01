#!/usr/bin/env python3
"""
SES (Schiper-Eggli-Sandoz) Algorithm Implementation
Ensures causal ordering of messages in distributed systems
"""

import socket
import threading
import time
import random
import json
import logging
import sys
from datetime import datetime
from typing import Dict, List, Tuple
import os


class VectorClock:
    """Vector Clock implementation for causal ordering"""
    
    def __init__(self, process_id: int, num_processes: int):
        self.process_id = process_id
        self.clock = [0] * num_processes
        self.lock = threading.Lock()
    
    def increment(self):
        """Increment own clock"""
        with self.lock:
            self.clock[self.process_id] += 1
    
    def update(self, received_clock: List[int]):
        """Update vector clock based on received clock"""
        with self.lock:
            for i in range(len(self.clock)):
                if i != self.process_id:
                    self.clock[i] = max(self.clock[i], received_clock[i])
    
    def get_clock(self) -> List[int]:
        """Get copy of current clock"""
        with self.lock:
            return self.clock.copy()
    
    def __str__(self):
        return str(self.clock)


class Message:
    """Message structure with vector clock timestamp"""
    
    def __init__(self, sender_id: int, receiver_id: int, content: str, 
                 timestamp: List[int], seq_num: int):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.timestamp = timestamp
        self.seq_num = seq_num
        self.arrival_time = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert message to dictionary for JSON serialization"""
        return {
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'timestamp': self.timestamp,
            'seq_num': self.seq_num
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Message':
        """Create message from dictionary"""
        msg = Message(
            data['sender_id'],
            data['receiver_id'],
            data['content'],
            data['timestamp'],
            data['seq_num']
        )
        return msg
    
    def __str__(self):
        return f"Msg[{self.sender_id}→{self.receiver_id}, #{self.seq_num}, VC:{self.timestamp}]"


class SESProcess:
    """
    SES Process implementing causal ordering
    Each process can send/receive messages with causal guarantees
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
        
        # Vector clock
        self.vector_clock = VectorClock(process_id, self.num_processes)
        
        # Message counters
        self.messages_sent = {i: 0 for i in range(self.num_processes) if i != process_id}
        self.messages_received = {i: 0 for i in range(self.num_processes) if i != process_id}
        self.messages_delivered = {i: 0 for i in range(self.num_processes) if i != process_id}
        
        # Buffer for messages waiting to be delivered
        self.buffer: List[Message] = []
        self.buffer_lock = threading.Lock()
        
        # Delivered messages log
        self.delivered_messages: List[Message] = []
        self.delivered_lock = threading.Lock()
        
        # Server socket
        self.server_socket = None
        self.running = False
        
        # Statistics
        self.total_buffered = 0
        self.max_buffer_size = 0
        
        # Setup logging
        self._setup_logging()
        
        self.logger.info(f"Process {self.process_id} initialized at {self.host}:{self.port}")
        self.logger.info(f"Vector Clock: {self.vector_clock}")
    
    def _setup_logging(self):
        """Setup detailed logging for this process"""
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = f'{log_dir}/process_{self.process_id}.log'
        
        # Create logger
        self.logger = logging.getLogger(f'Process-{self.process_id}')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        fh = logging.FileHandler(log_file, mode='w')
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [P%(name)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S.%f'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def can_deliver(self, msg: Message) -> bool:
        """
        Check if message can be delivered according to SES algorithm
        Message M(i,j) can be delivered at process j if:
        1. seq_num = delivered_count[i] + 1 (next in FIFO order from sender i)
        2. For all k: TS(M)[k] <= VC[j][k] (no missing causally dependent messages)
        """
        current_vc = self.vector_clock.get_clock()
        msg_ts = msg.timestamp
        sender = msg.sender_id
        
        # Condition 1: FIFO ordering - must be next expected message from this sender
        expected_seq = self.messages_delivered[sender] + 1
        if msg.seq_num != expected_seq:
            return False
        
        # Condition 2: Causal dependencies - all timestamps must be satisfied
        for k in range(self.num_processes):
            if msg_ts[k] > current_vc[k]:
                return False
        
        return True
    
    def deliver_message(self, msg: Message):
        """
        Deliver a message and update vector clock
        """
        # Update vector clock: merge with message timestamp
        self.vector_clock.update(msg.timestamp)
        # Increment the sender's entry in our vector clock (we've now seen one more message from sender)
        self.vector_clock.clock[msg.sender_id] += 1
        
        # Add to delivered messages
        with self.delivered_lock:
            self.delivered_messages.append(msg)
            self.messages_delivered[msg.sender_id] += 1
        
        # Log delivery
        self.logger.info(f"✓ DELIVERED: {msg.content} from P{msg.sender_id}")
        self.logger.info(f"  Message VC: {msg.timestamp}")
        self.logger.info(f"  Updated VC: {self.vector_clock}")
        self.logger.info(f"  Total delivered from P{msg.sender_id}: {self.messages_delivered[msg.sender_id]}")
        
        # Print to console for visibility
        self._print_status(f"✓ DELIVERED: {msg.content}", "green")
    
    def try_deliver_buffered(self):
        """
        Try to deliver messages from buffer
        """
        with self.buffer_lock:
            delivered_any = True
            while delivered_any:
                delivered_any = False
                for msg in self.buffer[:]:
                    if self.can_deliver(msg):
                        self.buffer.remove(msg)
                        self.logger.info(f"⚡ UNBUFFERED: {msg.content} from P{msg.sender_id}")
                        self.logger.info("  Reason: Dependencies satisfied")
                        self.deliver_message(msg)
                        delivered_any = True
                        break
    
    def handle_received_message(self, msg: Message):
        """
        Handle a received message according to SES algorithm
        """
        self.messages_received[msg.sender_id] += 1
        
        self.logger.info(f"← RECEIVED: {msg.content} from P{msg.sender_id}")
        self.logger.info(f"  Message VC: {msg.timestamp}")
        self.logger.info(f"  Current VC: {self.vector_clock}")
        
        # Check if can deliver immediately
        if self.can_deliver(msg):
            self.deliver_message(msg)
        else:
            # Buffer the message
            with self.buffer_lock:
                self.buffer.append(msg)
                self.total_buffered += 1
                self.max_buffer_size = max(self.max_buffer_size, len(self.buffer))
            
            self.logger.warning(f"⊕ BUFFERED: {msg.content} from P{msg.sender_id}")
            self.logger.warning("  Reason: Waiting for dependencies")
            self.logger.warning(f"  Buffer size: {len(self.buffer)}")
            self._print_buffer_reason(msg)
            self._print_status(f"⊕ BUFFERED: {msg.content} (Buffer: {len(self.buffer)})", "yellow")
        
        # Try to deliver buffered messages
        self.try_deliver_buffered()
    
    def _print_buffer_reason(self, msg: Message):
        """Print detailed reason why message was buffered"""
        current_vc = self.vector_clock.get_clock()
        msg_ts = msg.timestamp
        sender = msg.sender_id
        
        reasons = []
        
        # Check FIFO condition
        expected_seq = self.messages_delivered[sender] + 1
        if msg.seq_num != expected_seq:
            reason = f"Out of order: expecting seq #{expected_seq}, got #{msg.seq_num}"
            reasons.append(reason)
            self.logger.warning(f"  └─ {reason}")
        
        # Check causal dependencies
        for k in range(self.num_processes):
            if msg_ts[k] > current_vc[k]:
                reason = f"Causal dep: need VC[{k}]>={msg_ts[k]}, have {current_vc[k]}"
                reasons.append(reason)
                self.logger.warning(f"  └─ {reason}")
    
    def _print_status(self, message: str, color: str = "white"):
        """Print colored status message"""
        colors = {
            "green": "\033[92m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "blue": "\033[94m",
            "white": "\033[0m"
        }
        color_code = colors.get(color, colors["white"])
        reset = "\033[0m"
        print(f"{color_code}[P{self.process_id}] {message}{reset}")
    
    def start_server(self):
        """Start server to receive messages"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(20)
        
        self.running = True
        self.logger.info(f"Server started on {self.host}:{self.port}")
        
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                client_socket, _ = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                thread.daemon = True
                thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.logger.error(f"Server error: {e}")

    def wait_for_all_peers(self, timeout: float = 60.0, check_interval: float = 0.5):
        """
        Wait until all peer servers are accepting connections.
        This performs a simple TCP connect check to each peer address:port.
        If timeout is reached, it will proceed but log a warning.
        """
        start = time.time()
        remaining = set(range(self.num_processes))

        # remove self from remaining set
        if self.process_id in remaining:
            remaining.remove(self.process_id)

        self.logger.info(f"Waiting for {len(remaining)} peers to be up (timeout={timeout}s)...")

        while remaining and (time.time() - start) < timeout:
            for pid in remaining.copy():
                peer = self.config['processes'][pid]
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    sock.connect((peer['host'], peer['port']))
                    sock.close()
                    remaining.remove(pid)
                    self.logger.info("Peer P{} is up ({}:{})".format(pid, peer['host'], peer['port']))
                except Exception:
                    # still not up
                    pass

            if remaining:
                time.sleep(check_interval)

        if remaining:
            self.logger.warning("Timeout reached while waiting for peers: %s. Proceeding anyway.", sorted(remaining))
            return False
        else:
            self.logger.info("All peers are up. Proceeding to send messages.")
            return True
    
    def handle_client(self, client_socket: socket.socket):
        """Handle incoming client connection"""
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
    
    def send_message(self, receiver_id: int, content: str):
        """Send a message to another process"""
        if receiver_id == self.process_id:
            return
        
        # Create message with current timestamp (capture state before sending)
        # Do NOT increment VC here - increment happens only on delivery
        msg = Message(
            sender_id=self.process_id,
            receiver_id=receiver_id,
            content=content,
            timestamp=self.vector_clock.get_clock(),
            seq_num=self.messages_sent[receiver_id] + 1
        )
        
        self.messages_sent[receiver_id] += 1
        
        # Send to receiver
        receiver_config = self.config['processes'][receiver_id]
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((receiver_config['host'], receiver_config['port']))
            
            msg_json = json.dumps(msg.to_dict()) + '\n'
            sock.sendall(msg_json.encode('utf-8'))
            sock.close()
            
            self.logger.debug(f"→ SENT: {content} to P{receiver_id}, VC: {msg.timestamp}")
        
        except Exception as e:
            self.logger.error(f"Error sending to P{receiver_id}: {e}")
    
    def send_messages_to_process(self, receiver_id: int, num_messages: int, 
                                  messages_per_minute: int):
        """Send messages to a specific process in a separate thread"""
        delay = 60.0 / messages_per_minute
        
        for i in range(1, num_messages + 1):
            if not self.running:
                break
            
            content = f"Message {i} from P{self.process_id} to P{receiver_id}"
            self.send_message(receiver_id, content)
            
            # Random delay
            sleep_time = random.uniform(delay * 0.5, delay * 1.5)
            time.sleep(sleep_time)
        
        self.logger.info(f"Finished sending {num_messages} messages to P{receiver_id}")
    
    def start_sending(self, num_messages_per_process: int, messages_per_minute: int):
        """Start sending messages to all other processes"""
        threads = []
        
        for receiver_id in range(self.num_processes):
            if receiver_id != self.process_id:
                thread = threading.Thread(
                    target=self.send_messages_to_process,
                    args=(receiver_id, num_messages_per_process, messages_per_minute)
                )
                thread.daemon = True
                thread.start()
                threads.append(thread)
        
        return threads
    
    def print_statistics(self):
        """Print statistics about message processing"""
        print(f"\n{'='*60}")
        print(f"Process {self.process_id} - Statistics")
        print(f"{'='*60}")
        print(f"Vector Clock: {self.vector_clock}")
        print("\nMessages Sent:")
        for pid, count in sorted(self.messages_sent.items()):
            print(f"  To P{pid}: {count}")
        print("\nMessages Received:")
        for pid, count in sorted(self.messages_received.items()):
            print(f"  From P{pid}: {count}")
        print("\nMessages Delivered:")
        for pid, count in sorted(self.messages_delivered.items()):
            print(f"  From P{pid}: {count}")
        print("\nBuffering Statistics:")
        print(f"  Current buffer size: {len(self.buffer)}")
        print(f"  Total buffered: {self.total_buffered}")
        print(f"  Max buffer size: {self.max_buffer_size}")
        print(f"{'='*60}\n")
        
        self.logger.info("=== FINAL STATISTICS ===")
        self.logger.info(f"Vector Clock: {self.vector_clock}")
        self.logger.info(f"Total messages sent: {sum(self.messages_sent.values())}")
        self.logger.info(f"Total messages received: {sum(self.messages_received.values())}")
        self.logger.info(f"Total messages delivered: {sum(self.messages_delivered.values())}")
        self.logger.info(f"Total buffered: {self.total_buffered}")
        self.logger.info(f"Max buffer size: {self.max_buffer_size}")
    
    def run(self, num_messages: int = 150, messages_per_minute: int = 100):
        """Run the SES process"""
        # Start server in background
        server_thread = threading.Thread(target=self.start_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait until all peers' servers appear to be up before sending
        all_found = self.wait_for_all_peers(timeout=self.config.get('peer_startup_timeout', 60.0))

        # If we successfully detected all peers, wait an extra 5 seconds before sending
        # (gives a short stabilization window). If we timed out, proceed immediately.
        if all_found:
            self.logger.info("All peers confirmed up — sleeping 5s before starting sends to stabilize.")
            time.sleep(5)

        print(f"\n[P{self.process_id}] Starting to send {num_messages} messages to each process...")
        
        # Start sending messages
        sender_threads = self.start_sending(num_messages, messages_per_minute)
        
        # Wait for all messages to be sent
        for thread in sender_threads:
            thread.join()
        
        print(f"\n[P{self.process_id}] All messages sent. Waiting for remaining messages...")
        
        # Wait for messages to be delivered
        time.sleep(5)
        
        # Print statistics
        self.print_statistics()
    
    def stop(self):
        """Stop the process"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        self.logger.info("Process stopped")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python ses_process.py <process_id> [num_messages] [messages_per_minute]")
        print("Example: python ses_process.py 0 150 100")
        sys.exit(1)
    
    process_id = int(sys.argv[1])
    num_messages = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    messages_per_minute = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    
    config_file = 'config/config.json'
    
    process = SESProcess(process_id, config_file)
    
    try:
        process.run(num_messages, messages_per_minute)
        
        # Keep running for interactive commands
        print(f"\n[P{process_id}] Press 's' for statistics, 'q' to quit")
        while True:
            cmd = input("> ").strip().lower()
            if cmd == 's':
                process.print_statistics()
            elif cmd == 'q':
                break
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    
    finally:
        process.stop()


if __name__ == '__main__':
    main()
