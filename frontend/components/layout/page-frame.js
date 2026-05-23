"use client";

import { Sidebar } from "@/components/layout/sidebar";

export function PageFrame({ title, subtitle, children, actions }) {
  return (
    <main className="min-h-screen p-4 md:p-6">
      <div className="mx-auto grid max-w-7xl gap-4 md:grid-cols-[280px_minmax(0,1fr)]">
        <div className="md:sticky md:top-6 md:h-[calc(100vh-3rem)]">
          <Sidebar />
        </div>
        <section className="rounded-[2rem] border border-[var(--line)] bg-[rgba(255,253,247,0.8)] p-5 shadow-[0_24px_80px_rgba(24,35,15,0.08)] backdrop-blur md:p-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">CreatorBridge IQ</p>
              <h2 className="mt-2 text-4xl font-semibold">{title}</h2>
              <p className="mt-2 max-w-3xl text-[var(--muted)]">{subtitle}</p>
            </div>
            {actions ? <div>{actions}</div> : null}
          </div>
          <div className="mt-8">{children}</div>
        </section>
      </div>
    </main>
  );
}
