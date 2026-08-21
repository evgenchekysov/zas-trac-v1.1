import { useEffect, useState } from "react";
import { getTickets } from "../api/tickets";
import Layout from "../components/Layout";

export default function Dispatcher() {
  const [tickets, setTickets] = useState([]);
  const [selectedStatus, setSelectedStatus] = useState(null);

  // ✅ загрузка
  useEffect(() => {
    async function load() {
      const data = await getTickets();
      setTickets(data);
    }

    load();
    window.reloadDispatcher = load;
  }, []);

   //const filtered = tickets.filter(isInRange);
  const filtered = tickets;
  const visibleTickets = selectedStatus
  ? filtered.filter((t) => t.status === selectedStatus)
  : filtered;

  const stats = {
  NEW: filtered.filter(t => t.status === "NEW").length,
  ASSIGNED: filtered.filter(t => t.status === "ASSIGNED").length,
  IN_PROGRESS: filtered.filter(t => t.status === "IN_PROGRESS").length,
  PAUSED: filtered.filter(t => t.status === "PAUSED").length,
  DONE: filtered.filter(t => t.status === "DONE").length,
  };

  console.log(tickets[0]);
  
  const now = new Date();

  const archiveMonth = filtered.filter((t) => {
    if (t.status !== "CLOSED") return false;

    const d = new Date(t.closed_at || t.updated_at);

    return (
      d.getMonth() === now.getMonth() &&
      d.getFullYear() === now.getFullYear()
    );
  }).length;

  const archiveYear = filtered.filter((t) => {
    if (t.status !== "CLOSED") return false;

    const d = new Date(t.closed_at || t.updated_at);

    return d.getFullYear() === now.getFullYear();
  }).length;

  const archiveTotal = filtered.filter(
    (t) => t.status === "CLOSED"
  ).length;

  return (
    <Layout>

      <h1 className="text-2xl font-semibold text-slate-700 mb-4">
        ДИСПЕТЧЕРСКАЯ
      </h1>

      <div className="mb-4 flex items-center gap-3">

        <button
          onClick={() => setSelectedStatus(null)}
          className={`px-4 py-2 rounded font-medium transition
            ${
              selectedStatus === null
                ? "bg-slate-800 text-white"
                : "bg-slate-600 text-white hover:bg-slate-700"
            }`}
        >
          Все заявки
        </button>
        
      </div>

      <div className="grid grid-cols-5 gap-3 mb-6">

        <div
          onClick={() => setSelectedStatus("NEW")}
          className={`p-6 rounded-xl shadow text-center cursor-pointer transition
            ${
              selectedStatus === "NEW"
                ? "bg-slate-800 text-white ring-4 ring-slate-300"
                : "bg-white hover:bg-slate-50"
            }`}
        >
          <div className={`text-sm ${selectedStatus === "NEW" ? "text-white" : "text-slate-500"}`}>
            Новые
          </div>
          <div className="text-3xl font-bold">
            {stats.NEW}
          </div>
        </div>

        <div
          onClick={() => setSelectedStatus("ASSIGNED")}
          className={`p-6 rounded-xl shadow text-center cursor-pointer transition
            ${
              selectedStatus === "ASSIGNED"
                ? "bg-slate-800 text-white ring-4 ring-slate-300"
                : "bg-white hover:bg-slate-50"
            }`}
        >
          <div className={`text-sm ${selectedStatus === "ASSIGNED" ? "text-white" : "text-slate-500"}`}>
            Назначены
          </div>
          <div className="text-3xl font-bold">
            {stats.ASSIGNED}
          </div>
        </div>

        <div
          onClick={() => setSelectedStatus("IN_PROGRESS")}
          className={`p-6 rounded-xl shadow text-center cursor-pointer transition
            ${
              selectedStatus === "IN_PROGRESS"
                ? "bg-slate-800 text-white ring-4 ring-slate-300"
                : "bg-white hover:bg-slate-50"
            }`}
        >
          <div className={`text-sm ${selectedStatus === "IN_PROGRESS" ? "text-white" : "text-slate-500"}`}>
            В работе
          </div>
          <div className="text-3xl font-bold">
            {stats.IN_PROGRESS}
          </div>
        </div>

        <div
          onClick={() => setSelectedStatus("PAUSED")}
          className={`p-6 rounded-xl shadow text-center cursor-pointer transition
            ${
              selectedStatus === "PAUSED"
                ? "bg-slate-800 text-white ring-4 ring-slate-300"
                : "bg-white hover:bg-slate-50"
            }`}
        >
          <div className={`text-sm ${selectedStatus === "PAUSED" ? "text-white" : "text-slate-500"}`}>
            Пауза
          </div>
          <div className="text-3xl font-bold">
            {stats.PAUSED}
          </div>
        </div>

        <div
          onClick={() => setSelectedStatus("DONE")}
          className={`p-6 rounded-xl shadow text-center cursor-pointer transition
            ${
              selectedStatus === "DONE"
                ? "bg-slate-800 text-white ring-4 ring-slate-300"
                : "bg-white hover:bg-slate-50"
            }`}
        >
          <div className={`text-sm ${selectedStatus === "DONE" ? "text-white" : "text-slate-500"}`}>
            Выполнено
          </div>
          <div className="text-3xl font-bold">
            {stats.DONE}
          </div>
        </div>

      </div>

      {/* СПИСОК ЗАЯВОК */}
      {visibleTickets.length === 0 ? (
        <div className="text-center text-slate-500">
          Нет заявок
        </div>
      ) : (
        <div className="space-y-3">

          {visibleTickets.map((t) => (
            <div
              key={t.id}
              className="bg-white p-4 rounded shadow flex justify-between"
            >
              <div>

                <div className="font-bold">
                  #{t.id}
                </div>

                <div className="text-sm text-slate-500">
                  {t.description || "Без описания"}
                </div>

                {t.assets && (
                  <div className="text-sm text-slate-500">
                    {t.assets.name} — {t.assets.location}
                  </div>
                )}

                <div className="text-xs mt-1 text-blue-500">
                  {t.status}
                </div>

              </div>
            </div>
          ))}

        </div>
      )}

    </Layout>
  );
}
