# HirePilot AI Backend

Phase 2 backend for the autonomous multi-agent job application copilot.

## Run

Use Python 3.11 or 3.12 for the full CrewAI stack.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m playwright install chromium
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Set `OPENAI_API_KEY` to enable GPT-4o. Without it, the backend uses deterministic fallback outputs so the demo still works.

Live scraping is opt-in for demo stability:

```bash
set ENABLE_LIVE_SCRAPING=true
```

When it is not enabled, the Job Agent returns realistic mock opportunities instantly.

## Core Endpoints

- `POST /api/workflows/upload-resume`
- `POST /api/workflows/start`
- `POST /api/workflows/run-sync`
- `GET /api/workflows/{workflow_id}`
- `GET /api/workflows/{workflow_id}/logs`
- `WS /api/workflows/{workflow_id}/logs/ws`
- `GET /api/workflows/{workflow_id}/jobs`
- `GET /api/workflows/{workflow_id}/ats-score`
- `GET /api/workflows/{workflow_id}/skill-gap`

## Demo Payload

```json
{
  "resume_text": "Backend developer with Node.js, REST APIs, PostgreSQL, SQL, and deployment experience.",
  "preferred_role": "Backend Developer",
  "preferred_location": "Bangalore",
  "experience": "1-2 Years",
  "remote_preference": true
}
```
