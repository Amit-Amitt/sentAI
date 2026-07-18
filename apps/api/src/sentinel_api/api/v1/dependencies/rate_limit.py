from fastapi import Request


async def rate_limiter(request: Request) -> None:
    """Rate limiting hook placeholder (e.g. for redis sliding window)."""
    pass
