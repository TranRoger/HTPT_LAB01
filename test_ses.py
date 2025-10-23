#!/usr/bin/env python3
"""
Simple test script to verify SES implementation
Chạy quick test với 3 processes để verify
"""

import subprocess
import sys
import time
import os
import json


def create_test_config():
    """Tạo config cho 3 processes để test"""
    config = {
        "processes": [
            {"id": 0, "host": "127.0.0.1", "port": 6000},
            {"id": 1, "host": "127.0.0.1", "port": 6001},
            {"id": 2, "host": "127.0.0.1", "port": 6002}
        ],
        "default_num_messages": 10,
        "default_messages_per_minute": 200,
        "log_level": "INFO"
    }
    
    # Backup original config
    if os.path.exists('config/config.json'):
        os.rename('config/config.json', 'config/config.json.bak')
    
    # Write test config
    with open('config/config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    return config


def restore_config():
    """Khôi phục config gốc"""
    if os.path.exists('config/config.json.bak'):
        os.rename('config/config.json.bak', 'config/config.json')


def run_test():
    """Chạy test"""
    print("=" * 80)
    print("SES ALGORITHM - QUICK TEST")
    print("=" * 80)
    print()
    
    # Create test config
    print("Creating test configuration (3 processes)...")
    create_test_config()
    
    # Clean old logs
    print("Cleaning old logs...")
    for i in range(3):
        log_file = f'logs/process_{i}.log'
        if os.path.exists(log_file):
            os.remove(log_file)
    
    print()
    print("Starting 3 processes (10 messages each)...")
    print("Expected: 60 total messages (3 × 2 × 10)")
    print()
    
    # Start processes
    processes = []
    for i in range(3):
        cmd = [sys.executable, 'src/ses_process.py', str(i), '10', '200']
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(proc)
        print(f"  Started Process {i}")
        time.sleep(0.5)
    
    print()
    print("Waiting for completion (20 seconds)...")
    time.sleep(20)
    
    # Terminate processes
    print("Stopping processes...")
    for proc in processes:
        proc.terminate()
    
    time.sleep(2)
    
    # Check results
    print()
    print("=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print()
    
    success = True
    for i in range(3):
        log_file = f'logs/process_{i}.log'
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                content = f.read()
                delivered = content.count('✓ DELIVERED')
                buffered = content.count('⊕ BUFFERED')
                
                print(f"Process {i}:")
                print(f"  Delivered: {delivered} (expected ~20)")
                print(f"  Buffered:  {buffered}")
                
                if delivered < 15:
                    print(f"  ⚠ WARNING: Low delivery count")
                    success = False
                else:
                    print(f"  ✓ OK")
                print()
        else:
            print(f"Process {i}: ✗ No log file found")
            success = False
    
    # Restore config
    print("Restoring original configuration...")
    restore_config()
    
    print("=" * 80)
    if success:
        print("✓ TEST PASSED")
    else:
        print("⚠ TEST HAD WARNINGS")
    print("=" * 80)
    print()
    
    return success


if __name__ == '__main__':
    try:
        success = run_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted.")
        restore_config()
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        restore_config()
        sys.exit(1)
