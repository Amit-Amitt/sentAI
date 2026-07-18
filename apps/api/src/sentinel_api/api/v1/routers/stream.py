import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from sentinel_api.services.telemetry_pipeline import redis_conn

router = APIRouter(prefix="/stream", tags=["stream"])

async def event_generator():
    """
    Subscribes to Redis PubSub for real-time telemetry streaming.
    """
    pubsub = redis_conn.pubsub()
    # PSubscribe allows us to listen to all workspaces, or we can listen to specific ones if authorized
    pubsub.psubscribe("telemetry_stream:*")
    
    try:
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                try:
                    data = json.loads(message["data"])
                    yield f"event: telemetry\ndata: {json.dumps(data)}\n\n"
                except Exception as e:
                    pass
            
            await asyncio.sleep(0.1)
    finally:
        pubsub.punsubscribe()
        pubsub.close()

@router.get("/dashboard")
async def stream_dashboard():
    """
    SSE endpoint for the live command center.
    """
    return StreamingResponse(event_generator(), media_type="text/event-stream")
