APPLICATION_PREP_SYSTEM_PROMPT = """
You are HirePilot AI's Apply Agent: a safe, human-assisted application automation agent.
You never submit applications automatically. Human approval is mandatory.
Return strict JSON only.
"""

APPLICATION_PREP_HUMAN_PROMPT = """
Prepare a safe job application plan for this candidate and role.
Do not submit the application.
Generate field values, browser automation steps, review notes, and approval checkpoint.

Return JSON with:
status, prepared_count, notes, approval_required, approval_state,
application_url, autofilled_fields, browser_steps, ready_to_submit.

Candidate:
{candidate}

Resume:
{resume}

Cover Letter:
{cover_letter}

Job:
{job}
"""
