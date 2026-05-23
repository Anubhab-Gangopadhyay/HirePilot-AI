from __future__ import annotations

import csv
import os
from datetime import datetime, timezone
from pathlib import Path

from models.workflow_models import JobApplicationResult, SheetSyncStatus, WorkflowState

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
except Exception:  # pragma: no cover - optional dependency
    Credentials = None
    build = None


SHEET_HEADERS = [
    "Timestamp",
    "Workflow ID",
    "Company",
    "Role",
    "Platform",
    "Location",
    "ATS Score",
    "Skill Match",
    "Resume Skills Parsed",
    "Required JD Skills",
    "Matched Skills",
    "Missing Skills",
    "Recommendations",
    "Status",
    "Apply Link",
]


class SheetsService:
    """Google Sheets tracker with local CSV fallback for stable demos."""

    def __init__(self) -> None:
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
        self.credentials_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.range_name = os.getenv("GOOGLE_SHEETS_RANGE", "HirePilot!A:O")
        self.local_path = Path(os.getenv("LOCAL_SHEETS_FALLBACK", "career_tracking.csv"))

    @property
    def google_enabled(self) -> bool:
        return bool(self.spreadsheet_id and self.credentials_file and Credentials and build)

    async def sync_result(self, state: WorkflowState, result: JobApplicationResult) -> SheetSyncStatus:
        row = self._result_to_row(state, result)
        if self.google_enabled:
            try:
                return self._append_google_row(row)
            except Exception as exc:
                return self._upsert_local_row(state, result, row, f"Google Sheets failed, local fallback used: {exc}")

        return self._upsert_local_row(state, result, row, "Google Sheets credentials not configured. Local tracking row updated.")

    def _append_google_row(self, row: list[str]) -> SheetSyncStatus:
        credentials = Credentials.from_service_account_file(
            self.credentials_file,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        service = build("sheets", "v4", credentials=credentials)
        response = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range=self.range_name,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [row]},
            )
            .execute()
        )
        return SheetSyncStatus(
            status="synced",
            provider="google_sheets",
            row_id=response.get("updates", {}).get("updatedRange"),
            message="Google Sheet updated",
            updated_at=datetime.now(timezone.utc),
        )

    def _upsert_local_row(self, state: WorkflowState, result: JobApplicationResult, row: list[str], message: str) -> SheetSyncStatus:
        rows: list[dict[str, str]] = []
        if self.local_path.exists():
            with self.local_path.open("r", newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

        row_dict = dict(zip(SHEET_HEADERS, row))
        row_key = self._row_key(state, result)
        updated = False
        for index, existing in enumerate(rows):
            if self._dict_row_key(existing) == row_key:
                rows[index] = row_dict
                updated = True
                break

        if not updated:
            rows.append(row_dict)

        with self.local_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(SHEET_HEADERS)
            for item in rows:
                writer.writerow([item.get(header, "") for header in SHEET_HEADERS])

        return SheetSyncStatus(
            status="synced",
            provider="local_csv",
            row_id=row_key,
            message=message,
            updated_at=datetime.now(timezone.utc),
        )

    def _row_key(self, state: WorkflowState, result: JobApplicationResult) -> str:
        return f"{state.workflow_id}:{result.job.company}:{result.job.role}:{result.job.url or result.job.source}"

    def _dict_row_key(self, row: dict[str, str]) -> str:
        return f"{row.get('Workflow ID', '')}:{row.get('Company', '')}:{row.get('Role', '')}:{row.get('Apply Link', '') or row.get('Platform', '')}"

    def _result_to_row(self, state: WorkflowState, result: JobApplicationResult) -> list[str]:
        return [
            datetime.now(timezone.utc).isoformat(),
            state.workflow_id,
            result.job.company,
            result.job.role,
            result.job.source,
            result.job.location,
            str(result.resume.ats_score),
            str(result.skill_gap.skill_match_percent),
            ", ".join(result.skill_gap.resume_skills),
            ", ".join(result.skill_gap.required_skills or result.skill_gap.job_skills),
            ", ".join(result.skill_gap.matched_skills),
            ", ".join(result.skill_gap.missing_skills),
            " | ".join(result.skill_gap.recommendations),
            result.application.approval_state,
            result.job.url or "",
        ]


sheets_service = SheetsService()
