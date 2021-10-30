"""
ASGI config for api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
import asyncio
import logging
from websockets import connect


from django.core.asgi import get_asgi_application
# Get an instance of a logger
logger = logging.getLogger(__name__)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "websocket_app.settings")

django_application = get_asgi_application()


async def application(scope, receive, send):
    # if "headers" not in scope:
    #     raise Exception("Headers not found in scope")
    # cookie = dict(scope["headers"]).get(b"cookie")
    if scope["type"] == "http":
        await django_application(scope, receive, send)
    elif scope["type"] == "websocket":
        await websocket_cuelake_redirect_application(scope, receive, send)
    elif scope["type"] == "lifespan":
        logger.info("Lifespan not supported")
        # await django_application(scope, receive, send)
    else:
        raise NotImplementedError(f"Unknown scope type {scope['type']}")

async def listen_to_zeppelin(ws, send):
    while True:
        text = await ws.recv()
        await send({"type": "websocket.send", "text": text})


async def websocket_cuelake_redirect_application(scope, receive, send):
    url = "ws://localhost:8080/ws/"
    if os.environ.get("ENVIRONMENT","") != "dev":
        pathArray = scope.get('path', '').split('/')
        if pathArray[3]:
            url = f"ws://zeppelin-server-{pathArray[3]}/ws/"
    async with connect(url, max_size=10000000) as ws:
        task = asyncio.create_task(listen_to_zeppelin(ws, send))
        while True:
            event = await receive()
            if event["type"] == "websocket.connect":
                await send({"type": "websocket.accept"})

            if event["type"] == "websocket.disconnect":
                break

            if event["type"] == "websocket.receive":
                await ws.send(event["text"])
