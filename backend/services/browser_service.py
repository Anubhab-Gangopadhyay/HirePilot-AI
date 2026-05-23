from __future__ import annotations

import os

from models.workflow_models import ApplicationPreparation, JobOpportunity

try:
    from playwright.async_api import async_playwright
except Exception:  # pragma: no cover
    async_playwright = None


class BrowserAutomationService:
    """Human-assisted application preparation. Never submits final applications."""

    async def prepare_application(
        self,
        job: JobOpportunity,
        optimized_resume: str,
        cover_letter: str,
        candidate: dict[str, str],
        application_url: str | None = None,
    ) -> ApplicationPreparation:
        url = application_url or job.url or "demo://human-assisted-application"
        fields = {
            "name": candidate.get("name", "HirePilot Candidate"),
            "email": candidate.get("email", "candidate@example.com"),
            "phone": candidate.get("phone", "+91 90000 00000"),
            "role": job.role,
            "company": job.company,
            "cover_letter": cover_letter[:1200],
        }
        steps = [
            "Application page opened",
            "Candidate profile fields detected",
            "Tailored resume attached to application packet",
            "Cover letter populated",
            "Waiting for human approval before final submit",
        ]

        if self._live_browser_enabled(url):
            browser_steps = await self._prepare_with_playwright(url, fields)
            steps = [*steps[:1], *browser_steps, *steps[-1:]]

        return ApplicationPreparation(
            status="prepared",
            prepared_count=1,
            notes=[
                f"Prepared application packet for {job.role} at {job.company}.",
                "Final submission is blocked until the user clicks Approve & Apply.",
                "Automation is positioned as human-assisted, not mass auto-apply.",
            ],
            approval_required=True,
            approval_state="waiting_for_human_review",
            application_url=url,
            autofilled_fields=fields,
            browser_steps=steps,
            ready_to_submit=False,
        )

    async def approve_application(self, preparation: ApplicationPreparation) -> ApplicationPreparation:
        if not preparation.approval_required:
            return preparation

        updated = preparation.model_copy(deep=True)
        updated.status = "approved"
        updated.approval_state = "approved_by_human"
        updated.ready_to_submit = True
        updated.notes = [
            *updated.notes,
            "Human approval received. Application marked ready for final submission.",
        ]
        updated.browser_steps = [
            *updated.browser_steps,
            "Approve & Apply clicked by user",
            "Final submit remains controlled by the job platform page",
        ]
        return updated

    def _live_browser_enabled(self, url: str) -> bool:
        return (
            async_playwright is not None
            and url.startswith(("http://", "https://"))
            and os.getenv("ENABLE_APPLICATION_BROWSER", "false").lower() in {"1", "true", "yes"}
        )

    async def _prepare_with_playwright(self, url: str, fields: dict[str, str]) -> list[str]:
        steps: list[str] = []
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            steps.append("Application page opened with Playwright")

            selectors = {
                "name": "input[name*='name' i], input[id*='name' i]",
                "email": "input[type='email'], input[name*='email' i]",
                "phone": "input[type='tel'], input[name*='phone' i]",
                "cover_letter": "textarea[name*='cover' i], textarea",
            }
            for field, selector in selectors.items():
                locator = page.locator(selector).first
                if await locator.count():
                    await locator.fill(fields[field])
                    steps.append(f"{field.replace('_', ' ').title()} field autofilled")

            await browser.close()
        return steps


browser_service = BrowserAutomationService()
