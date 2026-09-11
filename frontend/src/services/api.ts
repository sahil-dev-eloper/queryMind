const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("qm_token");
  const headers: Record<string, string> = { "Content-Type": "application/json", ...options.headers as Record<string, string> };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    localStorage.removeItem("qm_token");
    window.location.href = "/login";
    throw new ApiError(401, "Session expired. Please sign in again.");
  }

  if (!response.ok) {
    const payload = await response.json().catch(() => undefined);
    throw new ApiError(response.status, payload?.detail ?? payload?.error?.message ?? "Request failed.");
  }
  return response.json() as Promise<T>;
}
