#!/usr/bin/env python3
"""
Script để launch tất cả 15 SES processes cùng lúc
Mỗi process sẽ chạy trong terminal riêng (Linux) hoặc background (other OS)
"""

import subprocess
import sys
import time
import os
import signal


def get_terminal_command():
    """Tìm terminal emulator có sẵn trên hệ thống"""
    terminals = [
        ['gnome-terminal', '--'],
        ['konsole', '-e'],
        ['xfce4-terminal', '-e'],
        ['xterm', '-e'],
        ['terminator', '-e']
    ]
    
    for term_cmd in terminals:
        try:
            result = subprocess.run(
                ['which', term_cmd[0]],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                return term_cmd
        except:
            continue
    
    return None


def launch_process(process_id, num_messages, messages_per_minute, use_terminal=True):
    """
    Launch một SES process
    
    Args:
        process_id: ID của process (0-14)
        num_messages: Số messages gửi đến mỗi process
        messages_per_minute: Tốc độ gửi
        use_terminal: Có mở terminal riêng không
    
    Returns:
        subprocess.Popen object
    """
    python_cmd = sys.executable
    script_path = os.path.join('src', 'ses_process.py')
    
    cmd = [
        python_cmd,
        script_path,
        str(process_id),
        str(num_messages),
        str(messages_per_minute)
    ]
    
    if use_terminal and sys.platform.startswith('linux'):
        terminal_cmd = get_terminal_command()
        
        if terminal_cmd:
            if terminal_cmd[0] == 'gnome-terminal':
                # gnome-terminal cần cú pháp đặc biệt
                full_cmd = terminal_cmd + [
                    'bash', '-c',
                    f"{' '.join(cmd)}; echo ''; echo 'Press Enter to close...'; read"
                ]
            else:
                # Các terminal khác
                full_cmd = terminal_cmd + [
                    'bash', '-c',
                    f"{' '.join(cmd)}; echo ''; echo 'Press Enter to close...'; read"
                ]
            
            return subprocess.Popen(full_cmd)
    
    # Fallback: chạy trong background
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )


def main():
    """Main function"""
    # Parse arguments
    num_messages = 150
    messages_per_minute = 100
    
    if len(sys.argv) > 1:
        num_messages = int(sys.argv[1])
    if len(sys.argv) > 2:
        messages_per_minute = int(sys.argv[2])
    
    num_processes = 15
    
    print("=" * 80)
    print("SES ALGORITHM - LAUNCH ALL PROCESSES")
    print("=" * 80)
    print(f"Number of processes:      {num_processes}")
    print(f"Messages per process:     {num_messages}")
    print(f"Messages per minute:      {messages_per_minute}")
    print(f"Total messages expected:  {num_processes * (num_processes - 1) * num_messages}")
    print("=" * 80)
    print()
    
    # Kiểm tra config file
    config_file = 'config/config.json'
    if not os.path.exists(config_file):
        print(f"Error: Config file not found: {config_file}")
        print("Please run this script from the project root directory.")
        sys.exit(1)
    
    # Tạo logs directory
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Clean old logs
    print("Cleaning old log files...")
    for i in range(num_processes):
        log_file = f'logs/process_{i}.log'
        if os.path.exists(log_file):
            os.remove(log_file)
    
    # Launch processes
    processes = []
    use_terminal = sys.platform.startswith('linux')
    
    print(f"\nLaunching {num_processes} processes...")
    print("(Each process will open in a new terminal window)\n" if use_terminal else 
          "(Processes running in background)\n")
    
    for i in range(num_processes):
        try:
            proc = launch_process(i, num_messages, messages_per_minute, use_terminal)
            processes.append(proc)
            print(f"  ✓ Launched Process {i}")
            time.sleep(0.5)  # Small delay giữa các launches
        except Exception as e:
            print(f"  ✗ Failed to launch Process {i}: {e}")
    
    print()
    print("=" * 80)
    print(f"Successfully launched {len(processes)} processes!")
    print("=" * 80)
    print()
    print("Monitoring:")
    print("  - Check 'logs/' directory for detailed logs")
    print("  - Each process has its own log file: logs/process_X.log")
    print()
    print("Commands:")
    print("  - Press Ctrl+C to stop all processes")
    print("  - Use 'make analyze' to analyze logs after completion")
    print("=" * 80)
    print()
    
    # Đợi processes
    try:
        print("Waiting for processes to complete...")
        print("(This may take several minutes depending on message rate)")
        print()
        
        # Kiểm tra processes định kỳ
        all_done = False
        while not all_done:
            time.sleep(5)
            
            # Đếm processes còn chạy
            running = sum(1 for p in processes if p.poll() is None)
            
            if running == 0:
                all_done = True
            else:
                print(f"  Status: {running}/{len(processes)} processes still running...")
        
        print()
        print("=" * 80)
        print("All processes completed!")
        print("=" * 80)
        print()
        print("Next steps:")
        print("  1. Check logs: ls -lh logs/")
        print("  2. Analyze results: python3 src/log_analyzer.py")
        print("  3. View specific log: tail -f logs/process_0.log")
        print()
    
    except KeyboardInterrupt:
        print()
        print()
        print("=" * 80)
        print("Stopping all processes...")
        print("=" * 80)
        
        # Terminate tất cả processes
        for i, proc in enumerate(processes):
            if proc.poll() is None:
                print(f"  Stopping Process {i}...")
                try:
                    proc.terminate()
                except:
                    pass
        
        # Đợi một chút
        time.sleep(2)
        
        # Kill nếu vẫn còn chạy
        for proc in processes:
            if proc.poll() is None:
                try:
                    proc.kill()
                except:
                    pass
        
        print()
        print("All processes stopped.")
        print()


if __name__ == '__main__':
    main()
