# Gunicorn configuration for production
import os
import multiprocessing

# Server socket - Use PORT from environment (Render sets this automatically)
# If PORT is set (like on Render), use it. Otherwise default to 8000
port = os.environ.get("PORT", "8000")
bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker processes
workers = 4
worker_class = "sync"  # Use sync worker to avoid gevent warnings
timeout = 60
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "sovereign_habit_app"

# Server mechanics
daemon = False

# Production optimizations
max_requests = 10000
max_requests_jitter = 1000
