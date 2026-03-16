from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import asyncio

from agent.agent import run_agent, book_charger

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("ui/index.html", "r") as f:
        return HTMLResponse(content=f.read())


class ChatRequest(BaseModel):
    message: str
    mode:    str = "browse"


class BookRequest(BaseModel):
    charger_id: str


async def sse_stream(generator):
    try:
        async for chunk in generator:
            yield f"data: {chunk}\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: ❌ Error: {str(e)}\n"
        yield "data: [DONE]\n\n"


@app.post("/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(
        sse_stream(run_agent(request.message, request.mode)),
        media_type="text/event-stream",
        headers={
            "Cache-Control":    "no-cache",
            "Connection":       "keep-alive",
            "X-Accel-Buffering":"no"
        }
    )


@app.post("/book")
async def book(request: BookRequest):
    return StreamingResponse(
        sse_stream(book_charger(request.charger_id)),
        media_type="text/event-stream",
        headers={
            "Cache-Control":    "no-cache",
            "Connection":       "keep-alive",
            "X-Accel-Buffering":"no"
        }
    )


# ── WALLET ROUTES FOR UI ──────────────────────────────────────
@app.get("/wallet/balance")
async def wallet_balance():
    async with httpx.AsyncClient() as client:
        r = await client.get("http://localhost:8000/tools/wallet/balance")
        return r.json()


@app.post("/wallet/topup")
async def wallet_topup():
    async with httpx.AsyncClient() as client:
        r = await client.post("http://localhost:8000/tools/wallet/topup")
        return r.json()