from __future__ import annotations

import os
from typing import Any

from models.workflow_models import JobOpportunity, ResumeOptimization, SkillGapAnalysis
from prompts.resume_prompts import RESUME_OPTIMIZATION_HUMAN_PROMPT, RESUME_OPTIMIZATION_SYSTEM_PROMPT
from prompts.skill_gap_prompts import SKILL_GAP_HUMAN_PROMPT, SKILL_GAP_SYSTEM_PROMPT
from services.ats_service import ats_service
from services.skill_analysis_service import skill_analysis_service

try:
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI
except Exception:  # pragma: no cover - optional hackathon dependency
    ChatOpenAI = None
    ChatPromptTemplate = None
    JsonOutputParser = None


class OpenAIService:
    """Small LangChain wrapper with deterministic fallback for stable demos."""

    def __init__(self) -> None:
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.api_key = os.getenv("OPENAI_API_KEY")

    @property
    def enabled(self) -> bool:
        return bool(self.api_key and ChatOpenAI and ChatPromptTemplate and JsonOutputParser)

    async def optimize_resume(self, resume_text: str, job: JobOpportunity) -> ResumeOptimization:
        if self.enabled:
            try:
                return await self._optimize_resume_with_llm(resume_text, job)
            except Exception:
                return self._fallback_resume_optimization(resume_text, job)

        return self._fallback_resume_optimization(resume_text, job)

    async def analyze_skill_gap(
        self,
        resume_text: str,
        job: JobOpportunity,
        optimized_resume: str = "",
    ) -> SkillGapAnalysis:
        if self.enabled:
            try:
                return await self._analyze_skill_gap_with_llm(resume_text, job, optimized_resume)
            except Exception:
                return self._fallback_skill_gap(resume_text, job, optimized_resume)

        return self._fallback_skill_gap(resume_text, job, optimized_resume)

    async def _optimize_resume_with_llm(self, resume_text: str, job: JobOpportunity) -> ResumeOptimization:
        parser = JsonOutputParser()
        prompt = ChatPromptTemplate.from_messages([
            ("system", RESUME_OPTIMIZATION_SYSTEM_PROMPT),
            ("human", RESUME_OPTIMIZATION_HUMAN_PROMPT),
        ])
        llm = ChatOpenAI(model=self.model_name, temperature=0.2)
        chain = prompt | llm | parser
        result: dict[str, Any] = await chain.ainvoke({
            "resume": resume_text,
            "job": job.model_dump_json(indent=2),
        })
        fallback = ats_service.build_optimized_resume(resume_text, job, ats_service.analyze(resume_text, job))
        return fallback.model_copy(update=result)

    async def _analyze_skill_gap_with_llm(
        self,
        resume_text: str,
        job: JobOpportunity,
        optimized_resume: str = "",
    ) -> SkillGapAnalysis:
        parser = JsonOutputParser()
        prompt = ChatPromptTemplate.from_messages([
            ("system", SKILL_GAP_SYSTEM_PROMPT),
            ("human", SKILL_GAP_HUMAN_PROMPT),
        ])
        llm = ChatOpenAI(model=self.model_name, temperature=0.15)
        chain = prompt | llm | parser
        result: dict[str, Any] = await chain.ainvoke({
            "resume": resume_text,
            "optimized_resume": optimized_resume,
            "job": job.model_dump_json(indent=2),
        })
        fallback = skill_analysis_service.analyze(resume_text, optimized_resume, job)
        return fallback.model_copy(update=result)

    def _fallback_resume_optimization(self, resume_text: str, job: JobOpportunity) -> ResumeOptimization:
        analysis = ats_service.analyze(resume_text, job)
        return ats_service.build_optimized_resume(resume_text, job, analysis)

    def _fallback_skill_gap(
        self,
        resume_text: str,
        job: JobOpportunity,
        optimized_resume: str = "",
    ) -> SkillGapAnalysis:
        return skill_analysis_service.analyze(resume_text, optimized_resume, job)


openai_service = OpenAIService()
