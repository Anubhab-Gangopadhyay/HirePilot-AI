# HirePilot AI — Detailed README.md

````md id="m7q2xe"
# HirePilot AI
## Autonomous Multi-Agent Job Application Copilot

<p align="center">
  <b>An AI-native employability intelligence platform powered by coordinated multi-agent workflows.</b>
</p>

---

# 📌 Overview

HirePilot AI is a multi-agent AI platform designed to intelligently assist users throughout the job application journey.

The platform combines:
- Generative AI,
- Agentic AI,
- workflow orchestration,
- browser automation,
- and real-time career intelligence

to help users:
- discover jobs,
- optimize resumes,
- identify missing skills,
- prepare applications,
- and track career progress.

Unlike traditional job automation platforms that focus on mass applications, HirePilot AI focuses on:

> improving employability intelligently.

The system behaves like:
> an autonomous AI workforce managing the user’s career pipeline.

---

# 🚀 Problem Statement

Modern job seekers face several challenges:

- Manually searching across multiple platforms
- Tailoring resumes repeatedly
- Understanding ATS optimization
- Identifying missing skills
- Tracking applications inefficiently
- Managing repetitive application workflows

Existing solutions mostly focus on:
❌ blind automation  
❌ mass auto-apply systems  

Very few platforms provide:
✅ employability intelligence  
✅ coordinated AI agents  
✅ personalized optimization  
✅ skill-gap analysis  
✅ transparent AI workflows  

HirePilot AI solves this using coordinated multi-agent intelligence.

---

# 🎯 Key Objectives

The platform aims to:

✅ automate repetitive career workflows  
✅ improve ATS compatibility  
✅ increase interview probability  
✅ identify employability gaps  
✅ provide actionable recommendations  
✅ assist applications safely  
✅ maintain real-time career tracking  

---

# 🧠 Core Innovation

HirePilot AI is NOT:
❌ an AI spam auto-apply bot

It IS:
✅ an autonomous AI employability intelligence system.

The platform emphasizes:
- intelligent optimization,
- coordinated AI workflows,
- and human-assisted automation.

---

# 🏗 System Architecture

```text
User Uploads Resume
        ↓
Orchestrator Agent
        ↓
------------------------------------------------
| Job Discovery Agent                          |
| Resume Intelligence Agent                    |
| Skill Gap Intelligence Agent                 |
| Application Workflow Agent                   |
------------------------------------------------
        ↓
Google Sheets Tracking Agent
        ↓
Frontend AI Command Center
````

---

# 🤖 Multi-Agent AI System

The platform uses coordinated AI agents where each agent has:

* a dedicated role,
* specialized intelligence,
* and independent responsibilities.

All agents are orchestrated through:

* n8n workflows,
* FastAPI,
* and centralized workflow state management.

---

# 🧩 AI Agents

---

# 1. Orchestrator Agent ⭐⭐⭐⭐⭐

## Purpose

Acts as the central AI coordination layer.

## Responsibilities

* receives user input
* triggers downstream agents
* maintains workflow state
* coordinates execution order
* aggregates outputs
* streams live logs
* handles retries/errors

## Why Important

This transforms the platform from:
❌ isolated AI prompts

to:
✅ true Agentic AI orchestration.

---

# 2. Job Discovery Agent ⭐⭐⭐⭐⭐

## Purpose

Find highly relevant jobs intelligently.

## Supported Platforms

* LinkedIn
* Naukri
* Indeed
* Company career pages

## Responsibilities

* scrape jobs
* extract job descriptions
* extract skills
* extract apply links
* filter irrelevant jobs
* rank opportunities

## Example Output

```json
{
  "company": "ABC Tech",
  "role": "Backend Developer",
  "location": "Bangalore",
  "skills": ["Node.js", "Docker"],
  "apply_link": "https://..."
}
```

---

# 3. Resume Intelligence Agent ⭐⭐⭐⭐⭐

## Purpose

Tailor resumes according to each job description.

## Responsibilities

* ATS optimization
* keyword insertion
* project optimization
* resume tailoring
* cover letter generation
* ATS scoring

## Features

* one tailored resume per job
* ATS keyword alignment
* role-specific optimization

## Example Output

```json
{
  "company": "ABC Tech",
  "ats_score": 84,
  "missing_keywords": ["Docker"],
  "optimized_resume": "..."
}
```

---

# 4. Skill Gap Intelligence Agent ⭐⭐⭐⭐⭐

## Main USP of the Platform

## Purpose

Analyze employability gaps intelligently.

## Responsibilities

* compare resume vs JD
* detect missing skills
* identify weak competencies
* generate recommendations
* generate learning roadmap
* suggest projects

## Example Output

```json
{
  "skill_match_score": 78,
  "missing_skills": [
    "Docker",
    "Kubernetes"
  ],
  "recommendations": [
    "Learn Docker Basics",
    "Build Deployment Project"
  ]
}
```

## Why It Matters

Most platforms:
❌ automate applications

HirePilot AI:
✅ improves candidate quality.

---

# 5. Application Workflow Agent ⭐⭐⭐⭐

## Purpose

Prepare applications safely using browser automation.

## Responsibilities

* open application pages
* autofill forms
* upload optimized resumes
* prepare workflows
* wait for approval

## Important Safety Principle

Applications are NEVER auto-submitted without:
✅ explicit human approval

This creates:

* safer automation
* realistic workflows
* ethical AI usage

---

# 6. Google Sheets Tracking Agent ⭐⭐⭐⭐

## Purpose

Maintain persistent real-time career tracking.

## Responsibilities

* update Google Sheets live
* track ATS scores
* track missing skills
* track application status
* track recommendations
* store application links

---

# ⚡ Real-Time AI Command Center

The frontend dashboard visualizes:

* AI workflow execution
* live logs
* agent communication
* ATS scores
* skill-gap insights
* application progress

This creates:

> perceived intelligence

which makes the platform feel like:
a real autonomous AI system.

---

# 📡 Example AI Logs

```text
[10:21] Job Agent activated
[10:22] LinkedIn jobs scraped
[10:23] Resume optimized for ABC Tech
[10:24] Missing Docker skill detected
[10:25] Google Sheet updated
[10:26] Waiting for approval
```

---

# 🛠 Tech Stack

# Frontend

| Purpose    | Technology   |
| ---------- | ------------ |
| UI         | React.js     |
| Framework  | Next.js      |
| Styling    | Tailwind CSS |
| Components | shadcn/ui    |

---

# Backend

| Purpose  | Technology |
| -------- | ---------- |
| APIs     | FastAPI    |
| Language | Python     |

---

# AI & Agents

| Purpose          | Technology    |
| ---------------- | ------------- |
| LLM              | OpenAI GPT-4o |
| Agent Framework  | CrewAI        |
| Prompt Pipelines | LangChain     |

---

# Automation

| Purpose             | Technology    |
| ------------------- | ------------- |
| Workflow Automation | n8n           |
| Browser Automation  | Playwright    |
| Parsing             | BeautifulSoup |

---

# Tracking & Storage

| Purpose       | Technology        |
| ------------- | ----------------- |
| Live Tracking | Google Sheets API |

---

# 🔄 Workflow

```text
User Uploads Resume
        ↓
User Enters Preferences
        ↓
Job Agent Scrapes Jobs
        ↓
Resume Agent Tailors Resume
        ↓
Skill Gap Agent Detects Missing Skills
        ↓
Google Sheet Updated
        ↓
Apply Agent Prepares Applications
        ↓
Human Approval
        ↓
Application Submission
```

---

# 📊 Google Sheets Tracking

The platform updates Google Sheets in real time.

## Example Sheet

| Company | Role | ATS Score | Missing Skills | Status |
| ------- | ---- | --------- | -------------- | ------ |

This creates:
✅ persistent career intelligence
✅ workflow visibility
✅ real-time tracking

---

# 🔐 Human-in-the-Loop Safety

HirePilot AI uses:
✅ human-assisted automation

instead of:
❌ uncontrolled autonomous applications

This improves:

* trust,
* safety,
* and platform realism.

---

# 📁 Project Structure

```text
backend/
 ├── agents/
 ├── services/
 ├── routes/
 ├── workflows/
 ├── utils/
 └── main.py

frontend/
 ├── components/
 ├── dashboard/
 ├── pages/
 └── styles/

n8n/
 ├── orchestrator_workflow.json
 ├── scraping_workflows.json
 ├── resume_workflows.json
 └── apply_workflows.json
```

---

# 🚀 Installation

# Clone Repository

```bash
git clone <repository-url>
cd hirepilot-ai
```

---

# Install Backend Dependencies

```bash
pip install -r requirements.txt
```

---

# Install Frontend Dependencies

```bash
npm install
```

---

# 🔑 Environment Variables

Create `.env` file:

```env
OPENAI_API_KEY=your_key
GOOGLE_SHEETS_CREDENTIALS=your_credentials
LINKEDIN_EMAIL=your_email
LINKEDIN_PASSWORD=your_password
```

---

# ▶ Run Backend

```bash
uvicorn main:app --reload
```

---

# ▶ Run Frontend

```bash
npm run dev
```

---

# 🏆 Hackathon Relevance

This project strongly aligns with:

✅ Generative AI
✅ Agentic AI
✅ Multi-Agent Collaboration
✅ Real-world Usefulness
✅ Workflow Automation
✅ Explainable AI

---

# 💡 Future Scope

* Interview preparation agent
* Recruiter intelligence engine
* Adaptive learning loop
* Career roadmap generation
* AI networking assistant
* Resume performance analytics

---

# 👨‍💻 Team

## Team Name

Agent_Forge

## Team Members

* Anubhab Gangopadhyay
* Samrat Ghosh
* Arman Khichi

---

# 🌟 Vision

> “Transforming job applications from repetitive automation into intelligent employability optimization powered by coordinated AI agents.”

HirePilot AI aims to become:

> an AI-native career intelligence ecosystem for the next generation workforce.

```
```
