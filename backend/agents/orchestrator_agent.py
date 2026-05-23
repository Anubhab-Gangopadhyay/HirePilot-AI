from __future__ import annotations

from datetime import datetime, timezone

from agents.apply_agent import ApplyAgent
from agents.job_agent import JobAgent
from agents.resume_agent import ResumeAgent
from agents.skill_gap_agent import SkillGapAgent
from models.workflow_models import AgentStatus, LogLevel, WorkflowStartRequest, WorkflowState, WorkflowStatus
from services.log_service import WorkflowLogService, log_service
from services.sheets_service import SheetsService, sheets_service

try:
    from crewai import Agent, Crew, Process, Task
except Exception:  # pragma: no cover - optional dependency
    Agent = Crew = Process = Task = None


class WorkflowStateManager:
    """Simple in-memory state store for hackathon demos."""

    def __init__(self) -> None:
        self._states: dict[str, WorkflowState] = {}

    def create(self, payload: WorkflowStartRequest) -> WorkflowState:
        state = WorkflowState(
            workflow_id=payload.workflow_id or WorkflowState().workflow_id,
            uploaded_resume=payload.resume_text,
            preferred_role=payload.preferred_role,
            preferred_location=payload.preferred_location,
            experience=payload.experience,
            remote_preference=payload.remote_preference,
        )
        self._states[state.workflow_id] = state
        return state

    def save_uploaded_resume(self, resume_text: str, filename: str) -> WorkflowState:
        state = WorkflowState(uploaded_resume=resume_text)
        state.intermediate_outputs["upload"] = {"filename": filename}
        self._states[state.workflow_id] = state
        return state

    def get(self, workflow_id: str) -> WorkflowState | None:
        return self._states.get(workflow_id)

    def upsert(self, state: WorkflowState) -> WorkflowState:
        state.updated_at = datetime.now(timezone.utc)
        self._states[state.workflow_id] = state
        return state

    def all(self) -> list[WorkflowState]:
        return list(self._states.values())


class OrchestratorAgent:
    name = "orchestrator"

    def __init__(
        self,
        state_manager: WorkflowStateManager,
        logs: WorkflowLogService = log_service,
        sheets: SheetsService = sheets_service,
    ) -> None:
        self.state_manager = state_manager
        self.logs = logs
        self.sheets = sheets
        self.job_agent = JobAgent(logs)
        self.resume_agent = ResumeAgent(logs)
        self.skill_gap_agent = SkillGapAgent(logs)
        self.apply_agent = ApplyAgent(logs)
        self.crewai_agent = self._build_crewai_agent()
        self.crewai_crew = self._build_crewai_crew()

    def _build_crewai_agent(self):
        if Agent is None:
            return None
        return Agent(
            role="Workflow Orchestrator Agent",
            goal="Coordinate a sequential job application workflow across specialist agents.",
            backstory="A calm operations lead that maintains state, logs progress, and routes outputs between agents.",
            verbose=True,
            allow_delegation=True,
        )

    def _build_crewai_crew(self):
        if not all([Agent, Crew, Process, Task, self.crewai_agent]):
            return None

        tasks = [
            Task(
                description="Coordinate job discovery, resume optimization, skill gap analysis, and application preparation.",
                expected_output="A complete structured workflow state for the candidate.",
                agent=self.crewai_agent,
            )
        ]
        return Crew(agents=[self.crewai_agent], tasks=tasks, process=Process.sequential, verbose=True)

    async def start(self, payload: WorkflowStartRequest) -> WorkflowState:
        existing = self.state_manager.get(payload.workflow_id) if payload.workflow_id else None
        if existing:
            existing.uploaded_resume = payload.resume_text or existing.uploaded_resume
            existing.preferred_role = payload.preferred_role
            existing.preferred_location = payload.preferred_location
            existing.experience = payload.experience
            existing.remote_preference = payload.remote_preference
            state = self.state_manager.upsert(existing)
        else:
            state = self.state_manager.create(payload)

        await self.run_workflow(state.workflow_id)
        return self.state_manager.get(state.workflow_id) or state

    async def run_workflow(self, workflow_id: str) -> WorkflowState:
        state = self.state_manager.get(workflow_id)
        if state is None:
            raise ValueError(f"Workflow {workflow_id} not found")

        state.status = WorkflowStatus.running
        state.agent_status[self.name] = AgentStatus.running
        await self.logs.emit(state, "Orchestrator", "Workflow received. Resume uploaded.")

        try:
            state = await self.job_agent.run(state)
            await self._handoff(state, "Job Agent", "Resume Agent", f"{len(state.jobs_found)} scraped jobs passed for per-job tailoring")

            state = await self.resume_agent.run_for_all_jobs(state)
            await self._handoff(state, "Resume Agent", "Skill Gap Agent", "Tailored resumes passed for per-job employability analysis")

            state = await self.skill_gap_agent.run_for_all_jobs(state)
            await self._sync_sheet_rows(state)
            await self._handoff(state, "Skill Gap Agent", "Apply Agent", "Skill insights passed to application prep")

            state = await self.apply_agent.run_for_all_jobs(state)
            await self._sync_sheet_rows(state)
            state.status = WorkflowStatus.completed
            state.agent_status[self.name] = AgentStatus.completed
            await self.logs.emit(state, "Orchestrator", "Autonomous workflow completed", LogLevel.success)
        except Exception as exc:
            state.status = WorkflowStatus.failed
            state.agent_status[self.name] = AgentStatus.failed
            await self.logs.emit(state, "Orchestrator", f"Workflow failed: {exc}", LogLevel.error)
        finally:
            self.state_manager.upsert(state)

        return state

    async def _handoff(self, state: WorkflowState, sender: str, receiver: str, message: str) -> None:
        await self.logs.emit(
            state,
            "Orchestrator",
            f"{sender} → {receiver}: {message}",
            LogLevel.info,
            {"sender": sender, "receiver": receiver},
        )

    async def _sync_sheet_rows(self, state: WorkflowState) -> None:
        if not state.job_results:
            return

        synced = 0
        for result in state.job_results:
            result.sheet_sync = await self.sheets.sync_result(state, result)
            synced += 1

        state.sheet_sync_status = state.job_results[-1].sheet_sync
        await self.logs.emit(
            state,
            "Sheets Service",
            f"Google Sheet tracking updated for {synced} jobs",
            LogLevel.success,
            {"provider": state.sheet_sync_status.provider, "row_id": state.sheet_sync_status.row_id},
        )


state_manager = WorkflowStateManager()
orchestrator = OrchestratorAgent(state_manager)
