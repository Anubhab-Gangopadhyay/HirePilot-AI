from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    idle = "idle"
    running = "running"
    completed = "completed"
    failed = "failed"


class WorkflowStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class LogLevel(str, Enum):
    info = "info"
    success = "success"
    warning = "warning"
    error = "error"


class ResumeUploadResponse(BaseModel):
    workflow_id: str
    filename: str
    resume_text: str


class WorkflowStartRequest(BaseModel):
    workflow_id: str | None = None
    resume_text: str = Field(default="", description="Extracted resume text or pasted resume content.")
    preferred_role: str = "Backend Developer"
    preferred_location: str = "Bangalore"
    experience: str = "1-2 Years"
    remote_preference: bool = True


class AgentActionRequest(BaseModel):
    workflow_id: str
    job_index: int = Field(default=0, ge=0)


class PrepareApplicationRequest(BaseModel):
    workflow_id: str
    job_index: int = Field(default=0, ge=0)
    application_url: str | None = None
    candidate_name: str = "HirePilot Candidate"
    candidate_email: str = "candidate@example.com"
    candidate_phone: str = "+91 90000 00000"


class ApproveApplicationRequest(BaseModel):
    workflow_id: str
    human_approved: bool = False
    job_id: str | None = None


class JobOpportunity(BaseModel):
    role: str
    company: str
    location: str
    description: str
    skills: list[str] = Field(default_factory=list)
    source: str = "Mock"
    match_score: int = Field(default=80, ge=0, le=100)
    url: str | None = None

    @property
    def apply_link(self) -> str | None:
        return self.url


class ResumeOptimization(BaseModel):
    optimized_resume: str = ""
    ats_score: int = Field(default=0, ge=0, le=100)
    missing_keywords: list[str] = Field(default_factory=list)
    improved_summary: str = ""
    tailored_projects: list[str] = Field(default_factory=list)
    cover_letter: str = ""
    extracted_keywords: list[str] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)
    section_scores: dict[str, int] = Field(default_factory=dict)
    relevance_score: int = Field(default=0, ge=0, le=100)


class SkillGapAnalysis(BaseModel):
    missing_skills: list[str] = Field(default_factory=list)
    weak_areas: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    project_suggestions: list[str] = Field(default_factory=list)
    learning_roadmap: list[str] = Field(default_factory=list)
    market_demand: list[str] = Field(default_factory=list)
    resume_skills: list[str] = Field(default_factory=list)
    job_skills: list[str] = Field(default_factory=list)
    skill_match_percent: int = Field(default=0, ge=0, le=100)


class ApplicationPreparation(BaseModel):
    status: str = "pending"
    prepared_count: int = 0
    notes: list[str] = Field(default_factory=list)
    approval_required: bool = True
    approval_state: str = "waiting_for_human_review"
    application_url: str | None = None
    autofilled_fields: dict[str, str] = Field(default_factory=dict)
    browser_steps: list[str] = Field(default_factory=list)
    ready_to_submit: bool = False


class SheetSyncStatus(BaseModel):
    status: str = "pending"
    provider: str = "local"
    row_id: str | None = None
    message: str = ""
    updated_at: datetime | None = None


class JobApplicationResult(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid4()))
    job: JobOpportunity
    resume: ResumeOptimization = Field(default_factory=ResumeOptimization)
    skill_gap: SkillGapAnalysis = Field(default_factory=SkillGapAnalysis)
    application: ApplicationPreparation = Field(default_factory=ApplicationPreparation)
    sheet_sync: SheetSyncStatus = Field(default_factory=SheetSyncStatus)
    status: str = "waiting_for_approval"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkflowLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    agent: str
    message: str
    level: LogLevel = LogLevel.info
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowState(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid4()))
    status: WorkflowStatus = WorkflowStatus.queued
    uploaded_resume: str = ""
    preferred_role: str = "Backend Developer"
    preferred_location: str = "Bangalore"
    experience: str = "1-2 Years"
    remote_preference: bool = True
    jobs_found: list[JobOpportunity] = Field(default_factory=list)
    selected_job: JobOpportunity | None = None
    optimized_resume: ResumeOptimization = Field(default_factory=ResumeOptimization)
    ats_score: int = 0
    missing_skills: list[str] = Field(default_factory=list)
    skill_gap: SkillGapAnalysis = Field(default_factory=SkillGapAnalysis)
    application_status: ApplicationPreparation = Field(default_factory=ApplicationPreparation)
    job_results: list[JobApplicationResult] = Field(default_factory=list)
    sheet_sync_status: SheetSyncStatus = Field(default_factory=SheetSyncStatus)
    agent_status: dict[str, AgentStatus] = Field(default_factory=lambda: {
        "orchestrator": AgentStatus.idle,
        "job_agent": AgentStatus.idle,
        "resume_agent": AgentStatus.idle,
        "skill_gap_agent": AgentStatus.idle,
        "apply_agent": AgentStatus.idle,
    })
    logs: list[WorkflowLog] = Field(default_factory=list)
    intermediate_outputs: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkflowResponse(BaseModel):
    workflow: WorkflowState
