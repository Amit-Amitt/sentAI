import os
import sys
import redis
from rq import Worker, Queue, Connection

# Ensure the app is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from sentinel_api.config.settings import settings

listen = ['telemetry_ingestion']

redis_conn = redis.from_url(settings.REDIS_URL)

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(map(Queue, listen))
        worker.work()
