const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers,
    ...options,
  });

  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const message =
      (isJson && payload?.detail) ||
      (typeof payload === "string" && payload) ||
      response.statusText ||
      "Request failed";
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }

  return payload;
}

export function loginUrl() {
  return `${API_BASE}/login`;
}

export function logoutUrl() {
  return `${API_BASE}/logout`;
}

export function getMe() {
  return apiFetch("/api/me");
}

export function getVault() {
  return apiFetch("/api/vault");
}

export function getEntry(service) {
  return apiFetch(`/api/vault/${encodeURIComponent(service)}`);
}

export function putEntry(service, entry) {
  return apiFetch(`/api/vault/${encodeURIComponent(service)}`, {
    method: "PUT",
    body: JSON.stringify(entry),
  });
}

export function deleteEntry(service) {
  return apiFetch(`/api/vault/${encodeURIComponent(service)}`, {
    method: "DELETE",
  });
}
