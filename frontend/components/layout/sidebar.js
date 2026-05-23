"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { useApp } from "@/components/layout/app-shell";

const links = [
  ["/", "Home"],
  ["/dashboard", "Dashboard"],
  ["/campaigns", "Campaigns"],
  ["/calculator", "Calculator"],
  ["/leaderboard", "Leaderboard"],
  ["/profile", "Profile"]
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useApp();

  return (
    <aside className="flex h-full flex-col justify-between rounded-[2rem] border border-[var(--line)] bg-[rgba(255,253,247,0.86)] p-5 shadow-[0_24px_80px_rgba(24,35,15,0.08)] backdrop-blur">
      <div>
        <div className="mb-8">
          <p className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">Creator Economy OS</p>
          <h1 className="mt-2 text-3xl font-semibold">CreatorBridge IQ</h1>
        </div>
        <nav className="space-y-2">
          {links.map(([href, label]) => (
            <Link
              key={href}
              href={href}
              className={clsx(
                "block rounded-2xl px-4 py-3 text-sm transition",
                pathname === href
                  ? "bg-[var(--ink)] text-white"
                  : "text-[var(--muted)] hover:bg-white hover:text-[var(--ink)]"
              )}
            >
              {label}
            </Link>
          ))}
        </nav>
      </div>
      <div className="rounded-2xl bg-[var(--ink)] p-4 text-white">
        <p className="text-sm text-white/70">Signed in as</p>
        <p className="mt-2 text-lg">{user?.name ?? "Guest demo"}</p>
        <p className="text-sm text-white/70">{user?.role ?? "Explore the platform"}</p>
        {user ? (
          <button onClick={logout} className="mt-4 rounded-full bg-white px-4 py-2 text-sm font-medium text-[var(--ink)]">
            Logout
          </button>
        ) : null}
      </div>
    </aside>
  );
}
