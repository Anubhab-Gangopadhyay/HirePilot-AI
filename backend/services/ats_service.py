from __future__ import annotations

import re
from collections import Counter

from models.workflow_models import JobOpportunity, ResumeOptimization
from utils.helpers import clamp, normalize_text


TECH_KEYWORDS = [
    "Python", "FastAPI", "Node.js", "JavaScript", "TypeScript", "React", "Docker",
    "Kubernetes", "AWS", "Azure", "GCP", "PostgreSQL", "MongoDB", "Redis", "SQL",
    "REST", "GraphQL", "Microservices", "CI/CD", "Git", "Playwright", "LangChain",
    "CrewAI", "OpenAI", "LLM", "APIs", "Authentication", "Testing", "Observability",
]


class ATSService:
    def parse_resume(self, resume_text: str) -> dict[str, str]:
        text = normalize_text(resume_text)
        return {
            "raw": text,
            "summary": self._section_after(text, ["summary", "profile", "objective"]),
            "skills": self._section_after(text, ["skills", "technical skills"]),
            "projects": self._section_after(text, ["projects", "experience"]),
        }

    def extract_keywords(self, text: str, job: JobOpportunity | None = None) -> list[str]:
        haystack = f"{text} {' '.join(job.skills) if job else ''}"
        found = [keyword for keyword in TECH_KEYWORDS if keyword.lower() in haystack.lower()]

        tokens = re.findall(r"\b[A-Za-z][A-Za-z0-9.+#/-]{2,}\b", haystack)
        common = [
            word for word, _ in Counter(tokens).most_common(30)
            if word.lower() not in {"and", "the", "for", "with", "role", "work", "team"}
        ]
        return list(dict.fromkeys([*found, *common]))[:24]

    def analyze(self, resume_text: str, job: JobOpportunity) -> dict:
        parsed = self.parse_resume(resume_text)
        job_keywords = self.extract_keywords(job.description, job)
        resume_keywords = self.extract_keywords(resume_text)
        resume_lower = resume_text.lower()
        matched = [keyword for keyword in job_keywords if keyword.lower() in resume_lower]
        missing = [keyword for keyword in job_keywords if keyword.lower() not in resume_lower]

        keyword_score = round((len(matched) / max(len(job_keywords), 1)) * 100)
        section_scores = {
            "summary": 82 if parsed["summary"] else 58,
            "skills": clamp(55 + len(set(resume_keywords) & set(job_keywords)) * 6),
            "projects": 84 if any(term in parsed["projects"].lower() for term in ["api", "project", "service", "deploy"]) else 62,
            "metrics": 78 if re.search(r"\d+%|\d+x|\d+\+", resume_text) else 52,
        }
        relevance_score = clamp(round(keyword_score * 0.55 + sum(section_scores.values()) / len(section_scores) * 0.45))
        ats_score = clamp(max(68, relevance_score + 6))

        return {
            "job_keywords": job_keywords,
            "resume_keywords": resume_keywords,
            "matched_keywords": matched,
            "missing_keywords": missing[:8],
            "section_scores": section_scores,
            "relevance_score": relevance_score,
            "ats_score": ats_score,
        }

    def build_optimized_resume(self, resume_text: str, job: JobOpportunity, analysis: dict) -> ResumeOptimization:
        missing = analysis["missing_keywords"][:5]
        matched = analysis["matched_keywords"][:8]
        improved_summary = (
            f"Backend engineer aligned to {job.role} roles, with experience building reliable APIs, "
            f"database-backed services, and production-oriented engineering workflows."
        )
        tailored_projects = [
            f"Reframed backend project work around {skill} and measurable service ownership."
            for skill in (missing[:2] or job.skills[:2] or ["API reliability"])
        ]
        optimized_resume = (
            f"{normalize_text(resume_text)}\n\n"
            f"Improved Summary: {improved_summary}\n\n"
            f"ATS Keyword Alignment: {', '.join(list(dict.fromkeys([*matched, *missing]))[:10])}\n\n"
            f"Tailored Projects:\n- " + "\n- ".join(tailored_projects)
        )
        cover_letter = (
            f"Dear {job.company} team,\n\n"
            f"I am excited to apply for the {job.role} role in {job.location}. My backend experience "
            f"aligns with your needs around {', '.join(job.skills[:3] or matched[:3] or ['API development'])}. "
            "I would bring a practical engineering mindset, ownership, and strong execution to the team.\n\n"
            "Regards,\nHirePilot Candidate"
        )
        inserted_keyword_count = len(missing)
        tailored_ats_score = clamp(max(78, analysis["ats_score"] + inserted_keyword_count * 4 + len(matched)))
        tailored_relevance = clamp(max(analysis["relevance_score"], tailored_ats_score - 5))

        return ResumeOptimization(
            optimized_resume=optimized_resume,
            ats_score=tailored_ats_score,
            missing_keywords=missing,
            improved_summary=improved_summary,
            tailored_projects=tailored_projects,
            cover_letter=cover_letter,
            extracted_keywords=analysis["job_keywords"],
            matched_keywords=matched,
            section_scores=analysis["section_scores"],
            relevance_score=tailored_relevance,
        )

    def _section_after(self, text: str, labels: list[str]) -> str:
        lower = text.lower()
        for label in labels:
            index = lower.find(label)
            if index >= 0:
                return text[index:index + 900]
        return ""


ats_service = ATSService()
