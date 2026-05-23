from __future__ import annotations

import re

from models.workflow_models import JobOpportunity, SkillGapAnalysis
from services.ats_service import TECH_KEYWORDS
from utils.helpers import clamp


class SkillAnalysisService:
    SKILL_ALIASES = {
        "APIs": ["api", "apis", "api development", "api design"],
        "Node.js": ["node", "nodejs", "node.js"],
        "JavaScript": ["javascript", "js"],
        "TypeScript": ["typescript", "ts"],
        "PostgreSQL": ["postgresql", "postgres"],
        "MongoDB": ["mongodb", "mongo"],
        "REST": ["rest", "restful"],
        "GraphQL": ["graphql", "graph ql"],
        "Microservices": ["microservices", "micro services", "distributed services"],
        "CI/CD": ["ci/cd", "cicd", "continuous integration", "continuous delivery"],
        "AWS": ["aws", "amazon web services"],
        "Azure": ["azure", "microsoft azure"],
        "GCP": ["gcp", "google cloud"],
        "Authentication": ["authentication", "auth", "oauth", "jwt"],
        "Testing": ["testing", "tests", "test automation"],
        "Unit Testing": ["unit testing", "unit tests"],
        "Integration Testing": ["integration testing", "integration tests"],
        "System Design": ["system design", "architecture", "scalable systems"],
        "Data Structures": ["data structures", "dsa"],
        "Algorithms": ["algorithms", "dsa"],
        "GitHub Actions": ["github actions"],
        "Spring Boot": ["spring boot", "springboot"],
    }
    REQUIRED_MARKERS = (
        "required", "requirements", "must have", "must-have", "mandatory", "you have",
        "you will need", "looking for", "responsibilities", "qualifications", "experience with",
    )
    PREFERRED_MARKERS = (
        "preferred", "nice to have", "good to have", "bonus", "plus", "advantage",
        "familiarity", "exposure to",
    )

    def extract_skills(self, text: str, seed_skills: list[str] | None = None) -> list[str]:
        haystack = f"{text} {' '.join(seed_skills or [])}".lower()
        skills: list[str] = []
        for skill in self._skill_catalog(seed_skills):
            if self._contains_skill(haystack, skill):
                skills.append(skill)

        for seed in seed_skills or []:
            canonical = self._canonical_skill(seed)
            if canonical and not any(canonical.lower() == skill.lower() for skill in skills):
                skills.append(canonical)

        return list(dict.fromkeys(skills))

    def extract_resume_skills(self, resume_text: str) -> list[str]:
        return self.extract_skills(resume_text)

    def extract_job_skill_requirements(self, job: JobOpportunity) -> dict[str, list[str]]:
        description = job.description or ""
        seeded = self.extract_skills(description, job.skills)
        sentences = self._split_sentences(description)
        required: list[str] = []
        preferred: list[str] = []

        for sentence in sentences:
            sentence_lower = sentence.lower()
            sentence_skills = self.extract_skills(sentence)
            if not sentence_skills:
                continue

            if any(marker in sentence_lower for marker in self.PREFERRED_MARKERS):
                preferred.extend(sentence_skills)
            elif any(marker in sentence_lower for marker in self.REQUIRED_MARKERS):
                required.extend(sentence_skills)

        if not required:
            # Job board descriptions are often unstructured; seeded skills are the safest required proxy.
            required = seeded

        preferred = [skill for skill in preferred if skill not in required]
        all_job_skills = list(dict.fromkeys([*required, *preferred, *seeded]))
        return {
            "required_skills": list(dict.fromkeys(required)),
            "preferred_skills": list(dict.fromkeys(preferred)),
            "job_skills": all_job_skills,
        }

    def analyze(self, resume_text: str, optimized_resume: str, job: JobOpportunity) -> SkillGapAnalysis:
        # Critical: detect gaps against the original candidate resume.
        # The optimized resume may already include missing keywords, so using it here would hide real gaps.
        resume_skills = self.extract_resume_skills(resume_text)
        job_requirements = self.extract_job_skill_requirements(job)
        job_skills = job_requirements["job_skills"]
        required_skills = job_requirements["required_skills"]
        preferred_skills = job_requirements["preferred_skills"]
        resume_set = {skill.lower() for skill in resume_skills}
        matched = [skill for skill in job_skills if skill.lower() in resume_set]
        missing_required = [skill for skill in required_skills if skill.lower() not in resume_set]
        missing_preferred = [skill for skill in preferred_skills if skill.lower() not in resume_set]
        missing = list(dict.fromkeys([*missing_required, *missing_preferred]))
        required_match = len(required_skills) - len(missing_required)
        preferred_match = len(preferred_skills) - len(missing_preferred)
        if preferred_skills:
            skill_match = clamp(round(((required_match / max(len(required_skills), 1)) * 0.8 + (preferred_match / len(preferred_skills)) * 0.2) * 100))
        else:
            skill_match = clamp(round((required_match / max(len(required_skills), 1)) * 100))
        visible_missing = missing[:8]

        return SkillGapAnalysis(
            missing_skills=visible_missing,
            weak_areas=self._weak_areas(visible_missing),
            recommendations=self._recommendations(visible_missing, job.role),
            project_suggestions=self._projects(visible_missing, job.role),
            learning_roadmap=self._roadmap(visible_missing),
            market_demand=self._market_demand(job_skills),
            resume_skills=resume_skills,
            job_skills=job_skills,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            matched_skills=matched,
            skill_match_percent=skill_match,
        )

    def _skill_catalog(self, seed_skills: list[str] | None = None) -> list[str]:
        return list(dict.fromkeys([*TECH_KEYWORDS, *(self._canonical_skill(skill) for skill in seed_skills or [] if skill)]))

    def _canonical_skill(self, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            return ""
        for skill in TECH_KEYWORDS:
            aliases = self.SKILL_ALIASES.get(skill, [skill.lower()])
            if cleaned.lower() == skill.lower() or cleaned.lower() in [alias.lower() for alias in aliases]:
                return skill
        return cleaned

    def _contains_skill(self, haystack: str, skill: str) -> bool:
        aliases = self.SKILL_ALIASES.get(skill, [skill.lower()])
        for alias in aliases:
            escaped = re.escape(alias.lower())
            pattern = rf"(?<![a-z0-9+#.]){escaped}(?![a-z0-9+#.])"
            if re.search(pattern, haystack):
                return True
        return False

    def _split_sentences(self, text: str) -> list[str]:
        chunks = re.split(r"[\n\r•\u2022]|(?<=[.!?])\s+", text)
        return [chunk.strip() for chunk in chunks if len(chunk.strip()) > 12]

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
