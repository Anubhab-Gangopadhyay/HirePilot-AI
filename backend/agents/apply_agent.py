from __future__ import annotations

import asyncio

from models.workflow_models import AgentStatus, ApplicationPreparation, JobApplicationResult, LogLevel, WorkflowState
from services.browser_service import BrowserAutomationService, browser_service
from services.log_service import WorkflowLogService

try:
    from crewai import Agent
except Exception:  # pragma: no cover
    Agent = None


class ApplyAgent:
    name = "apply_agent"

    def __init__(
        self,
        logs: WorkflowLogService,
        browser: BrowserAutomationService = browser_service,
    ) -> None:
        self.logs = logs
        self.browser = browser
        self.crewai_agent = self._build_crewai_agent()

    def _build_crewai_agent(self):
        if Agent is None:
            return None
        return Agent(
            role="Application Preparation Agent",
            goal="Prepare realistic application packets without submitting them automatically.",
            backstory="A careful application operations agent that keeps the human in control.",
            verbose=True,
            allow_delegation=False,
        )

    async def run(self, state: WorkflowState) -> WorkflowState:
        state.agent_status[self.name] = AgentStatus.running
        await self.logs.emit(state, "Apply Agent", "Apply Agent preparing application")
        await asyncio.sleep(0.25)

        job = state.selected_job or (state.jobs_found[0] if state.jobs_found else None)
        if not job:
            await self.logs.emit(state, "Apply Agent", "No job available for application preparation", LogLevel.warning)
            state.agent_status[self.name] = AgentStatus.failed
            return state

        preparation = await self.browser.prepare_application(
            job=job,
            optimized_resume=state.optimized_resume.optimized_resume,
            cover_letter=state.optimized_resume.cover_letter,
            candidate={
                "name": "HirePilot Candidate",
                "email": "candidate@example.com",
                "phone": "+91 90000 00000",
            },
        )
        state.application_status = preparation
        state.intermediate_outputs["apply_agent"] = state.application_status.model_dump()

        for step in preparation.browser_steps[:4]:
            await self.logs.emit(state, "Apply Agent", step, LogLevel.success)

        await self.logs.emit(
            state,
            "Apply Agent",
            "Waiting for human approval",
            LogLevel.success,
            {"approval_state": preparation.approval_state, "ready_to_submit": preparation.ready_to_submit},
        )
        state.agent_status[self.name] = AgentStatus.completed
        return state

    async def prepare_result(self, state: WorkflowState, result: JobApplicationResult) -> JobApplicationResult:
        preparation = await self.browser.prepare_application(
            job=result.job,
            optimized_resume=result.resume.optimized_resume,
            cover_letter=result.resume.cover_letter,
            candidate={
                "name": "HirePilot Candidate",
                "email": "candidate@example.com",
                "phone": "+91 90000 00000",
            },
            application_url=result.job.url,
        )
        result.application = preparation
        result.status = preparation.approval_state
        await self.logs.emit(
            state,
            "Apply Agent",
            f"Application waiting for approval: {result.job.company}",
            LogLevel.success,
            {"apply_link": result.job.url, "approval_state": preparation.approval_state},
        )
        return result

    async def run_for_all_jobs(self, state: WorkflowState, concurrency: int = 3) -> WorkflowState:
        state.agent_status[self.name] = AgentStatus.running
        await self.logs.emit(state, "Apply Agent", f"Preparing application packets for {len(state.job_results)} jobs")

        semaphore = asyncio.Semaphore(concurrency)

        async def guarded(result: JobApplicationResult) -> JobApplicationResult:
            async with semaphore:
                return await self.prepare_result(state, result)

        state.job_results = await asyncio.gather(*(guarded(result) for result in state.job_results))
        if state.job_results:
            best = max(state.job_results, key=lambda item: (item.resume.ats_score + item.skill_gap.skill_match_percent) / 2)
            state.application_status = best.application
            state.intermediate_outputs["apply_agent"] = [item.application.model_dump() for item in state.job_results]

        await self.logs.emit(state, "Apply Agent", "Applications prepared. Human approval required.", LogLevel.success)
        state.agent_status[self.name] = AgentStatus.completed
        return state
