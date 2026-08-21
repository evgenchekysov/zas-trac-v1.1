import { apiFetch } from "./client";

export async function getTickets() {
  return apiFetch("/tickets/");
}

export async function joinTicket(id) {
  return apiFetch(`/tickets/${id}/join`, {
    method: "POST",
  });
}

export async function startTicket(id) {
  return apiFetch(`/tickets/${id}/start`, {
    method: "POST",
  });
}

export async function stopTicket(id) {
  return apiFetch(`/tickets/${id}/stop`, {
    method: "POST",
  });
}

// ✅ ДЕНЬ 13
export async function doneTicket(id) {
  return apiFetch(`/tickets/${id}/done`, {
    method: "POST",
  });
}

export async function closeTicket(id) {
  return apiFetch(`/tickets/${id}/close`, {
    method: "POST",
  });
}

export async function getTicket(id) {
  return apiFetch(`/tickets/${id}`);
}