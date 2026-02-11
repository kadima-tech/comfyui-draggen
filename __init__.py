from .nodes import (
    DraggenLocalMoodboardLoader,
    DraggenRemoteMoodboardLoader,
    DraggenMoodboardRendered,
    DraggenMoodboardImages,
    DraggenMoodboardText
)

import server
from aiohttp import web
from .draggen_client import DraggenClient

@server.PromptServer.instance.routes.get("/draggen/api/list_boards")
async def list_boards(request):
    api_key = request.headers.get("x-api-key")
    
    if not api_key:
        return web.Response(text="API Key is required", status=400)
    
    try:
        client = DraggenClient(api_key=api_key)
        boards = client.list_boards()
        return web.json_response({"boards": boards})
    except Exception as e:
        return web.Response(text=str(e), status=500)

NODE_CLASS_MAPPINGS = {
    "DraggenLocalMoodboardLoader": DraggenLocalMoodboardLoader,
    "DraggenRemoteMoodboardLoader": DraggenRemoteMoodboardLoader,
    "DraggenMoodboardRendered": DraggenMoodboardRendered,
    "DraggenMoodboardImages": DraggenMoodboardImages,
    "DraggenMoodboardText": DraggenMoodboardText
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DraggenLocalMoodboardLoader": "Draggen Local Loader",
    "DraggenRemoteMoodboardLoader": "Draggen Remote Loader",
    "DraggenMoodboardRendered": "Draggen Board to Image",
    "DraggenMoodboardImages": "Draggen Extract Images",
    "DraggenMoodboardText": "Draggen Extract Text"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

WEB_DIRECTORY = "./web/js"
