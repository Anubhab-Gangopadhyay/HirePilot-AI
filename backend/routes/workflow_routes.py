from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from agents.orchestrator_agent import orchestrator, state_manager
from models.workflow_models import AgentActionRequest, ApproveApplicationRequest, PrepareApplicationRequest, ResumeUploadResponse, WorkflowResponse, WorkflowStartRequest
from models.workflow_models import LogLevel
from services.log_service import log_service
from services.sheets_service import sheets_service
from utils.helpers import normalize_text

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


@router.post("/upload-resume", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)) -> ResumeUploadResponse:
    raw = await file.read()
    resume_text = _extract_resume_text(raw, file.filename or "resume.txt")
    state = state_manager.save_uploaded_resume(resume_text, file.filename or "resume.txt")
    await log_service.emit(state, "Orchestrator", "Resume uploaded and stored in workflow state")
    return ResumeUploadResponse(
        workflow_id=state.workflow_id,
        filename=file.filename or "resume.txt",
        resume_text=resume_text,
    )


@router.post("/start", response_model=WorkflowResponse)
async def start_workflow(payload: WorkflowStartRequest, background_tasks: BackgroundTasks) -> WorkflowResponse:
    if payload.workflow_id and state_manager.get(payload.workflow_id):
        state = state_manager.get(payload.workflow_id)
        state.uploaded_resume = payload.resume_text or state.uploaded_resume
        state.preferred_role = payload.preferred_role
        state.preferred_location = payload.preferred_location
        state.experience = payload.experience
        state.remote_preference = payload.remote_preference
        state_manager.upsert(state)
    else:
        state = state_manager.create(payload)

    background_tasks.add_task(orchestrator.run_workflow, state.workflow_id)
    return WorkflowResponse(workflow=state)


@router.post("/run-sync", response_model=WorkflowResponse)
async def run_workflow_sync(payload: WorkflowStartRequest) -> WorkflowResponse:
    state = await orchestrator.start(payload)
    return WorkflowResponse(workflow=state)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str) -> WorkflowResponse:
    state = _get_state_or_404(workflow_id)
    return WorkflowResponse(workflow=state)


@router.get("/{workflow_id}/logs")
async def get_logs(workflow_id: str, after: int = 0) -> JSONResponse:
    state = _get_state_or_404(workflow_id)
    logs = log_service.get_logs(state, after=after)
    return JSONResponse({
        "workflow_id": workflow_id,
        "count": len(logs),
        "logs": [log.model_dump(mode="json") for log in logs],
    })


@router.websocket("/{workflow_id}/logs/ws")
async def stream_logs(websocket: WebSocket, workflow_id: str) -> None:
    await websocket.accept()
    state = state_manager.get(workflow_id)
    if not state:
        await websocket.send_json({"type": "error", "message": "Workflow not found"})
        await websocket.close()
        return

    for log in state.logs:
        await websocket.send_json({"type": "log", "data": log.model_dump(mode="json")})

    queue = log_service.register(workflow_id)
    try:
        while True:
            try:
                log = await asyncio.wait_for(queue.get(), timeout=25)
                await websocket.send_json({"type": "log", "data": log.model_dump(mode="json")})
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "heartbeat", "workflow_id": workflow_id})
    except WebSocketDisconnect:
        pass
    finally:
        log_service.unregister(workflow_id, queue)


@router.get("/{workflow_id}/jobs")
async def get_jobs(workflow_id: str) -> JSONResponse:
    state = _get_state_or_404(workflow_id)
    return JSONResponse({
        "workflow_id": workflow_id,
        "jobs": [job.model_dump() for job in state.jobs_found],
        "results": [_result_summary(result) for result in state.job_results],
        "selected_job": state.selected_job.model_dump() if state.selected_job else None,
    })


@router.get("/{workflow_id}/ats-score")
async def get_ats_score(workflow_id: str) -> JSONResponse:
    state = _get_state_or_404(workflow_id)
    return JSONResponse({
        "workflow_id": workflow_id,
        "ats_score": state.ats_score,
        "resume_optimization": state.optimized_resume.model_dump(),
        "per_job_scores": [
            {
                "job_id": result.job_id,
                "company": result.job.company,
                "role": result.job.role,
                "platform": result.job.source,
                "ats_score": result.resume.ats_score,
                "missing_keywords": result.resume.missing_keywords,
            }
            for result in state.job_results
        ],
    })


@router.post("/optimize-resume", response_model=WorkflowResponse)
async def optimize_resume(payload: AgentActionRequest) -> WorkflowResponse:
    state = _get_state_or_404(payload.workflow_id)
    _select_job(state, payload.job_index)
    state = await orchestrator.resume_agent.run(state)
    state_manager.upsert(state)
    return WorkflowResponse(workflow=state)


@router.post("/analyze-skill-gap", response_model=WorkflowResponse)
async def analyze_skill_gap(payload: AgentActionRequest) -> WorkflowResponse:
    state = _get_state_or_404(payload.workflow_id)
    _select_job(state, payload.job_index)
    state = await orchestrator.skill_gap_agent.run(state)
    state_manager.upsert(state)
    return WorkflowResponse(workflow=state)


@router.post("/prepare-application", response_model=WorkflowResponse)
async def prepare_application(payload: PrepareApplicationRequest) -> WorkflowResponse:
    state = _get_state_or_404(payload.workflow_id)
    _select_job(state, payload.job_index)
    if payload.application_url and state.selected_job:
        state.selected_job.url = payload.application_url
    state = await orchestrator.apply_agent.run(state)
    state_manager.upsert(state)
    return WorkflowResponse(workflow=state)


@router.post("/approve-application", response_model=WorkflowResponse)
async def approve_application(payload: ApproveApplicationRequest) -> WorkflowResponse:
    state = _get_state_or_404(payload.workflow_id)
    if not payload.human_approved:
        raise HTTPException(status_code=400, detail="Human approval is required before applying.")

    target_result = None
    if payload.job_id:
        target_result = next((result for result in state.job_results if result.job_id == payload.job_id), None)
        if not target_result:
            raise HTTPException(status_code=404, detail="Job result not found")

    application = target_result.application if target_result else state.application_status
    application.status = "approved"
    application.approval_state = "approved_by_human"
    application.ready_to_submit = True
    application.notes.append("Human approved the prepared application.")
    application.browser_steps.append("Approve & Apply clicked by user")
    if target_result:
        target_result.application = application
        target_result.status = "approved_by_human"
        target_result.sheet_sync = await sheets_service.sync_result(state, target_result)
    state.application_status = application
    await log_service.emit(
        state,
        "Apply Agent",
        "Human approved application. Ready for final job-platform submission.",
        LogLevel.success,
        {"application_url": application.application_url, "job_id": payload.job_id},
    )
    state_manager.upsert(state)
    return WorkflowResponse(workflow=state)


@router.get("/{workflow_id}/skill-gap")
async def get_skill_gap(workflow_id: str) -> JSONResponse:
    state = _get_state_or_404(workflow_id)
    return JSONResponse({
        "workflow_id": workflow_id,
        "missing_skills": state.missing_skills,
        "analysis": state.skill_gap.model_dump(),
        "per_job_skill_gaps": [
            {
                "job_id": result.job_id,
                "company": result.job.company,
                "role": result.job.role,
                "skill_match_score": result.skill_gap.skill_match_percent,
                "missing_skills": result.skill_gap.missing_skills,
                "recommendations": result.skill_gap.recommendations,
            }
            for result in state.job_results
        ],
    })


@router.get("/{workflow_id}/recommendations")
async def get_recommendations(workflow_id: str) -> JSONResponse:
    state = _get_state_or_404(workflow_id)
    return JSONResponse({
        "workflow_id": workflow_id,
        "recommendations": state.skill_gap.recommendations,
        "project_suggestions": state.skill_gap.project_suggestions,
        "learning_roadmap": state.skill_gap.learning_roadmap,
        "market_demand": state.skill_gap.market_demand,
        "approval_state": state.application_status.approval_state,
    })


@router.get("/{workflow_id}/tailored-resumes")
async def get_tailored_resumes(workflow_id: str) -> JSONResponse:
    state = _get_state_or_404(workflow_id)
    return JSONResponse({
        "workflow_id": workflow_id,
        "tailored_resumes": [
            {
                "job_id": result.job_id,
                "company": result.job.company,
                "role": result.job.role,
                "platform": result.job.source,
                "apply_link": result.job.url,
                "ats_score": result.resume.ats_score,
                "missing_keywords": result.resume.missing_keywords,
                "optimized_resume": result.resume.optimized_resume,
                "cover_letter": result.resume.cover_letter,
            }
            for result in state.job_results
        ],
    })


@router.get("/{workflow_id}/applications")
async def get_application_links(workflow_id: str) -> JSONResponse:
    state = _get_state_or_404(workflow_id)
    return JSONResponse({
        "workflow_id": workflow_id,
        "applications": [
            {
                "job_id": result.job_id,
                "company": result.job.company,
                "role": result.job.role,
                "platform": result.job.source,
                "apply_link": result.job.url,
                "status": result.application.approval_state,
                "ready_to_submit": result.application.ready_to_submit,
                "sheet_sync": result.sheet_sync.model_dump(mode="json"),
            }
            for result in state.job_results
        ],
    })


def _get_state_or_404(workflow_id: str):
    state = state_manager.get(workflow_id)
    if not state:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return state


def _select_job(state, job_index: int):
    if not state.jobs_found:
        raise HTTPException(status_code=400, detail="No jobs found. Start the workflow or run the Job Agent first.")
    if job_index >= len(state.jobs_found):
        raise HTTPException(status_code=400, detail="job_index is outside the jobs_found range")
    state.selected_job = state.jobs_found[job_index]
    return state.selected_job


def _result_summary(result):
    return {
        "job_id": result.job_id,
        "company": result.job.company,
        "role": result.job.role,
        "platform": result.job.source,
        "location": result.job.location,
        "ats_score": result.resume.ats_score,
        "skill_match_score": result.skill_gap.skill_match_percent,
        "missing_skills": result.skill_gap.missing_skills,
        "status": result.application.approval_state,
        "apply_link": result.job.url,
        "sheet_sync": result.sheet_sync.model_dump(mode="json"),
    }


def _extract_resume_text(raw: bytes, filename: str) -> str:
    # Hackathon-friendly parser: handles txt/md cleanly and gives useful text for PDF/DOCX demos.
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError:
        decoded = raw.decode("latin-1", errors="ignore")

    text = normalize_text(decoded)
    if text:
        return text[:12000]

    return (
        f"Uploaded resume file {filename}. Backend developer with API, database, "
        "Node.js, Python, SQL, and deployment project experience."
    )
