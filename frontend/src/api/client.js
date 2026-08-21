export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("token");

  const res = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(options.headers || {}),
    },
  });

  // ✅ ГЛАВНОЕ ПРАВИЛО
  if (res.status === 401) {
    localStorage.removeItem("token");

    // однократный редирект
    window.location.href = "/login";

    throw new Error("Unauthorized");
  }

  let data = {};

  try {
    data = await res.json();
  } catch {}

  if (!res.ok) {
    throw new Error(data.detail || "Ошибка запроса");
  }

  return data;
}