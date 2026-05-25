import { apiFetch } from "./client";

export async function getTickets() {
  return apiFetch("/tickets/");
}
