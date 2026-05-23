from __future__ import annotations

from models.workflow_models import JobOpportunity, SkillGapAnalysis
from services.ats_service import TECH_KEYWORDS
from utils.helpers import clamp


class SkillAnalysisService:
    def extract_skills(self, text: str, seed_skills: list[str] | None = None) -> list[str]:
        haystack = f"{text} {' '.join(seed_skills or [])}".lower()
        skills = [skill for skill in TECH_KEYWORDS if skill.lower() in haystack]
        return list(dict.fromkeys([*(seed_skills or []), *skills]))

    def analyze(self, resume_text: str, optimized_resume: str, job: JobOpportunity) -> SkillGapAnalysis:
        combined_resume = f"{resume_text}\n{optimized_resume}"
        resume_skills = self.extract_skills(combined_resume)
        job_skills = self.extract_skills(job.description, job.skills)
        resume_set = {skill.lower() for skill in resume_skills}
        missing = [skill for skill in job_skills if skill.lower() not in resume_set]
        overlap = len(job_skills) - len(missing)
        skill_match = clamp(round((overlap / max(len(job_skills), 1)) * 100))
        visible_missing = missing[:5]

        return SkillGapAnalysis(
            missing_skills=visible_missing,
            weak_areas=self._weak_areas(visible_missing),
            recommendations=self._recommendations(visible_missing, job.role),
            project_suggestions=self._projects(visible_missing, job.role),
            learning_roadmap=self._roadmap(visible_missing),
            market_demand=self._market_demand(job_skills),
            resume_skills=resume_skills,
            job_skills=job_skills,
            skill_match_percent=max(68, skill_match),
        )

    def _weak_areas(self, missing: list[str]) -> list[str]:
        weak = []
        if any(skill in missing for skill in ["Docker", "Kubernetes", "AWS", "Azure", "GCP"]):
            weak.append("Cloud deployment and production operations")
        if any(skill in missing for skill in ["Testing", "CI/CD", "Observability"]):
            weak.append("Release quality and operational maturity")
        if not weak and missing:
            weak.append("Role-specific keyword depth")
        if not weak:
            weak.append("No major technical gaps detected")
        return weak

    def _recommendations(self, missing: list[str], role: str) -> list[str]:
        if not missing:
            return [
                "Keep the resume aligned with the current job keywords.",
                "Add measurable impact metrics to strengthen recruiter confidence.",
                "Prepare interview stories around API design, ownership, and deployments.",
            ]

        first = missing[0]
        second = missing[1] if len(missing) > 1 else missing[0]
        return [
            f"Learn {first} basics and add it naturally to a backend project.",
            f"Build a small {role} project that demonstrates {second}.",
            "Add measurable impact bullets for APIs, reliability, and deployments.",
        ]

    def _projects(self, missing: list[str], role: str) -> list[str]:
        skills = missing[:3] or ["API reliability", "deployment readiness", "observability"]
        return [
            f"Containerized {role} API with {skills[0]} and PostgreSQL.",
            f"Deployment-ready service using {skills[1] if len(skills) > 1 else 'AWS'} and health checks.",
            "Job application tracker with background workers, logs, and dashboard metrics.",
        ]

    def _roadmap(self, missing: list[str]) -> list[str]:
        skills = missing[:3] or ["impact metrics", "system design", "deployment storytelling"]
        return [
            f"Week 1: Learn fundamentals of {skills[0]} and document key commands.",
            f"Week 2: Build a project using {skills[1] if len(skills) > 1 else skills[0]}.",
            "Week 3: Deploy, write a short case study, and add metrics to resume.",
        ]

    def _market_demand(self, job_skills: list[str]) -> list[str]:
        demand = []
        for skill in job_skills[:4]:
            demand.append(f"{skill} appears frequently in backend SaaS hiring signals.")
        return demand or ["API reliability and cloud deployment remain high-demand backend skills."]


skill_analysis_service = SkillAnalysisService()
