export const API_BASE_URL = "http://localhost:8000";

export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Error desconocido" }));
    console.error("API Error:", res.status, res.url, error);
    throw new Error(error.detail ?? `Error ${res.status}`);
  }

  if (res.status === 204) return undefined as T;

  const data = await res.json();
  
  
  console.log(
    `%c ${res.status} ${options?.method ?? "GET"} ${path}`,
    "color: #22c55e; font-weight: bold;",
    data
  );

  return data;
}