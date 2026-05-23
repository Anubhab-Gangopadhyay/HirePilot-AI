from __future__ import annotations

import asyncio

from models.workflow_models import AgentStatus, JobApplicationResult, JobOpportunity, LogLevel, WorkflowState
from services.ats_service import ats_service
from services.log_service import WorkflowLogService
from services.openai_service import OpenAIService, openai_service

try:
    from crewai import Agent
except Exception:  # pragma: no cover
    Agent = None


class ResumeAgent:
    name = "resume_agent"

    def __init__(
        self,
        logs: WorkflowLogService,
        llm: OpenAIService = openai_service,
    ) -> None:
        self.logs = logs
        self.llm = llm
        self.crewai_agent = self._build_crewai_agent()

    def _build_crewai_agent(self):
        if Agent is None:
            return None
        return Agent(
            role="Resume Optimization Agent",
            goal="Tailor resumes for ATS compatibility and role relevance.",
            backstory="A senior resume strategist trained on recruiter-friendly, realistic resume improvements.",
            verbose=True,
            allow_delegation=False,
        )

    async def run(self, state: WorkflowState) -> WorkflowState:
        state.agent_status[self.name] = AgentStatus.running
        await self.logs.emit(state, "Resume Agent", "Resume Agent optimizing ATS keywords")

        if not state.selected_job:
            await self.logs.emit(state, "Resume Agent", "No selected job available for optimization", LogLevel.warning)
            state.agent_status[self.name] = AgentStatus.failed
            return state

        parsed = ats_service.parse_resume(state.uploaded_resume)
        await self.logs.emit(state, "Resume Agent", "Resume parsed", LogLevel.success, {
            "has_summary": bool(parsed["summary"]),
            "has_skills": bool(parsed["skills"]),
            "has_projects": bool(parsed["projects"]),
        })
        ats_analysis = ats_service.analyze(state.uploaded_resume, state.selected_job)
        await self.logs.emit(state, "Resume Agent", "ATS keywords extracted", LogLevel.success, {
            "keywords": ats_analysis["job_keywords"][:8],
            "missing_keywords": ats_analysis["missing_keywords"][:5],
        })

        optimization = await self.llm.optimize_resume(state.uploaded_resume, state.selected_job)
        state.optimized_resume = optimization
        state.ats_score = optimization.ats_score
        state.intermediate_outputs["resume_agent"] = optimization.model_dump()

        await self.logs.emit(
            state,
            "Resume Agent",
            f"Resume optimized for {state.selected_job.role} role",
            LogLevel.success,
            {"section_scores": optimization.section_scores},
        )
        await self.logs.emit(
            state,
            "Resume Agent",
            f"ATS score improved to {optimization.ats_score}%",
            LogLevel.success,
            {"missing_keywords": optimization.missing_keywords},
        )
        state.agent_status[self.name] = AgentStatus.completed
        return state

    async def tailor_job(self, state: WorkflowState, job: JobOpportunity) -> JobApplicationResult:
        await self.logs.emit(state, "Resume Agent", f"Tailoring resume for {job.company} - {job.role}")
        optimization = await self.llm.optimize_resume(state.uploaded_resume, job)
        await self.logs.emit(
            state,
            "Resume Agent",
            f"Tailored resume generated for {job.company}",
            LogLevel.success,
            {"ats_score": optimization.ats_score, "missing_keywords": optimization.missing_keywords},
        )
        return JobApplicationResult(job=job, resume=optimization)

    async def run_for_all_jobs(self, state: WorkflowState, concurrency: int = 4) -> WorkflowState:
        state.agent_status[self.name] = AgentStatus.running
        await self.logs.emit(state, "Resume Agent", f"Tailoring resumes for {len(state.jobs_found)} scraped jobs")

        semaphore = asyncio.Semaphore(concurrency)

        async def guarded(job: JobOpportunity) -> JobApplicationResult:
            async with semaphore:
                return await self.tailor_job(state, job)

        state.job_results = await asyncio.gather(*(guarded(job) for job in state.jobs_found))
        if state.job_results:
            best = max(state.job_results, key=lambda item: item.resume.ats_score)
            state.selected_job = best.job
            state.optimized_resume = best.resume
            state.ats_score = best.resume.ats_score
            state.intermediate_outputs["resume_agent"] = [item.resume.model_dump() for item in state.job_results]

        await self.logs.emit(
            state,
            "Resume Agent",
            f"{len(state.job_results)} tailored resume versions generated",
            LogLevel.success,
        )
        state.agent_status[self.name] = AgentStatus.completed
        return state
