from __future__ import annotations

import asyncio
import os
from urllib.parse import quote_plus, urljoin, urlparse

from bs4 import BeautifulSoup

from models.workflow_models import JobOpportunity
from utils.helpers import normalize_text

try:
    from playwright.async_api import async_playwright
except Exception:  # pragma: no cover - optional dependency in local demos
    async_playwright = None


class ScraperService:
    """Demo-safe scraper for 5-10 jobs with robust mock fallback."""

    def __init__(self) -> None:
        self.last_diagnostics: list[str] = []

    async def search_jobs(
        self,
        role: str,
        location: str,
        remote_preference: bool = True,
        limit: int = 8,
    ) -> list[JobOpportunity]:
        self.last_diagnostics = []
        if os.getenv("ENABLE_LIVE_SCRAPING", "true").lower() in {"0", "false", "no"}:
            self.last_diagnostics.append("Live scraping disabled by ENABLE_LIVE_SCRAPING.")
            return self.mock_jobs(role, location, remote_preference)[:limit]

        per_source_limit = max(4, min(8, (limit // 3) + 2))
        search_terms = self._search_terms(role)
        scraping_tasks = []
        for search_role in search_terms:
            scraping_tasks.extend([
                self._scrape_indeed(search_role, location, limit=per_source_limit),
                self._scrape_naukri(search_role, location, limit=per_source_limit),
                self._scrape_linkedin_public(search_role, location, limit=per_source_limit),
            ])
        results = await asyncio.gather(*scraping_tasks, return_exceptions=True)

        jobs: list[JobOpportunity] = []
        source_names = ["Indeed", "Naukri", "LinkedIn"]
        for result in results:
            if isinstance(result, list):
                jobs.extend(result)
            elif isinstance(result, Exception):
                self.last_diagnostics.append(f"{type(result).__name__}: {result}")

        for source_name in source_names:
            count = len([job for job in jobs if job.source == source_name])
            if count == 0:
                self.last_diagnostics.append(f"{source_name}: no extractable jobs returned, likely blocked or client-rendered.")

        filtered = self._dedupe_jobs(self._filter_jobs(jobs, role, location, remote_preference))
        if len(filtered) >= limit:
            return filtered[:limit]

        if filtered:
            self.last_diagnostics.append(f"Live scraping returned {len(filtered)} relevant jobs; demo fallback topped up to {limit}.")
            return self._dedupe_jobs([*filtered, *self.mock_jobs(role, location, remote_preference)])[:limit]

        if not jobs:
            self.last_diagnostics.append("No live job cards were parsed from LinkedIn, Naukri, or Indeed.")
        else:
            self.last_diagnostics.append("Live jobs were parsed but filtered out by role/location matching.")
        return self.mock_jobs(role, location, remote_preference)[:limit]

    def _search_terms(self, role: str) -> list[str]:
        terms = [role]
        lowered = role.lower()
        if "backend" in lowered:
            terms.extend(["Backend Engineer", "Node.js Developer", "Software Engineer Backend"])
        elif "developer" in lowered:
            terms.extend(["Software Engineer", "Full Stack Developer"])
        return list(dict.fromkeys(terms))

    async def _scrape_indeed(self, role: str, location: str, limit: int) -> list[JobOpportunity]:
        url = f"https://in.indeed.com/jobs?q={quote_plus(role)}&l={quote_plus(location)}"
        html = await self._fetch_page(url)
        soup = BeautifulSoup(html, "html.parser")
        jobs: list[JobOpportunity] = []

        for card in soup.select("[data-testid='slider_item'], .job_seen_beacon")[:limit]:
            title = normalize_text(card.select_one("h2, .jobTitle").get_text(" ")) if card.select_one("h2, .jobTitle") else role
            company = normalize_text(card.select_one("[data-testid='company-name'], .companyName").get_text(" ")) if card.select_one("[data-testid='company-name'], .companyName") else "Indeed Company"
            job_location = normalize_text(card.select_one("[data-testid='text-location'], .companyLocation").get_text(" ")) if card.select_one("[data-testid='text-location'], .companyLocation") else location
            detail_url = self._extract_link(card, "https://in.indeed.com")
            description = await self._read_job_description(detail_url, card, "Indeed")
            jobs.append(self._build_job(title, company, job_location, description, "Indeed", detail_url))

        return jobs

    async def _scrape_naukri(self, role: str, location: str, limit: int) -> list[JobOpportunity]:
        slug_role = quote_plus(role).replace("+", "-").lower()
        slug_location = quote_plus(location).replace("+", "-").lower()
        url = f"https://www.naukri.com/{slug_role}-jobs-in-{slug_location}"
        html = await self._fetch_page(url)
        soup = BeautifulSoup(html, "html.parser")
        jobs: list[JobOpportunity] = []

        for card in soup.select(".srp-jobtuple-wrapper, article.jobTuple")[:limit]:
            title = normalize_text(card.select_one("a.title, .title").get_text(" ")) if card.select_one("a.title, .title") else role
            company = normalize_text(card.select_one(".comp-name, .companyInfo").get_text(" ")) if card.select_one(".comp-name, .companyInfo") else "Naukri Company"
            job_location = normalize_text(card.select_one(".locWdth, .location").get_text(" ")) if card.select_one(".locWdth, .location") else location
            detail_url = self._extract_link(card, "https://www.naukri.com")
            description = await self._read_job_description(detail_url, card, "Naukri")
            jobs.append(self._build_job(title, company, job_location, description, "Naukri", detail_url))

        return jobs

    async def _scrape_linkedin_public(self, role: str, location: str, limit: int) -> list[JobOpportunity]:
        url = f"https://www.linkedin.com/jobs/search?keywords={quote_plus(role)}&location={quote_plus(location)}"
        html = await self._fetch_page(url)
        soup = BeautifulSoup(html, "html.parser")
        jobs: list[JobOpportunity] = []

        for card in soup.select(".base-card, .jobs-search__results-list li")[:limit]:
            title = normalize_text(card.select_one(".base-search-card__title, h3").get_text(" ")) if card.select_one(".base-search-card__title, h3") else role
            company = normalize_text(card.select_one(".base-search-card__subtitle, h4").get_text(" ")) if card.select_one(".base-search-card__subtitle, h4") else "LinkedIn Company"
            job_location = normalize_text(card.select_one(".job-search-card__location").get_text(" ")) if card.select_one(".job-search-card__location") else location
            detail_url = self._extract_link(card, "https://www.linkedin.com")
            description = await self._read_job_description(detail_url, card, "LinkedIn")
            jobs.append(self._build_job(title, company, job_location, description, "LinkedIn", detail_url))

        return jobs

    async def _fetch_page(self, url: str) -> str:
        if async_playwright is None:
            raise RuntimeError("Playwright is not installed")

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page(user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
            ))
            await page.goto(url, wait_until="domcontentloaded", timeout=18000)
            try:
                await page.wait_for_load_state("networkidle", timeout=6000)
            except Exception:
                pass
            await page.wait_for_timeout(2800)
            html = await page.content()
            await browser.close()
            return html

    async def _read_job_description(self, url: str | None, card, source: str) -> str:
        card_text = normalize_text(card.get_text(" "))
        if not url:
            return card_text[:1600]

        try:
            html = await self._fetch_page(url)
            soup = BeautifulSoup(html, "html.parser")
            selectors = {
                "Indeed": "#jobDescriptionText, [data-testid='jobsearch-JobComponent-description'], .jobsearch-jobDescriptionText",
                "Naukri": ".styles_JDC__dang-inner-html__h0K4t, .dang-inner-html, .job-desc, section",
                "LinkedIn": ".show-more-less-html__markup, .description__text, .jobs-description-content__text",
            }
            node = soup.select_one(selectors.get(source, "main, body"))
            detail_text = normalize_text(node.get_text(" ")) if node else ""
            return (detail_text or card_text)[:4000]
        except Exception:
            return card_text[:1600]

    def _filter_jobs(
        self,
        jobs: list[JobOpportunity],
        role: str,
        location: str,
        remote_preference: bool,
    ) -> list[JobOpportunity]:
        filtered: list[JobOpportunity] = []
        role_terms = {term.lower() for term in role.split() if len(term) > 2}

        for job in jobs:
            haystack = f"{job.role} {job.description}".lower()
            if not any(term in haystack for term in role_terms):
                continue
            if not remote_preference and location.lower() not in job.location.lower():
                continue
            filtered.append(job)

        return sorted(filtered, key=lambda job: job.match_score, reverse=True)

    def _dedupe_jobs(self, jobs: list[JobOpportunity]) -> list[JobOpportunity]:
        seen: set[str] = set()
        unique: list[JobOpportunity] = []
        for job in jobs:
            key = self._dedupe_key(job)
            if key in seen:
                continue
            seen.add(key)
            unique.append(job)
        return unique

    def _dedupe_key(self, job: JobOpportunity) -> str:
        if job.url:
            parsed = urlparse(job.url)
            normalized_path = parsed.path.rstrip("/")
            return f"{job.source}:{parsed.netloc}:{normalized_path}:{job.company.lower()}:{job.role.lower()}"
        return f"{job.source}:{job.company.lower()}:{job.role.lower()}:{job.location.lower()}"

    def _extract_link(self, card, base_url: str) -> str | None:
        anchor = card.select_one("a[href]")
        if not anchor:
            return None
        href = anchor.get("href")
        return urljoin(base_url, href)

    def _build_job(self, role: str, company: str, location: str, description: str, source: str, url: str | None = None) -> JobOpportunity:
        skills = self._extract_skills(description)
        return JobOpportunity(
            role=role or "Backend Developer",
            company=company or "Hiring Company",
            location=location or "Bangalore",
            description=description or "Backend engineering role focused on APIs, services, and production systems.",
            skills=skills,
            source=source,
            match_score=min(94, 72 + len(skills) * 3),
            url=url,
        )

    def _extract_skills(self, text: str) -> list[str]:
        known = [
            "Python", "FastAPI", "Node.js", "React", "Docker", "Kubernetes", "AWS",
            "PostgreSQL", "MongoDB", "REST", "GraphQL", "Redis", "Microservices",
            "CI/CD", "TypeScript", "SQL",
        ]
        lowered = text.lower()
        found = [skill for skill in known if skill.lower() in lowered]
        return found or ["Node.js", "REST", "SQL", "Docker"]

    def mock_jobs(self, role: str, location: str, remote_preference: bool) -> list[JobOpportunity]:
        location_label = "Remote" if remote_preference else location
        return [
            JobOpportunity(
                role=role,
                company="ABC Tech",
                location=location,
                description="Build high-throughput backend APIs, own database models, improve deployment reliability, and collaborate with product engineering teams.",
                skills=["Node.js", "Docker", "PostgreSQL", "REST", "AWS"],
                source="Mock",
                match_score=91,
                url="https://www.linkedin.com/jobs/search/",
            ),
            JobOpportunity(
                role="Node.js Engineer",
                company="Cloudlane",
                location=location_label,
                description="Work on distributed services, event-driven workflows, observability, CI/CD, and cloud deployments for a growing SaaS platform.",
                skills=["Node.js", "Redis", "Kubernetes", "AWS", "CI/CD"],
                source="Mock",
                match_score=88,
                url="https://www.naukri.com/backend-developer-jobs",
            ),
            JobOpportunity(
                role="API Platform Engineer",
                company="NovaStack",
                location=location,
                description="Design REST APIs, improve SQL query performance, build internal tooling, and support production service ownership.",
                skills=["REST", "SQL", "Docker", "Microservices", "TypeScript"],
                source="Mock",
                match_score=84,
                url="https://in.indeed.com/jobs?q=backend+developer",
            ),
            JobOpportunity(
                role="Backend Software Engineer",
                company="FinGrid",
                location=location_label,
                description="Create secure backend services, payment workflow integrations, automated tests, and cloud-ready deployment pipelines.",
                skills=["Python", "FastAPI", "PostgreSQL", "AWS", "CI/CD"],
                source="Mock",
                match_score=82,
            ),
        ]


scraper_service = ScraperService()
