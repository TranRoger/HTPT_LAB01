#!/usr/bin/env python3
"""
Script to launch all 15 SES processes
"""

import subprocess
import sys
import time
import os

def main():
    """Launch all processes"""
    num_processes = 15
    num_messages = 150  # Default: 150 messages per process
    messages_per_minute = 100  # Default: 100 messages per minute
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        num_messages = int(sys.argv[1])
    if len(sys.argv) > 2:
        messages_per_minute = int(sys.argv[2])
    
    print(f"Launching {num_processes} processes...")
    print(f"Each process will send {num_messages} messages to each other process")
    print(f"Rate: {messages_per_minute} messages per minute")
    print(f"{'='*60}\n")
    
    processes = []
    
    # Launch all processes
    for i in range(num_processes):
        cmd = [
            sys.executable,
            'src/ses_process.py',
            str(i),
            str(num_messages),
            str(messages_per_minute)
        ]
        
        # Open in new terminal (for Linux)
        if sys.platform.startswith('linux'):
            # Try different terminal emulators
            terminals = [
                ['gnome-terminal', '--', 'bash', '-c'],
                ['xterm', '-e'],
                ['konsole', '-e'],
                ['xfce4-terminal', '-e']
            ]
            
            terminal_cmd = None
            for term in terminals:
                try:
                    # Check if terminal is available
                    subprocess.run(['which', term[0]], 
                                 capture_output=True, check=True)
                    terminal_cmd = term
                    break
                except:
                    continue
            
            if terminal_cmd:
                if terminal_cmd[0] == 'gnome-terminal':
                    full_cmd = terminal_cmd + [' '.join(cmd) + '; exec bash']
                else:
                    full_cmd = terminal_cmd + [' '.join(cmd)]
                
                proc = subprocess.Popen(full_cmd)
            else:
                # Fallback: run in background
                print(f"No terminal emulator found. Running P{i} in background...")
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
        else:
            # For other platforms, just run in background
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        processes.append(proc)
        print(f"Launched Process {i}")
        time.sleep(0.3)  # Small delay between launches
    
    print(f"\n{'='*60}")
    print(f"All {num_processes} processes launched!")
    print(f"Check the 'logs/' directory for detailed logs")
    print(f"Press Ctrl+C to stop all processes")
    print(f"{'='*60}\n")
    
    try:
        # Wait for all processes
        for proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\nStopping all processes...")
        for proc in processes:
            proc.terminate()
        
        # Wait a bit then kill if still running
        time.sleep(2)
        for proc in processes:
            if proc.poll() is None:
                proc.kill()
        
        print("All processes stopped.")

if __name__ == '__main__':
    main()
