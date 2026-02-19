from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import asyncio
import uuid
import json
import os

from config import settings
from llm_router import FreeLLMRouter
from db import db
from storage import storage
from agent import Agent
from ws_manager import ConnectionManager

# ═══════════════════
# Globals
# ═══════════════════

llm_router: FreeLLMRouter = None
ws_manager = ConnectionManager()
active_tasks = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm_router
    llm_router = FreeLLMRouter()
    os.makedirs(settings.WORKSPACE_ROOT, exist_ok=True)

    # Init database tables
    await db.init_tables()

    print("🚀 Luxor9 Backend — Free Cloud Edition")
    print(f"🧠 LLM Providers: {list(llm_router.providers.keys())}")
    print(f"🗄️  Database: Neon PostgreSQL")
    yield


app = FastAPI(title="Luxor9", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════
# REST API
# ═══════════════════

@app.post("/api/tasks")
async def create_task(request: dict):
    task_id = str(uuid.uuid4())
    description = request.get("description", "").strip()

    if not description:
        raise HTTPException(400, "description required")

    config = request.get("config", {})
    await db.create_task(task_id, description, config)

    asyncio.create_task(run_task(task_id, description, config))

    return {"task_id": task_id, "status": "pending"}


@app.get("/api/tasks")
async def list_tasks():
    return await db.list_tasks(50)


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    task = await db.get_task(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@app.get("/api/tasks/{task_id}/turns")
async def get_turns(task_id: str):
    return await db.get_task_turns(task_id)


@app.get("/api/tasks/{task_id}/files")
async def list_files(task_id: str):
    workspace = os.path.join(settings.WORKSPACE_ROOT, task_id)
    if not os.path.exists(workspace):
        return {"files": []}

    files = []
    for root, dirs, filenames in os.walk(workspace):
        for f in filenames:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, workspace)
            size = os.path.getsize(full)
            files.append({"path": rel, "size": size})

    return {"files": files}


@app.get("/api/tasks/{task_id}/files/{path:path}")
async def download_file(task_id: str, path: str):
    filepath = os.path.join(settings.WORKSPACE_ROOT, task_id, path)
    filepath = os.path.normpath(filepath)
    workspace = os.path.normpath(os.path.join(settings.WORKSPACE_ROOT, task_id))

    if not filepath.startswith(workspace):
        raise HTTPException(403, "Forbidden")
    if not os.path.exists(filepath):
        raise HTTPException(404, "File not found")

    return FileResponse(filepath)


@app.post("/api/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    if task_id in active_tasks:
        active_tasks[task_id]["agent"].cancel()
    await db.update_task(task_id, status="cancelled")
    return {"status": "cancelled"}


@app.post("/api/tasks/{task_id}/message")
async def send_message(task_id: str, request: dict):
    message = request.get("message", "").strip()
    if not message:
        raise HTTPException(400, "message required")
    if task_id in active_tasks:
        active_tasks[task_id]["agent"].inject_message(message)
    return {"status": "sent"}


@app.get("/api/llm/status")
async def llm_status():
    return llm_router.get_status()


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": "0.2.0",
        "providers": list(llm_router.providers.keys()),
        "active_tasks": len(active_tasks),
    }


# ═══════════════════
# WEBSOCKET
# ═══════════════════

@app.websocket("/ws/task/{task_id}")
async def task_ws(websocket: WebSocket, task_id: str):
    await ws_manager.connect(websocket, task_id)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "user_message" and task_id in active_tasks:
                active_tasks[task_id]["agent"].inject_message(msg.get("content", ""))
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, task_id)


# ═══════════════════
# TASK EXECUTION
# ═══════════════════

async def run_task(task_id: str, description: str, config: dict):
    """Execute a task using the agent."""
    workspace = os.path.join(settings.WORKSPACE_ROOT, task_id)
    os.makedirs(workspace, exist_ok=True)

    await db.update_task(task_id, status="running")

    async def emit(event: dict):
        event["task_id"] = task_id
        await ws_manager.broadcast_to_task(task_id, event)

    agent = Agent(
        name=task_id,
        role="general",
        llm_router=llm_router,
        workspace_path=workspace,
        event_callback=emit,
        database=db,
    )

    active_tasks[task_id] = {"agent": agent}

    try:
        await emit({"type": "task_started", "content": {"description": description}})

        result = await agent.run(description)

        await db.update_task(
            task_id,
            status="completed",
            result_summary=result[:5000],
            total_turns=agent.turn_count,
            total_tokens=agent.total_tokens,
            provider_stats=dict(agent.provider_stats),
        )

        await emit({
            "type": "task_complete",
            "content": {
                "summary": result,
                "turns": agent.turn_count,
                "tokens": agent.total_tokens,
                "providers_used": dict(agent.provider_stats),
            }
        })

    except Exception as e:
        await db.update_task(task_id, status="failed", result_summary=f"Error: {str(e)}")
        await emit({"type": "error", "content": {"error": str(e)}})

    finally:
        if task_id in active_tasks:
            del active_tasks[task_id]
        from tools.browser import close_browser_session
        await close_browser_session(task_id)
