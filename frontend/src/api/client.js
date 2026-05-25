export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("token");

  const res = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
      Authorization: `Bearer ${token}`,
    },
  });

  
  if (res.status === 401) {
    console.log("❗ NOT AUTHORIZED");
    return { error: "unauthorized" };
  }

  const data = await res.json();

  return data;
}