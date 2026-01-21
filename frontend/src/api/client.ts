// In production (Vercel), we want the frontend to call the
// backend in the same deployment via the "/api" route.
// For local development, you can override this with
// VITE_API_BASE_URL (e.g. http://localhost:8000).
//
// To avoid broken deployments when VITE_API_BASE_URL is accidentally
// set to a localhost URL on Vercel, we automatically fall back to
// "/api" whenever we're not running on localhost.
let API_BASE_URL = "/api";
const envBase = import.meta.env.VITE_API_BASE_URL?.toString().trim();

if (envBase) {
  const isLocalEnvUrl = envBase.includes("localhost") || envBase.includes("127.0.0.1");
  const isBrowser = typeof window !== "undefined";
  const isLocalHost = isBrowser && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1");

  if (!isLocalEnvUrl || isLocalHost) {
    API_BASE_URL = envBase;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {})
    }
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return (await res.json()) as T;
}

export const api = {
  API_BASE_URL,
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  del: <T>(path: string) => request<T>(path, { method: "DELETE" })
};

