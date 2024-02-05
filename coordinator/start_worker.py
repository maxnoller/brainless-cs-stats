from rq import Worker
from redis import Redis
import os

redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
redis_db = int(os.environ.get('REDIS_DB', 0))
redis_password = os.environ.get('REDIS_PASSWORD', None)

redis_conn = Redis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)

# Start the worker using the custom worker class
worker = Worker(connection=redis_conn)
worker.work()
