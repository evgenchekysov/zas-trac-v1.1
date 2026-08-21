import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import TicketCard from "../components/TicketCard";

export default function Work() {
  const [tickets, setTickets] = useState([]);

  const currentUserId = "<test_user_id>";

  // ✅ ОТДЕЛЬНАЯ ФУНКЦИЯ ЗАГРУЗКИ
  async function loadTickets() {
    const token = localStorage.getItem("token");

    try {
      const res = await fetch("/tickets/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json();

      if (Array.isArray(data)) {
        setTickets(data);
      } else {
        setTickets([]);
      }
    } catch {
      setTickets([]);
    }
  }

  // ✅ AUTO REFRESH
  useEffect(() => {
    loadTickets();

    const interval = setInterval(() => {
      loadTickets();
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  // ✅ helpers

  const isParticipant = (ticket) =>
    ticket.participants?.some((p) => p.user_id === currentUserId);

  const statusOrder = {
    IN_PROGRESS: 1,
    PAUSED: 2,
    ASSIGNED: 3,
  };

  const sortByStatus = (a, b) =>
    (statusOrder[a.status] || 99) - (statusOrder[b.status] || 99);

  const emergency = tickets.filter((t) => t.priority === "EMERGENCY");

  const rest = tickets.filter((t) => t.priority !== "EMERGENCY");

  const myTickets = rest
    .filter((t) => isParticipant(t))
    .sort(sortByStatus);

  const newTickets = rest.filter((t) => t.status === "NEW");

  const availableTickets = rest.filter(
    (t) =>
      !isParticipant(t) &&
      ["ASSIGNED", "IN_PROGRESS", "PAUSED"].includes(t.status)
  );

  // ✅ UI

  return (
    <Layout title="Заявки">
      <div className="space-y-6">

        {/* 🚨 СРОЧНО */}
        {emergency.length > 0 && (
          <section>
            <h2 className="text-lg font-bold text-red-600 mb-2">
              🚨 Срочно ({emergency.length})
            </h2>

            <div className="space-y-2">
              {emergency.map((t) => (
                <TicketCard key={t.id} ticket={t} />
              ))}
            </div>
          </section>
        )}

        {/* 👤 МОИ */}
        <section>
          <h2 className="text-lg font-semibold mb-2">
            Мои заявки ({myTickets.length})
          </h2>

          {myTickets.length === 0 && (
            <div className="text-slate-400">
              Вы не участвуете ни в одной заявке
            </div>
          )}

          <div className="space-y-2">
            {myTickets.map((t) => (
              <TicketCard key={t.id} ticket={t} />
            ))}
          </div>
        </section>

        {/* 🆕 НОВЫЕ */}
        <section>
          <h2 className="text-lg font-semibold mb-2">
            Новые ({newTickets.length})
          </h2>

          {newTickets.length === 0 && (
            <div className="text-slate-400">
              Нет новых заявок
            </div>
          )}

          <div className="space-y-2">
            {newTickets.map((t) => (
              <TicketCard key={t.id} ticket={t} />
            ))}
          </div>
        </section>

        {/* 📂 ДОСТУПНЫЕ */}
        <section>
          <h2 className="text-lg font-semibold mb-2">
            Доступные ({availableTickets.length})
          </h2>

          {availableTickets.length === 0 && (
            <div className="text-slate-400">
              Нет доступных заявок
            </div>
          )}

          <div className="space-y-2">
            {availableTickets.map((t) => (
              <TicketCard key={t.id} ticket={t} />
            ))}
          </div>
        </section>

      </div>
    </Layout>
  );
}