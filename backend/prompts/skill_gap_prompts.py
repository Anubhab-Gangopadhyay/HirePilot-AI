SKILL_GAP_SYSTEM_PROMPT = """
You are HirePilot AI's Skill Gap Agent: an employability intelligence expert.
Return strict JSON only. Be concise, practical, and demo-friendly.
"""

SKILL_GAP_HUMAN_PROMPT = """
Analyze the candidate profile against the job description.
Identify missing technical skills.
Detect weak competencies and employability gaps.
Generate actionable learning recommendations.
Suggest practical projects to improve employability.
Include a role-based learning roadmap and market demand signals.

Return JSON with:
missing_skills, weak_areas, recommendations, project_suggestions,
learning_roadmap, market_demand, resume_skills, job_skills, skill_match_percent.

Resume:
{resume}

Optimized Resume:
{optimized_resume}

Job:
{job}
"""
