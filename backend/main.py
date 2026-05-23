from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.workflow_routes import router as workflow_router

app = FastAPI(
    title="HirePilot AI Backend",
    description="Autonomous multi-agent job application copilot powered by FastAPI and CrewAI-style orchestration.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3001", "http://localhost:3001", "http://127.0.0.1:3000", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workflow_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "hirepilot-ai-backend"}


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "HirePilot AI",
        "phase": "Phase 2",
        "docs": "/docs",
        "health": "/health",
    }
