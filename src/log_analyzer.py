#!/usr/bin/env python3
"""
Log analyzer tool to visualize and analyze SES process logs
"""

import os
import re
from datetime import datetime
from typing import List, Dict
import json


class LogAnalyzer:
    """Analyze SES process logs"""
    
    def __init__(self, log_dir: str = 'logs'):
        self.log_dir = log_dir
        self.processes = {}
    
    def parse_log_file(self, process_id: int) -> Dict:
        """Parse log file for a process"""
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
            'buffer_events': [],
            'delivery_events': []
        }
        
        with open(log_file, 'r') as f:
            for line in f:
                if '→ SENT:' in line:
                    data['sent'] += 1
                elif '← RECEIVED:' in line:
                    data['received'] += 1
                elif '✓ DELIVERED:' in line:
                    data['delivered'] += 1
                elif '⊕ BUFFERED:' in line:
                    data['buffered'] += 1
                    # Extract buffer event details
                    match = re.search(r'BUFFERED: (.+) from P(\d+)', line)
                    if match:
                        data['buffer_events'].append({
                            'message': match.group(1),
                            'from': int(match.group(2)),
                            'line': line
                        })
                elif '⚡ UNBUFFERED:' in line:
                    data['unbuffered'] += 1
        
        return data
    
    def analyze_all(self):
        """Analyze logs from all processes"""
        print("="*80)
        print("SES LOG ANALYSIS")
        print("="*80)
        
        total_sent = 0
        total_received = 0
        total_delivered = 0
        total_buffered = 0
        
        for i in range(15):
            data = self.parse_log_file(i)
            if data:
                self.processes[i] = data
                total_sent += data['sent']
                total_received += data['received']
                total_delivered += data['delivered']
                total_buffered += data['buffered']
        
        print(f"\nOverall Statistics:")
        print(f"  Total messages sent: {total_sent}")
        print(f"  Total messages received: {total_received}")
        print(f"  Total messages delivered: {total_delivered}")
        print(f"  Total messages buffered: {total_buffered}")
        
        print(f"\nPer-Process Statistics:")
        print(f"{'PID':<5} {'Sent':<10} {'Received':<12} {'Delivered':<12} {'Buffered':<10}")
        print("-"*80)
        
        for pid, data in sorted(self.processes.items()):
            print(f"{pid:<5} {data['sent']:<10} {data['received']:<12} "
                  f"{data['delivered']:<12} {data['buffered']:<10}")
        
        # Show buffering events
        print(f"\nBuffering Events Summary:")
        for pid, data in sorted(self.processes.items()):
            if data['buffered'] > 0:
                print(f"\nProcess {pid}: {data['buffered']} messages buffered")
                for event in data['buffer_events'][:5]:  # Show first 5
                    print(f"  - {event['message']} from P{event['from']}")
                if len(data['buffer_events']) > 5:
                    print(f"  ... and {len(data['buffer_events'])-5} more")
        
        print("\n" + "="*80)
    
    def show_process_detail(self, process_id: int):
        """Show detailed analysis for a specific process"""
        data = self.parse_log_file(process_id)
        if not data:
            print(f"No log file found for Process {process_id}")
            return
        
        print(f"\n{'='*80}")
        print(f"Process {process_id} - Detailed Analysis")
        print(f"{'='*80}")
        print(f"Messages sent: {data['sent']}")
        print(f"Messages received: {data['received']}")
        print(f"Messages delivered: {data['delivered']}")
        print(f"Messages buffered: {data['buffered']}")
        print(f"Messages unbuffered: {data['unbuffered']}")
        
        if data['buffer_events']:
            print(f"\nBuffering Events ({len(data['buffer_events'])} total):")
            for i, event in enumerate(data['buffer_events'][:10], 1):
                print(f"{i}. {event['message']} from P{event['from']}")
            if len(data['buffer_events']) > 10:
                print(f"... and {len(data['buffer_events'])-10} more")
        
        print(f"{'='*80}\n")


def main():
    """Main entry point"""
    import sys
    
    analyzer = LogAnalyzer()
    
    if len(sys.argv) > 1:
        # Show specific process
        process_id = int(sys.argv[1])
        analyzer.show_process_detail(process_id)
    else:
        # Show all
        analyzer.analyze_all()


if __name__ == '__main__':
    main()
