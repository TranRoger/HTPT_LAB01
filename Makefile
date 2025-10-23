# Makefile for SES Project

.PHONY: all help setup run run-test analyze clean logs kill verify

# Default target
all: help

# Setup project
setup:
	@echo "Setting up SES project..."
	@chmod +x src/ses_process.py
	@chmod +x src/launch_all.py
	@chmod +x src/log_analyzer.py
	@mkdir -p logs
	@echo "✓ Setup complete!"

# Run full demo (15 processes, 150 messages each)
run:
	@echo "Starting 15 SES processes..."
	@python3 src/launch_all.py

# Run with custom parameters
# Usage: make run-custom MSGS=200 RATE=50
run-custom:
	@python3 src/launch_all.py $(MSGS) $(RATE)

# Quick test (10 messages per process)
run-test:
	@echo "Running quick test..."
	@python3 src/launch_all.py 10 200

# Run single process
# Usage: make run-single PID=0 MSGS=150 RATE=100
run-single:
	@python3 src/ses_process.py $(PID) $(MSGS) $(RATE)

# Analyze all logs
analyze:
	@echo "Analyzing logs..."
	@python3 src/log_analyzer.py

# Analyze specific process
# Usage: make analyze-process PID=0
analyze-process:
	@python3 src/log_analyzer.py $(PID)

# List log files
logs:
	@echo "Log files:"
	@ls -lh logs/ 2>/dev/null || echo "No logs found"

# Tail specific log
# Usage: make tail PID=0
tail:
	@tail -f logs/process_$(PID).log

# Show log summary
log-summary:
	@echo "Log Summary:"
	@echo ""
	@for i in {0..14}; do \
		if [ -f logs/process_$$i.log ]; then \
			delivered=$$(grep -c "✓ DELIVERED" logs/process_$$i.log 2>/dev/null || echo "0"); \
			buffered=$$(grep -c "⊕ BUFFERED" logs/process_$$i.log 2>/dev/null || echo "0"); \
			echo "Process $$i: $$delivered delivered, $$buffered buffered"; \
		fi \
	done

# Clean logs
clean-logs:
	@echo "Cleaning log files..."
	@rm -f logs/process_*.log
	@echo "✓ Logs cleaned!"

# Clean all generated files
clean: clean-logs
	@echo "Cleaning generated files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@echo "✓ Clean complete!"

# Kill all running processes
kill:
	@echo "Killing all SES processes..."
	@pkill -f "ses_process.py" || echo "No processes running"
	@echo "✓ All processes killed!"

# Check ports
check-ports:
	@echo "Checking ports 5000-5014..."
	@for port in {5000..5014}; do \
		if lsof -Pi :$$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then \
			echo "Port $$port is in use"; \
		fi \
	done

# Verify installation
verify:
	@echo "Verifying setup..."
	@python3 --version
	@echo "✓ Python OK"
	@test -f config/config.json && echo "✓ Config OK" || echo "✗ Config missing"
	@test -f src/ses_process.py && echo "✓ ses_process.py OK" || echo "✗ ses_process.py missing"
	@test -d logs && echo "✓ logs/ OK" || echo "✗ logs/ missing"

# Count messages
count:
	@echo "Counting messages..."
	@total_sent=$$(grep -rh "→ SENT" logs/ 2>/dev/null | wc -l); \
	total_received=$$(grep -rh "← RECEIVED" logs/ 2>/dev/null | wc -l); \
	total_delivered=$$(grep -rh "✓ DELIVERED" logs/ 2>/dev/null | wc -l); \
	total_buffered=$$(grep -rh "⊕ BUFFERED" logs/ 2>/dev/null | wc -l); \
	echo "Total SENT:      $$total_sent"; \
	echo "Total RECEIVED:  $$total_received"; \
	echo "Total DELIVERED: $$total_delivered"; \
	echo "Total BUFFERED:  $$total_buffered"

# Help
help:
	@echo "================================"
	@echo "SES Project - Makefile Commands"
	@echo "================================"
	@echo ""
	@echo "Setup:"
	@echo "  make setup           - Setup project (make scripts executable)"
	@echo "  make verify          - Verify installation"
	@echo ""
	@echo "Running:"
	@echo "  make run             - Run full demo (15 processes, 150 msgs)"
	@echo "  make run-test        - Quick test (10 msgs)"
	@echo "  make run-custom MSGS=200 RATE=50 - Custom parameters"
	@echo "  make run-single PID=0 MSGS=150 RATE=100 - Run single process"
	@echo ""
	@echo "Analysis:"
	@echo "  make analyze         - Analyze all logs"
	@echo "  make analyze-process PID=0 - Analyze specific process"
	@echo "  make count           - Count messages"
	@echo ""
	@echo "Logs:"
	@echo "  make logs            - List log files"
	@echo "  make tail PID=0      - Tail specific log"
	@echo "  make log-summary     - Show log summary"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean-logs      - Clean log files"
	@echo "  make clean           - Clean all generated files"
	@echo "  make kill            - Kill all running processes"
	@echo "  make check-ports     - Check if ports are in use"
	@echo ""
