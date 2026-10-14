"""FastAPI サーバ（main.py）
alternative-beat-sampler の Web アプリケーションサーバ。
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

import credentials
credentials.configure()

from agent import root_agent
import store

APP_NAME = "alternative_beat_sampler"
_USER_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,80}$")

app = FastAPI(title="alternative-beat-sampler")
session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
_sessions: dict[str, str] = {}


async def _session_id_for(user_id: str) -> str:
    sid = _sessions.get(user_id)
    if sid:
        sess = await session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=sid)
        if sess is not None:
            return sid
    sess = await session_service.create_session(app_name=APP_NAME, user_id=user_id)
    _sessions[user_id] = sess.id
    return sess.id


@app.get("/health")
async def health():
    return {"status": "ok", "agent": root_agent.name}


@app.get("/api/state")
async def get_state():
    return store.get_state()


@app.post("/api/pattern")
async def set_pattern(request: Request):
    body = await request.json()
    track = body.get("track")
    steps = body.get("steps")
    if track and isinstance(steps, list):
        store.update_pattern(track, steps)
        return {"status": "success", "state": store.get_state()}
    return JSONResponse({"status": "error", "message": "Invalid pattern data"}, status_code=400)


@app.post("/api/parameters")
async def set_parameters(request: Request):
    body = await request.json()
    tempo_bpm = body.get("tempo_bpm")
    filter_cutoff = body.get("filter_cutoff")
    pitch = body.get("pitch")
    volume = body.get("volume")
    store.update_parameters(tempo_bpm=tempo_bpm, filter_cutoff=filter_cutoff, pitch=pitch, volume=volume)
    return {"status": "success", "state": store.get_state()}


@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = str(body.get("message", "")).strip()
    user_id = str(body.get("user_id") or "web-user")
    if not _USER_ID_RE.match(user_id):
        user_id = "web-user"
    if not message:
        return JSONResponse({"reply": "", "state": store.get_state()})

    session_id = await _session_id_for(user_id)
    content = types.Content(role="user", parts=[types.Part.from_text(text=message)])
    final_text = ""
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.content and event.author == root_agent.name:
            texts = [p.text for p in event.content.parts or [] if getattr(p, "text", None)]
            if texts:
                final_text = "\n".join(texts)

    reply_text = final_text.strip() or "(応答がありませんでした)"
    # 最新の store 状態も添えて返すことで、画面側がAIの操作結果を即座にUIへ反映できるようにする
    return JSONResponse({
        "reply": reply_text,
        "state": store.get_state(),
    })


# static 配信
STATIC_DIR = Path(__file__).parent / "static"
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.is_file():
        return FileResponse(str(index_file))
    return JSONResponse({"message": "alternative-beat-sampler backend is running"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
