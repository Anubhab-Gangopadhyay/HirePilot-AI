from __future__ import annotations

from models.workflow_models import AgentStatus, LogLevel, WorkflowState
from services.log_service import WorkflowLogService
from services.scraper_service import ScraperService, scraper_service

try:
    from crewai import Agent
except Exception:  # pragma: no cover - optional dependency
    Agent = None


class JobAgent:
    name = "job_agent"

    def __init__(
        self,
        logs: WorkflowLogService,
        scraper: ScraperService = scraper_service,
    ) -> None:
        self.logs = logs
        self.scraper = scraper
        self.crewai_agent = self._build_crewai_agent()

    def _build_crewai_agent(self):
        if Agent is None:
            return None
        return Agent(
            role="Job Discovery Agent",
            goal="Find high-fit job opportunities for the candidate profile.",
            backstory="A pragmatic sourcing specialist that searches only enough roles for a stable demo.",
            verbose=True,
            allow_delegation=False,
        )

    async def run(self, state: WorkflowState) -> WorkflowState:
        state.agent_status[self.name] = AgentStatus.running
        await self.logs.emit(state, "Job Agent", "Job Agent activated")
        await self.logs.emit(
            state,
            "Job Agent",
            f"Searching LinkedIn, Naukri, and Indeed for {state.preferred_role} roles",
        )

        jobs = await self.scraper.search_jobs(
            state.preferred_role,
            state.preferred_location,
            state.remote_preference,
            limit=10,
        )
        state.jobs_found = jobs
        state.selected_job = jobs[0] if jobs else None
        state.intermediate_outputs["job_agent"] = [job.model_dump() for job in jobs]

        scraped_sources = sorted({job.source for job in jobs})
        real_jobs = [job for job in jobs if job.source != "Mock" and job.url]
        if self.scraper.last_diagnostics:
            await self.logs.emit(
                state,
                "Job Agent",
                "Live scraping diagnostics captured",
                LogLevel.warning,
                {"diagnostics": self.scraper.last_diagnostics[:5]},
            )
        await self.logs.emit(
            state,
            "Job Agent",
            f"Read {len(real_jobs)} live job descriptions from {', '.join(scraped_sources) or 'fallback sources'}",
            LogLevel.success if real_jobs else LogLevel.warning,
            {"sources": scraped_sources, "live_job_urls": [job.url for job in real_jobs[:5]]},
        )

        await self.logs.emit(
            state,
            "Job Agent",
            f"{len(jobs)} matching jobs prepared",
            LogLevel.success,
            {"top_company": state.selected_job.company if state.selected_job else None},
        )
        state.agent_status[self.name] = AgentStatus.completed
        return state
