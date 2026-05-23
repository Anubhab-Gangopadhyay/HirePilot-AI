from __future__ import annotations

import asyncio

from models.workflow_models import AgentStatus, JobApplicationResult, LogLevel, WorkflowState
from services.log_service import WorkflowLogService
from services.openai_service import OpenAIService, openai_service

try:
    from crewai import Agent
except Exception:  # pragma: no cover
    Agent = None


class SkillGapAgent:
    name = "skill_gap_agent"

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
            role="Skill Gap Analysis Agent",
            goal="Identify missing skills and concise learning actions for target jobs.",
            backstory="A practical career coach that surfaces only the highest-leverage gaps.",
            verbose=True,
            allow_delegation=False,
        )

    async def run(self, state: WorkflowState) -> WorkflowState:
        state.agent_status[self.name] = AgentStatus.running
        await self.logs.emit(state, "Skill Gap Agent", "Skill Gap Agent analyzing profile")

        if not state.selected_job:
            await self.logs.emit(state, "Skill Gap Agent", "No selected job available for skill comparison", LogLevel.warning)
            state.agent_status[self.name] = AgentStatus.failed
            return state

        await self.logs.emit(state, "Skill Gap Agent", "Skills extracted from resume")
        await self.logs.emit(state, "Skill Gap Agent", "Job description analyzed")

        analysis = await self.llm.analyze_skill_gap(
            state.uploaded_resume,
            state.selected_job,
            state.optimized_resume.optimized_resume,
        )
        state.skill_gap = analysis
        state.missing_skills = analysis.missing_skills
        state.intermediate_outputs["skill_gap_agent"] = analysis.model_dump()

        await self.logs.emit(
            state,
            "Skill Gap Agent",
            "Missing skills detected",
            LogLevel.success,
            {"missing_skills": analysis.missing_skills, "weak_areas": analysis.weak_areas},
        )
        await self.logs.emit(
            state,
            "Skill Gap Agent",
            "Recommendations generated",
            LogLevel.success,
            {"skill_match_percent": analysis.skill_match_percent},
        )
        state.agent_status[self.name] = AgentStatus.completed
        return state

    async def analyze_result(self, state: WorkflowState, result: JobApplicationResult) -> JobApplicationResult:
        await self.logs.emit(state, "Skill Gap Agent", f"Analyzing skill gap for {result.job.company}")
        analysis = await self.llm.analyze_skill_gap(
            state.uploaded_resume,
            result.job,
            result.resume.optimized_resume,
        )
        result.skill_gap = analysis
        await self.logs.emit(
            state,
            "Skill Gap Agent",
            f"{result.job.company}: skill match {analysis.skill_match_percent}%",
            LogLevel.success,
            {"missing_skills": analysis.missing_skills},
        )
        return result

    async def run_for_all_jobs(self, state: WorkflowState, concurrency: int = 4) -> WorkflowState:
        state.agent_status[self.name] = AgentStatus.running
        await self.logs.emit(state, "Skill Gap Agent", f"Analyzing employability gaps for {len(state.job_results)} jobs")

        semaphore = asyncio.Semaphore(concurrency)

        async def guarded(result: JobApplicationResult) -> JobApplicationResult:
            async with semaphore:
                return await self.analyze_result(state, result)

        state.job_results = await asyncio.gather(*(guarded(result) for result in state.job_results))
        if state.job_results:
            best = max(state.job_results, key=lambda item: (item.resume.ats_score + item.skill_gap.skill_match_percent) / 2)
            state.skill_gap = best.skill_gap
            state.missing_skills = best.skill_gap.missing_skills
            state.intermediate_outputs["skill_gap_agent"] = [item.skill_gap.model_dump() for item in state.job_results]

        await self.logs.emit(state, "Skill Gap Agent", "Recommendations generated for every job", LogLevel.success)
        state.agent_status[self.name] = AgentStatus.completed
        return state
