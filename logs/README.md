# Logs Directory

This directory contains log files for each SES process.

Log files are automatically generated when processes run:
- `process_0.log` - Process 0
- `process_1.log` - Process 1
- ...
- `process_14.log` - Process 14

Each log file contains:
- Sent messages
- Received messages
- Delivered messages
- Buffered messages
- Vector clock updates
- Statistics

## View Logs

```bash
# List all logs
ls -lh logs/

# View specific log
cat logs/process_0.log

# Tail log (real-time)
tail -f logs/process_0.log

# Analyze logs
python3 src/log_analyzer.py
```
