import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import Layout from "../components/Layout";

import {
  startTicket,
  stopTicket,  
  getTicket,
  doneTicket,
  closeTicket
} from "../api/tickets";

export default function TicketPage() {
  const { id } = useParams();

  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(false);

  async function loadTicket() {
    const data = await getTicket(id);
    setTicket(data);
  }
    
    useEffect(() => {
      loadTicket();
      window.reloadTicket = loadTicket;
    }, [id]);

  async function handleAction(fn) {
    try {
      await fn(id);
      await loadTicket();
    } catch (e) {
      console.error(e);

      const msg = e.message || "";

      if (msg.includes("active work session")) {
        alert("Нельзя завершить заявку: нет активной работы");
      } else if (msg.includes("not participant")) {
        alert("Вы не участвуете в заявке");
      } else {
        alert("Ошибка действия");
      }
    }
  }


  if (!ticket) {
    return (
      <Layout>
        <div className="p-4">Загрузка...</div>
      </Layout>
    );
  }
  
  const statusLabels = {
    NEW: "Новая",
    ASSIGNED: "Назначена",
    IN_PROGRESS: "В работе",
    PAUSED: "Приостановлена",
    DONE: "Завершена",
    CLOSED: "Закрыта",
  };

  
  const statusColors = {
    NEW: "text-red-500",
    ASSIGNED: "text-blue-600",
    IN_PROGRESS: "text-yellow-600",
    PAUSED: "text-orange-500",
    DONE: "text-green-600",
    CLOSED: "text-slate-400",
  };

  return (
    <Layout>
      <div className="p-4 max-w-xl space-y-4">

        {/* НОМЕР */}
        <div className="text-xl font-semibold">
          Заявка №{ticket.id}
        </div>

        {/* СТАТУС */}
        <div>
          <b>Статус:</b> {statusLabels[ticket.status?.toUpperCase()] || ticket.status}
        </div>

        {/* ОБОРУДОВАНИЕ */}
        <div>
          <b>Оборудование:</b>{" "}
          {ticket.assets
            ? `${ticket.assets.name} — ${ticket.assets.location}`
            : "—"}
        </div>

        {/* ОПИСАНИЕ */}
        <div>
          <b>Описание:</b>
          <div className="mt-1 p-3 bg-white rounded border">
            {ticket.description || "—"}
          </div>
        </div>

        {/* КНОПКИ */}
        <div className="pt-4 flex gap-2">

          {["NEW", "ASSIGNED", "PAUSED"].includes(ticket.status) && (
            <button
              onClick={() => handleAction(startTicket)}
              className="bg-green-600 text-white px-4 py-2 rounded"
            >
              НАЧАТЬ
            </button>
          )}

          {ticket.status === "IN_PROGRESS" && (
            <>
              <button
                onClick={() => handleAction(stopTicket)}
                className="bg-yellow-500 text-white px-4 py-2 rounded"
              >
                СТОП
              </button>

              <button
                onClick={() => handleAction(doneTicket)}
                className="bg-purple-600 text-white px-4 py-2 rounded"
              >
                ЗАВЕРШИТЬ
              </button>
            </>
          )}

          {ticket.status === "DONE" && (
            <button
              onClick={() => handleAction(closeTicket)}
              className="bg-black text-white px-4 py-2 rounded"
            >
              ЗАКРЫТЬ
            </button>
          )}

        </div>

      </div>
    </Layout>
  );
}