# Gunicorn configuration for production
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = 4
worker_class = "gunicorn.workers.ggevent.GeventWorker"
worker_connections = 1000
timeout = 60
keepalive = 5


# Early monkey-patch for gevent
def post_fork(server, worker):
    """Called just after a worker has been forked"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def when_ready(server):
    """Called just before the master process is initialized"""
    pass


# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "sovereign_habit_app"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Production optimizations
max_requests = 10000
max_requests_jitter = 1000
preload_app = False
