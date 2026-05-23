"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Bot,
  BriefcaseBusiness,
  Check,
  CheckCircle2,
  ChevronDown,
  CircleDot,
  Cloud,
  FileText,
  Gauge,
  Layers3,
  MapPin,
  MessageSquareText,
  Play,
  Radar,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  Zap
} from "lucide-react";

const workflowLogs = [
  { time: "09:41:12", text: "Job Agent activated", status: "complete" },
  { time: "09:41:19", text: "Searching LinkedIn opportunities", status: "active" },
  { time: "09:41:26", text: "Resume Agent optimizing ATS keywords", status: "complete" },
  { time: "09:41:34", text: "Skill Gap Agent analyzing profile", status: "active" },
  { time: "09:41:43", text: "Application workflow prepared", status: "queued" }
];

const agentMessages = [
  {
    from: "Job Agent",
    to: "Resume Agent",
    message: "Backend-heavy role detected.",
    icon: Search,
    tone: "blue"
  },
  {
    from: "Resume Agent",
    to: "Skill Gap Agent",
    message: "ATS score improved to 84%.",
    icon: FileText,
    tone: "emerald"
  },
  {
    from: "Skill Gap Agent",
    to: "",
    message: "Missing Kubernetes experience identified.",
    icon: Layers3,
    tone: "amber"
  }
];

const traces = [
  "Detected missing keyword: Docker",
  "Resume aligned with backend role",
  "Strong Node.js project relevance identified"
];

const analytics = [
  { label: "Active Agents", value: "5", progress: 82, icon: Bot },
  { label: "Jobs Found", value: "48", progress: 68, icon: BriefcaseBusiness },
  { label: "ATS Score", value: "84%", progress: 84, icon: Gauge },
  { label: "Skill Match", value: "76%", progress: 76, icon: Radar },
  { label: "Applications", value: "12", progress: 54, icon: Zap }
];

const missingSkills = ["Docker", "Kubernetes", "AWS"];

const opportunities = [
  {
    role: "Backend Developer",
    company: "ABC Tech",
    location: "Bangalore",
    match: "91%",
    logo: "A"
  },
  {
    role: "Node.js Engineer",
    company: "Cloudlane",
    location: "Remote",
    match: "88%",
    logo: "C"
  },
  {
    role: "API Platform Engineer",
    company: "NovaStack",
    location: "Bangalore",
    match: "84%",
    logo: "N"
  }
];

const tracking = ["Applications Logged", "Google Sheet Synced", "Skill Gap Updated"];
const API_BASE_URL = "http://127.0.0.1:8000";
const DEFAULT_RESUME_TEXT =
  "Backend developer with Node.js, REST APIs, PostgreSQL, SQL, deployment experience, and product-focused project ownership.";

const fadeIn = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 }
};

export default function HirePilotDashboard() {
  const [form, setForm] = useState({
    resumeText: DEFAULT_RESUME_TEXT,
    preferredRole: "Backend Developer",
    preferredLocation: "Bangalore",
    experience: "1-2 Years",
    remotePreference: true
  });
  const [uploadedFileName, setUploadedFileName] = useState("ashish_backend_resume.pdf");
  const [workflow, setWorkflow] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState("");

  const liveLogs = workflow?.logs?.length ? workflow.logs : [];
  const dashboardLogs = useMemo(() => toDashboardLogs(liveLogs), [liveLogs]);
  const dashboardAnalytics = useMemo(() => toDashboardAnalytics(workflow), [workflow]);
  const dashboardMessages = useMemo(() => toAgentMessages(liveLogs), [liveLogs]);
  const dashboardTraces = useMemo(() => toReasoningTraces(workflow), [workflow]);
  const opportunityRows = useMemo(() => toOpportunityRows(workflow), [workflow]);

  async function handleResumeFile(file) {
    if (!file) return;
    setUploadedFileName(file.name);
    try {
      const text = await file.text();
      setForm((current) => ({
        ...current,
        resumeText: text?.trim() ? text.slice(0, 12000) : DEFAULT_RESUME_TEXT
      }));
    } catch {
      setForm((current) => ({ ...current, resumeText: DEFAULT_RESUME_TEXT }));
    }
  }

  async function activateWorkflow() {
    setIsRunning(true);
    setError("");

    try {
      const payload = {
        resume_text: form.resumeText || DEFAULT_RESUME_TEXT,
        preferred_role: form.preferredRole,
        preferred_location: form.preferredLocation,
        experience: form.experience,
        remote_preference: form.remotePreference
      };

      const response = await fetch(`${API_BASE_URL}/api/workflows/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error("Unable to start workflow");
      }

      const data = await response.json();
      setWorkflow(data.workflow);
      await pollWorkflow(data.workflow.workflow_id);
    } catch (workflowError) {
      setError(workflowError.message || "Workflow failed to start");
    } finally {
      setIsRunning(false);
    }
  }

  async function pollWorkflow(workflowId) {
    for (let attempt = 0; attempt < 180; attempt += 1) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      const response = await fetch(`${API_BASE_URL}/api/workflows/${workflowId}`);
      if (!response.ok) continue;
      const data = await response.json();
      setWorkflow(data.workflow);

      if (["completed", "failed"].includes(data.workflow.status)) {
        break;
      }
    }
  }

  async function prepareApplication(jobIndex = 0) {
    if (!workflow?.workflow_id) return;
    setError("");
    const response = await fetch(`${API_BASE_URL}/api/workflows/prepare-application`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ workflow_id: workflow.workflow_id, job_index: jobIndex })
    });
    if (!response.ok) {
      setError("Unable to prepare application");
      return;
    }
    const data = await response.json();
    setWorkflow(data.workflow);
  }

  async function approveApplication() {
    if (!workflow?.workflow_id) return;
    setError("");
    const response = await fetch(`${API_BASE_URL}/api/workflows/approve-application`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ workflow_id: workflow.workflow_id, human_approved: true })
    });
    if (!response.ok) {
      setError("Unable to approve application");
      return;
    }
    const data = await response.json();
    setWorkflow(data.workflow);
  }

  return (
    <main className="min-h-screen bg-[#f7f8fb] text-slate-950">
      <div className="mx-auto flex w-full max-w-[1540px] flex-col gap-5 px-4 py-4 sm:px-6 lg:px-8">
        <TopBar />

        <div className="grid gap-5 xl:grid-cols-[320px_minmax(0,1fr)_380px]">
          <motion.aside
            variants={fadeIn}
            initial="hidden"
            animate="visible"
            transition={{ duration: 0.35 }}
            className="xl:sticky xl:top-4 xl:h-[calc(100vh-2rem)]"
          >
            <CareerPreferences
              form={form}
              setForm={setForm}
              uploadedFileName={uploadedFileName}
              onResumeFile={handleResumeFile}
              onActivate={activateWorkflow}
              isRunning={isRunning}
              error={error}
            />
          </motion.aside>

          <motion.section
            variants={fadeIn}
            initial="hidden"
            animate="visible"
            transition={{ duration: 0.4, delay: 0.05 }}
            className="min-w-0"
          >
            <CommandCenter
              workflow={workflow}
              logs={dashboardLogs}
              analytics={dashboardAnalytics}
              agentMessages={dashboardMessages}
              traces={dashboardTraces}
            />
          </motion.section>

          <motion.aside
            variants={fadeIn}
            initial="hidden"
            animate="visible"
            transition={{ duration: 0.4, delay: 0.1 }}
            className="min-w-0 space-y-5 xl:sticky xl:top-4 xl:h-[calc(100vh-2rem)] xl:overflow-y-auto xl:pr-1"
          >
            <ATSCard workflow={workflow} />
            <SkillGapCard workflow={workflow} />
            <OpportunitiesCard
              jobs={opportunityRows.length ? opportunityRows : opportunities}
              workflow={workflow}
              onPrepare={prepareApplication}
            />
            <TrackingCard workflow={workflow} onApprove={approveApplication} />
          </motion.aside>
        </div>
      </div>
    </main>
  );
}

function TopBar() {
  return (
    <header className="flex flex-col justify-between gap-4 rounded-xl border border-slate-200 bg-white/90 px-4 py-3 shadow-sm shadow-slate-200/60 backdrop-blur sm:flex-row sm:items-center">
      <div className="flex items-center gap-3">
        <div className="flex size-10 items-center justify-center rounded-xl bg-slate-950 text-white shadow-sm">
          <Bot className="size-5" />
        </div>
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-base font-semibold tracking-tight text-slate-950">HirePilot AI</h1>
            <span className="rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-[11px] font-medium text-blue-700">
              Phase 1 MVP
            </span>
          </div>
          <p className="text-sm text-slate-500">Autonomous Multi-Agent Job Application Copilot</p>
        </div>
      </div>

      <div className="flex items-center gap-2 text-sm">
        <div className="hidden items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-slate-600 md:flex">
          <span className="size-2 rounded-full bg-emerald-500 shadow-[0_0_0_4px_rgba(16,185,129,0.14)]" />
          Workflow online
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50">
          <RefreshCw className="size-4" />
          Sync
        </button>
      </div>
    </header>
  );
}

function CareerPreferences({ form, setForm, uploadedFileName, onResumeFile, onActivate, isRunning, error }) {
  return (
    <Panel className="flex h-full flex-col">
      <div>
        <SectionTitle eyebrow="Input Layer" title="Career Preferences" icon={FileText} />
        <div className="mt-5 space-y-4">
          <UploadBox fileName={uploadedFileName} onResumeFile={onResumeFile} />
          <Field label="Preferred Role">
            <input
              className="input"
              placeholder="Backend Developer"
              value={form.preferredRole}
              onChange={(event) => setForm((current) => ({ ...current, preferredRole: event.target.value }))}
            />
          </Field>
          <Field label="Preferred Location">
            <div className="relative">
              <MapPin className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" />
              <input
                className="input pl-9"
                placeholder="Bangalore"
                value={form.preferredLocation}
                onChange={(event) => setForm((current) => ({ ...current, preferredLocation: event.target.value }))}
              />
            </div>
          </Field>
          <Field label="Experience">
            <div className="relative">
              <select
                className="input appearance-none pr-10"
                value={form.experience}
                onChange={(event) => setForm((current) => ({ ...current, experience: event.target.value }))}
              >
                <option value="Fresher">Fresher</option>
                <option value="1-2 Years">1-2 Years</option>
                <option value="3-5 Years">3-5 Years</option>
                <option value="5+ Years">5+ Years</option>
              </select>
              <ChevronDown className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" />
            </div>
          </Field>
          <Field label="Sources to scrape">
            <div className="grid grid-cols-3 gap-2">
              {["LinkedIn", "Naukri", "Indeed"].map((source) => (
                <div key={source} className="rounded-lg border border-slate-200 bg-slate-50 px-2 py-2 text-center text-xs font-medium text-slate-600">
                  {source}
                </div>
              ))}
            </div>
          </Field>
          <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-3 py-3">
            <div>
              <p className="text-sm font-medium text-slate-800">Remote Preference</p>
              <p className="text-xs text-slate-500">Include remote-first roles</p>
            </div>
            <button
              aria-label="Toggle remote preference"
              onClick={() => setForm((current) => ({ ...current, remotePreference: !current.remotePreference }))}
              className={`relative h-6 w-11 rounded-full transition ${form.remotePreference ? "bg-slate-950" : "bg-slate-300"}`}
            >
              <span className={`absolute top-1 size-4 rounded-full bg-white shadow-sm transition ${form.remotePreference ? "right-1" : "left-1"}`} />
            </button>
          </div>
        </div>
      </div>

      <div className="mt-5 space-y-3">
        <button
          onClick={onActivate}
          disabled={isRunning}
          className="group inline-flex w-full items-center justify-center gap-2 rounded-xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          <Play className={`size-4 fill-white ${isRunning ? "animate-pulse" : ""}`} />
          {isRunning ? "Agents Running..." : "Activate AI Workflow"}
          <ArrowRight className="size-4 transition group-hover:translate-x-0.5" />
        </button>
        {error ? <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs font-medium text-red-700">{error}</p> : null}
        <p className="text-center text-xs leading-5 text-slate-500">
          Agents use your preferences to prepare role-specific applications.
        </p>
      </div>
    </Panel>
  );
}

function UploadBox({ fileName, onResumeFile }) {
  return (
    <label className="block cursor-pointer rounded-xl border border-dashed border-slate-300 bg-slate-50/80 p-4 transition hover:border-blue-300 hover:bg-blue-50/40">
      <input
        className="sr-only"
        type="file"
        accept=".txt,.md,.pdf,.doc,.docx"
        onChange={(event) => onResumeFile(event.target.files?.[0])}
      />
      <div className="flex items-start gap-3">
        <div className="flex size-10 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600">
          <UploadCloud className="size-5" />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-medium text-slate-800">Drop resume here</p>
          <p className="mt-1 text-xs leading-5 text-slate-500">PDF, DOCX, TXT, or MD up to 10 MB</p>
          <div className="mt-3 flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2">
            <FileText className="size-4 shrink-0 text-blue-600" />
            <span className="truncate text-xs font-medium text-slate-700">{fileName}</span>
          </div>
        </div>
      </div>
    </label>
  );
}

function CommandCenter({ workflow, logs, analytics, agentMessages, traces }) {
  return (
    <div className="space-y-5">
      <Panel className="overflow-hidden">
        <div className="flex flex-col justify-between gap-5 md:flex-row md:items-start">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
              <Sparkles className="size-3.5" />
              Multi-agent orchestration
            </div>
            <h2 className="mt-4 text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">AI Command Center</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
              Real-time multi-agent workflow orchestration for role discovery, resume optimization, skill matching, and application preparation.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <Signal label="Status" value={workflow?.status ?? "ready"} />
            <Signal label="Workflow" value={workflow?.workflow_id ? workflow.workflow_id.slice(0, 8) : "new"} />
          </div>
        </div>
      </Panel>

      <LiveAnalytics analytics={analytics} />

      <div className="grid gap-5 lg:grid-cols-[1.05fr_0.95fr]">
        <WorkflowLogs logs={logs} />
        <AgentFeed messages={agentMessages} />
      </div>

      <ThinkingTraces traces={traces} workflow={workflow} />
    </div>
  );
}

function WorkflowLogs({ logs }) {
  return (
    <Panel>
      <SectionTitle eyebrow="Live Workflow Logs" title="Activity Stream" icon={Cloud} />
      <div className="mt-5 rounded-xl border border-slate-200 bg-slate-950 p-3 shadow-inner">
        <div className="max-h-[310px] space-y-2 overflow-hidden">
          {logs.map((log, index) => (
            <motion.div
              key={log.text}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.25, delay: index * 0.08 }}
              className="flex items-center gap-3 rounded-lg border border-white/5 bg-white/[0.03] px-3 py-2.5 text-sm"
            >
              <StatusIcon status={log.status} />
              <span className="font-mono text-xs text-slate-500">{log.time}</span>
              <span className="min-w-0 flex-1 truncate text-slate-200">{log.text}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </Panel>
  );
}

function AgentFeed({ messages }) {
  return (
    <Panel>
      <SectionTitle eyebrow="Agent Communication Feed" title="Inter-Agent Notes" icon={MessageSquareText} />
      <div className="mt-5 space-y-3">
        {messages.map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.message} className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm shadow-slate-200/50">
              <div className="flex items-start gap-3">
                <div className={`flex size-9 shrink-0 items-center justify-center rounded-lg ${toneClass(item.tone)}`}>
                  <Icon className="size-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-xs font-medium text-slate-500">
                    {item.from} {item.to ? <span className="text-slate-300">→</span> : null} {item.to}
                  </p>
                  <p className="mt-1 text-sm font-medium leading-5 text-slate-800">"{item.message}"</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </Panel>
  );
}

function ThinkingTraces({ traces, workflow }) {
  return (
    <Panel>
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <SectionTitle eyebrow="Thinking Traces" title="Reasoning Insights" icon={CircleDot} />
        <span className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-500">
          {workflow?.updated_at ? "Updated from backend" : "Waiting for workflow"}
        </span>
      </div>
      <div className="mt-5 grid gap-3 md:grid-cols-3">
        {traces.map((trace) => (
          <div key={trace} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <div className="mb-3 flex size-8 items-center justify-center rounded-lg bg-white text-blue-600 shadow-sm">
              <Sparkles className="size-4" />
            </div>
            <p className="text-sm font-medium leading-5 text-slate-800">{trace}</p>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function LiveAnalytics({ analytics }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
      {analytics.map((item, index) => {
        const Icon = item.icon;
        return (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.04 }}
            className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-200/60"
          >
            <div className="flex items-center justify-between gap-3">
              <Icon className="size-4 text-slate-400" />
              <span className="text-lg font-semibold tracking-tight text-slate-950">{item.value}</span>
            </div>
            <p className="mt-3 text-xs font-medium text-slate-500">{item.label}</p>
            <Progress value={item.progress} className="mt-3" />
          </motion.div>
        );
      })}
    </div>
  );
}

function ATSCard({ workflow }) {
  const score = workflow?.ats_score || 84;
  const selectedRole = workflow?.selected_job?.role || "backend engineering roles";
  return (
    <Panel>
      <SectionTitle eyebrow="Score Layer" title="ATS Compatibility" icon={ShieldCheck} />
      <div className="mt-5 flex items-center gap-5">
        <ProgressRing value={score} />
        <div className="min-w-0">
          <p className="text-sm font-semibold text-slate-800">Strong ATS alignment</p>
          <p className="mt-1 text-sm leading-6 text-slate-500">Optimized for {selectedRole}</p>
          <div className="mt-3 flex items-center gap-2 text-xs font-medium text-emerald-700">
            <CheckCircle2 className="size-4" />
            Keyword alignment improved
          </div>
        </div>
      </div>
    </Panel>
  );
}

function SkillGapCard({ workflow }) {
  const perJobSkills = workflow?.job_results?.flatMap((result) => result.skill_gap?.missing_skills || []) || [];
  const perJobRecommendations = workflow?.job_results?.flatMap((result) => result.skill_gap?.recommendations || []) || [];
  const skills = perJobSkills.length ? [...new Set(perJobSkills)].slice(0, 8) : (workflow?.missing_skills?.length ? workflow.missing_skills : missingSkills);
  const recommendations = perJobRecommendations.length
    ? [...new Set(perJobRecommendations)].slice(0, 4)
    : workflow?.skill_gap?.recommendations?.length
    ? workflow.skill_gap.recommendations
    : ["Learn Docker basics", "Add deployment project", "Improve cloud exposure"];

  return (
    <Panel>
      <SectionTitle eyebrow="Profile Intelligence" title="Skill Gap Insights" icon={Layers3} />
      <div className="mt-5 flex flex-wrap gap-2">
        {skills.map((skill) => (
          <span key={skill} className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700">
            {skill}
          </span>
        ))}
      </div>
      <div className="mt-5 space-y-3">
        {recommendations.map((item) => (
          <div key={item} className="flex items-center gap-3 text-sm text-slate-700">
            <Check className="size-4 text-blue-600" />
            {item}
          </div>
        ))}
      </div>
    </Panel>
  );
}

function OpportunitiesCard({ jobs, workflow, onPrepare }) {
  return (
    <Panel>
      <SectionTitle eyebrow="Matched Roles" title="Top Matching Opportunities" icon={BriefcaseBusiness} />
      <div className="mt-5 space-y-3">
        {jobs.map((job, index) => (
          <div key={`${job.company}-${job.role}-${index}`} className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm shadow-slate-200/50">
            <div className="flex items-start gap-3">
              <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-950 text-sm font-semibold text-white">
                {job.logo || job.company?.charAt(0) || "H"}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-slate-900">{job.role}</p>
                    <p className="mt-1 truncate text-xs text-slate-500">{job.company} - {job.location} - {job.source || "Source"}</p>
                  </div>
                  <span className="shrink-0 rounded-full bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700">
                    {job.match || `${job.match_score || 80}%`} Match
                  </span>
                </div>
                {job.skillMatch ? (
                  <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                    <div className="rounded-lg bg-blue-50 px-2 py-1.5 font-semibold text-blue-700">{job.match} score</div>
                    <div className="rounded-lg bg-slate-50 px-2 py-1.5 font-semibold text-slate-600">{job.skillMatch}% skill match</div>
                  </div>
                ) : null}
                <div className="mt-3 flex flex-wrap gap-2">
                  <button className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-50">
                    View Role
                  </button>
                  <button
                    onClick={() => onPrepare(index)}
                    disabled={!workflow?.workflow_id}
                    className="rounded-lg bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700 transition hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Prepare Application
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function TrackingCard({ workflow, onApprove }) {
  const application = workflow?.application_status;
  const approvalState = application?.approval_state || "waiting_for_workflow";
  const canApprove = application?.status === "prepared" && application?.approval_state === "waiting_for_human_review";
  const statusItems = application?.browser_steps?.length
    ? application.browser_steps
    : tracking;

  return (
    <Panel>
      <SectionTitle eyebrow="Ops Sync" title="Career Tracking" icon={CheckCircle2} />
      <div className="mt-5 space-y-4">
        {statusItems.map((item, index) => (
          <div key={item} className="flex gap-3">
            <div className="flex flex-col items-center">
              <span className="flex size-6 items-center justify-center rounded-full bg-emerald-50 text-emerald-700 ring-1 ring-emerald-100">
                <Check className="size-3.5" />
              </span>
              {index < statusItems.length - 1 ? <span className="h-6 w-px bg-slate-200" /> : null}
            </div>
            <div>
              <p className="text-sm font-medium text-slate-800">{item}</p>
              <p className="mt-0.5 text-xs text-slate-500">{approvalState}</p>
            </div>
          </div>
        ))}
      </div>
      <button
        onClick={onApprove}
        disabled={!canApprove}
        className="mt-5 w-full rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {approvalState === "approved_by_human" ? "Application Approved" : "Approve & Apply"}
      </button>
    </Panel>
  );
}

function Panel({ children, className = "" }) {
  return (
    <div className={`rounded-xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-200/70 ${className}`}>
      {children}
    </div>
  );
}

function SectionTitle({ eyebrow, title, icon: Icon }) {
  return (
    <div className="flex items-start gap-3">
      <div className="flex size-9 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-slate-600">
        <Icon className="size-4" />
      </div>
      <div>
        <p className="text-xs font-medium uppercase tracking-[0.12em] text-slate-400">{eyebrow}</p>
        <h2 className="mt-1 text-base font-semibold tracking-tight text-slate-950">{title}</h2>
      </div>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-medium text-slate-500">{label}</span>
      {children}
    </label>
  );
}

function Progress({ value, className = "" }) {
  return (
    <div className={`h-1.5 overflow-hidden rounded-full bg-slate-100 ${className}`}>
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${value}%` }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="h-full rounded-full bg-blue-600"
      />
    </div>
  );
}

function ProgressRing({ value }) {
  const circumference = 2 * Math.PI * 40;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="relative size-28 shrink-0">
      <svg className="size-28 -rotate-90" viewBox="0 0 96 96" aria-label={`ATS score ${value}%`}>
        <circle cx="48" cy="48" r="40" stroke="#e2e8f0" strokeWidth="8" fill="transparent" />
        <motion.circle
          cx="48"
          cy="48"
          r="40"
          stroke="#2563eb"
          strokeWidth="8"
          strokeLinecap="round"
          fill="transparent"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 0.9, ease: "easeOut" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-semibold tracking-tight text-slate-950">{value}%</span>
        <span className="text-[11px] font-medium text-slate-400">ATS</span>
      </div>
    </div>
  );
}

function Signal({ label, value }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
      <p className="text-xs font-medium text-slate-500">{label}</p>
      <p className="mt-1 text-sm font-semibold text-slate-950">{value}</p>
    </div>
  );
}

function toDashboardLogs(logs) {
  if (!logs?.length) {
    return workflowLogs;
  }

  return logs.map((log) => ({
    time: formatTime(log.timestamp),
    text: log.message,
    status: log.level === "success" ? "complete" : log.level === "error" ? "queued" : "active"
  }));
}

function toDashboardAnalytics(workflow) {
  if (!workflow) {
    return analytics;
  }

  const activeAgents = Object.values(workflow.agent_status || {}).filter((status) => status === "running").length;
  const completedAgents = Object.values(workflow.agent_status || {}).filter((status) => status === "completed").length;
  const jobsFound = workflow.jobs_found?.length || 0;
  const bestResult = workflow.job_results?.length
    ? [...workflow.job_results].sort((a, b) => (b.resume?.ats_score || 0) - (a.resume?.ats_score || 0))[0]
    : null;
  const atsScore = bestResult?.resume?.ats_score || workflow.ats_score || workflow.optimized_resume?.ats_score || 0;
  const skillMatch = bestResult?.skill_gap?.skill_match_percent || workflow.skill_gap?.skill_match_percent || 0;
  const prepared = workflow.job_results?.filter((result) => result.application?.approval_state === "waiting_for_human_review").length || workflow.application_status?.prepared_count || 0;

  return [
    { label: "Active Agents", value: String(activeAgents || completedAgents || 0), progress: Math.max(20, completedAgents * 20), icon: Bot },
    { label: "Jobs Found", value: String(jobsFound), progress: Math.min(100, jobsFound * 16), icon: BriefcaseBusiness },
    { label: "ATS Score", value: `${atsScore}%`, progress: atsScore, icon: Gauge },
    { label: "Skill Match", value: `${skillMatch}%`, progress: skillMatch, icon: Radar },
    { label: "Applications", value: String(prepared), progress: Math.min(100, prepared * 30), icon: Zap }
  ];
}

function toOpportunityRows(workflow) {
  if (workflow?.job_results?.length) {
    return workflow.job_results.map((result) => ({
      ...result.job,
      job_id: result.job_id,
      match: `${result.resume?.ats_score || result.job.match_score || 80}% ATS`,
      skillMatch: result.skill_gap?.skill_match_percent || 0,
      approvalState: result.application?.approval_state,
      sheetSync: result.sheet_sync?.status
    }));
  }

  return workflow?.jobs_found || [];
}

function toAgentMessages(logs) {
  const handoffs = logs?.filter((log) => log.message?.includes("\u2192") || log.message?.includes("->")) || [];
  if (!handoffs.length) {
    return agentMessages;
  }

  return handoffs.slice(-3).map((log, index) => {
    const parts = log.message.split(":");
    const route = parts[0].replace("\u2192", "->").split("->");
    const icons = [Search, FileText, Layers3];
    const tones = ["blue", "emerald", "amber"];
    return {
      from: route[0]?.trim() || log.agent,
      to: route[1]?.trim() || "",
      message: parts.slice(1).join(":").trim() || log.message,
      icon: icons[index] || MessageSquareText,
      tone: tones[index] || "blue"
    };
  });
}

function toReasoningTraces(workflow) {
  if (!workflow) {
    return traces;
  }

  const missing = workflow.optimized_resume?.missing_keywords?.map((keyword) => `Detected missing keyword: ${keyword}`) || [];
  const recommendations = workflow.skill_gap?.recommendations || [];
  const selected = workflow.selected_job?.role ? [`Resume aligned with ${workflow.selected_job.role}`] : [];
  return [...missing, ...selected, ...recommendations].slice(0, 3);
}

function formatTime(timestamp) {
  if (!timestamp) return "--:--:--";
  try {
    return new Intl.DateTimeFormat("en", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false
    }).format(new Date(timestamp));
  } catch {
    return "--:--:--";
  }
}

function StatusIcon({ status }) {
  if (status === "complete") {
    return <CheckCircle2 className="size-4 shrink-0 text-emerald-400" />;
  }

  if (status === "active") {
    return <span className="size-2.5 shrink-0 animate-pulse rounded-full bg-blue-400 shadow-[0_0_0_4px_rgba(96,165,250,0.14)]" />;
  }

  return <span className="size-2.5 shrink-0 rounded-full bg-slate-500" />;
}

function toneClass(tone) {
  const tones = {
    blue: "bg-blue-50 text-blue-700",
    emerald: "bg-emerald-50 text-emerald-700",
    amber: "bg-amber-50 text-amber-700"
  };

  return tones[tone] ?? "bg-slate-50 text-slate-600";
}
