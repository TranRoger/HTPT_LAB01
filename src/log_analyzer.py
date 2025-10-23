#!/usr/bin/env python3
"""
Log Analyzer Tool
Phân tích và visualize logs từ các SES processes
"""

import os
import re
import sys
from typing import Dict, List, Tuple
from collections import defaultdict


class LogAnalyzer:
    """Analyzer để phân tích logs của SES processes"""
    
    def __init__(self, log_dir: str = 'logs'):
        self.log_dir = log_dir
        self.process_data = {}
    
    def parse_log_file(self, process_id: int) -> Dict:
        """
        Parse log file của một process
        
        Returns:
            Dictionary chứa statistics và events
        """
        log_file = f"{self.log_dir}/process_{process_id}.log"
        
        if not os.path.exists(log_file):
            return None
        
        data = {
            'process_id': process_id,
            'sent': 0,
            'received': 0,
            'delivered': 0,
            'buffered': 0,
            'unbuffered': 0,
            'sent_per_process': defaultdict(int),
            'received_per_process': defaultdict(int),
            'delivered_per_process': defaultdict(int),
            'buffer_events': [],
            'delivery_events': [],
            'final_vector_clock': None
        }
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Count sent messages
                if '→ SENT:' in line:
                    data['sent'] += 1
                    # Extract receiver
                    match = re.search(r'to P(\d+)', line)
                    if match:
                        receiver = int(match.group(1))
                        data['sent_per_process'][receiver] += 1
                
                # Count received messages
                elif '← RECEIVED:' in line:
                    data['received'] += 1
                    match = re.search(r'from P(\d+)', line)
                    if match:
                        sender = int(match.group(1))
                        data['received_per_process'][sender] += 1
                
                # Count delivered messages
                elif '✓ DELIVERED:' in line:
                    data['delivered'] += 1
                    match = re.search(r'from P(\d+)', line)
                    if match:
                        sender = int(match.group(1))
                        data['delivered_per_process'][sender] += 1
                        data['delivery_events'].append(line.strip())
                
                # Count buffered messages
                elif '⊕ BUFFERED:' in line:
                    data['buffered'] += 1
                    data['buffer_events'].append(line.strip())
                
                # Count unbuffered messages
                elif '⚡ UNBUFFERED:' in line:
                    data['unbuffered'] += 1
                
                # Extract final vector clock
                elif 'Vector Clock:' in line and 'FINAL STATISTICS' in ''.join(
                    open(log_file, 'r', encoding='utf-8').readlines()[
                        max(0, len(open(log_file, 'r', encoding='utf-8').readlines()) - 20):
                    ]
                ):
                    match = re.search(r'Vector Clock:\s*(\[.*?\])', line)
                    if match:
                        data['final_vector_clock'] = match.group(1)
        
        return data
    
    def analyze_all(self):
        """Phân tích logs từ tất cả processes"""
        print()
        print("=" * 100)
        print("SES ALGORITHM - LOG ANALYSIS")
        print("=" * 100)
        print()
        
        # Parse tất cả log files
        total_sent = 0
        total_received = 0
        total_delivered = 0
        total_buffered = 0
        total_unbuffered = 0
        
        num_processes = 15
        
        for i in range(num_processes):
            data = self.parse_log_file(i)
            if data:
                self.process_data[i] = data
                total_sent += data['sent']
                total_received += data['received']
                total_delivered += data['delivered']
                total_buffered += data['buffered']
                total_unbuffered += data['unbuffered']
        
        if not self.process_data:
            print("No log files found in 'logs/' directory.")
            print("Please run the SES processes first.")
            return
        
        # Overall Statistics
        print("OVERALL STATISTICS")
        print("-" * 100)
        print(f"Total messages sent:      {total_sent:,}")
        print(f"Total messages received:  {total_received:,}")
        print(f"Total messages delivered: {total_delivered:,}")
        print(f"Total messages buffered:  {total_buffered:,}")
        print(f"Total messages unbuffered: {total_unbuffered:,}")
        print()
        
        # Verify correctness
        expected_total = num_processes * (num_processes - 1) * 150  # 15 * 14 * 150
        print("VERIFICATION")
        print("-" * 100)
        print(f"Expected total messages:  {expected_total:,}")
        print(f"Actual delivered:         {total_delivered:,}")
        
        if total_delivered == expected_total:
            print("Status:                   ✓ SUCCESS - All messages delivered!")
        else:
            diff = expected_total - total_delivered
            print(f"Status:                   ⚠ WARNING - Missing {diff} messages")
        print()
        
        # Per-Process Statistics
        print("PER-PROCESS STATISTICS")
        print("-" * 100)
        print(f"{'PID':<6} {'Sent':<10} {'Received':<12} {'Delivered':<12} {'Buffered':<10} {'Unbuffered':<12}")
        print("-" * 100)
        
        for pid in sorted(self.process_data.keys()):
            data = self.process_data[pid]
            print(f"{pid:<6} {data['sent']:<10} {data['received']:<12} "
                  f"{data['delivered']:<12} {data['buffered']:<10} {data['unbuffered']:<12}")
        
        print("-" * 100)
        print()
        
        # Buffering Analysis
        self._analyze_buffering()
        
        # Vector Clock Analysis
        self._analyze_vector_clocks()
    
    def _analyze_buffering(self):
        """Phân tích buffering behavior"""
        print("BUFFERING ANALYSIS")
        print("-" * 100)
        
        processes_with_buffering = [
            pid for pid, data in self.process_data.items()
            if data['buffered'] > 0
        ]
        
        if not processes_with_buffering:
            print("No buffering occurred - all messages were delivered immediately!")
        else:
            print(f"Processes with buffering: {len(processes_with_buffering)}/{len(self.process_data)}")
            print()
            
            for pid in processes_with_buffering:
                data = self.process_data[pid]
                print(f"Process {pid}:")
                print(f"  Total buffered:   {data['buffered']}")
                print(f"  Total unbuffered: {data['unbuffered']}")
                
                # Show some buffer events
                if data['buffer_events']:
                    print(f"  Sample buffer events:")
                    for event in data['buffer_events'][:3]:
                        # Extract key info
                        if '⊕ BUFFERED:' in event:
                            msg_part = event.split('⊕ BUFFERED:')[1].strip()
                            print(f"    - {msg_part[:80]}...")
                    
                    if len(data['buffer_events']) > 3:
                        print(f"    ... and {len(data['buffer_events']) - 3} more")
                print()
        
        print("-" * 100)
        print()
    
    def _analyze_vector_clocks(self):
        """Phân tích final vector clocks"""
        print("FINAL VECTOR CLOCKS")
        print("-" * 100)
        
        for pid in sorted(self.process_data.keys()):
            data = self.process_data[pid]
            if data['final_vector_clock']:
                print(f"Process {pid}: {data['final_vector_clock']}")
        
        print("-" * 100)
        print()
    
    def show_process_detail(self, process_id: int):
        """Hiển thị phân tích chi tiết cho một process"""
        data = self.parse_log_file(process_id)
        
        if not data:
            print(f"No log file found for Process {process_id}")
            return
        
        print()
        print("=" * 100)
        print(f"PROCESS {process_id} - DETAILED ANALYSIS")
        print("=" * 100)
        print()
        
        print("OVERALL STATISTICS")
        print("-" * 100)
        print(f"Messages sent:      {data['sent']}")
        print(f"Messages received:  {data['received']}")
        print(f"Messages delivered: {data['delivered']}")
        print(f"Messages buffered:  {data['buffered']}")
        print(f"Messages unbuffered: {data['unbuffered']}")
        
        if data['final_vector_clock']:
            print(f"Final Vector Clock: {data['final_vector_clock']}")
        print()
        
        # Sent per process
        if data['sent_per_process']:
            print("MESSAGES SENT TO EACH PROCESS")
            print("-" * 100)
            for receiver in sorted(data['sent_per_process'].keys()):
                count = data['sent_per_process'][receiver]
                print(f"  To P{receiver}: {count}")
            print()
        
        # Received per process
        if data['received_per_process']:
            print("MESSAGES RECEIVED FROM EACH PROCESS")
            print("-" * 100)
            for sender in sorted(data['received_per_process'].keys()):
                count = data['received_per_process'][sender]
                print(f"  From P{sender}: {count}")
            print()
        
        # Delivered per process
        if data['delivered_per_process']:
            print("MESSAGES DELIVERED FROM EACH PROCESS")
            print("-" * 100)
            for sender in sorted(data['delivered_per_process'].keys()):
                count = data['delivered_per_process'][sender]
                print(f"  From P{sender}: {count}")
            print()
        
        # Buffering events
        if data['buffer_events']:
            print("BUFFERING EVENTS")
            print("-" * 100)
            print(f"Total: {len(data['buffer_events'])} events")
            print()
            print("Sample events (first 10):")
            for i, event in enumerate(data['buffer_events'][:10], 1):
                if '⊕ BUFFERED:' in event:
                    msg_part = event.split('⊕ BUFFERED:')[1].strip()
                    print(f"  {i}. {msg_part[:80]}")
            
            if len(data['buffer_events']) > 10:
                print(f"  ... and {len(data['buffer_events']) - 10} more")
            print()
        
        print("=" * 100)
        print()


def main():
    """Main entry point"""
    analyzer = LogAnalyzer()
    
    if len(sys.argv) > 1:
        # Analyze specific process
        try:
            process_id = int(sys.argv[1])
            if 0 <= process_id < 15:
                analyzer.show_process_detail(process_id)
            else:
                print(f"Error: Process ID must be between 0 and 14")
                sys.exit(1)
        except ValueError:
            print(f"Error: Invalid process ID: {sys.argv[1]}")
            sys.exit(1)
    else:
        # Analyze all processes
        analyzer.analyze_all()


if __name__ == '__main__':
    main()
