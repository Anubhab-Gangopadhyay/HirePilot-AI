"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

const AppContext = createContext(null);
const apiBase = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:4000";

async function request(path, options = {}) {
  const response = await fetch(`${apiBase}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {})
    }
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Request failed" }));
    throw new Error(error.message ?? "Request failed");
  }

  return response.json();
}

export function AppShell({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const stored = window.localStorage.getItem("creatorbridge-token");
    if (stored) {
      setToken(stored);
    }
  }, []);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    request("/api/auth/me", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then((data) => setUser(data.user))
      .catch(() => {
        setToken(null);
        setUser(null);
        window.localStorage.removeItem("creatorbridge-token");
      })
      .finally(() => setLoading(false));
  }, [token]);

  const value = useMemo(() => ({
    apiBase,
    token,
    user,
    loading,
    async login(email, password) {
      const data = await request("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });
      setToken(data.token);
      setUser(data.user);
      window.localStorage.setItem("creatorbridge-token", data.token);
      return data;
    },
    async register(payload) {
      const data = await request("/api/auth/register", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      setToken(data.token);
      setUser(data.user);
      window.localStorage.setItem("creatorbridge-token", data.token);
      return data;
    },
    async authed(path, options = {}) {
      if (!token) {
        throw new Error("Login required");
      }
      return request(path, {
        ...options,
        headers: {
          Authorization: `Bearer ${token}`,
          ...(options.headers ?? {})
        }
      });
    },
    logout() {
      setToken(null);
      setUser(null);
      window.localStorage.removeItem("creatorbridge-token");
    }
  }), [token, user, loading]);

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useApp must be used within AppShell");
  }
  return context;
}
