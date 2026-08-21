import { useNavigate } from "react-router-dom";
import {
  joinTicket,
  startTicket,
  stopTicket
} from "../api/tickets";

export default function TicketCard({ ticket }) {
  const navigate = useNavigate();
  const status = ticket.status?.toUpperCase();
  const isParticipant = ticket.participants?.some(
  (p) => p.user_id === "<test_user_id>"
  );

  const statusColor = {
    NEW: "text-gray-500",
    ASSIGNED: "text-blue-600",
    IN_PROGRESS: "text-yellow-600",
    PAUSED: "text-orange-500",
    DONE: "text-green-600",
    CLOSED: "text-slate-400",
  };

  const handleClick = () => {
    console.log("CLICK CARD", ticket.id);
    navigate(`/tickets/${ticket.id}`);
  };

  const stop = (e) => e.stopPropagation();


  async function handleAction(fn, e) {
    e.stopPropagation();

    try {
      await fn(ticket.id);

      window.reloadDispatcher?.(); // ✅ ВОТ ЭТО КЛЮЧ
      window.reloadTickets?.();    // ✅ для /work

    } catch (e) {
      console.error(e);
    }
  }


  return (
    <div
      onClick={(e) => handleClick(e)}
      className="bg-white p-4 rounded shadow border cursor-pointer hover:bg-slate-50 transition"
    >

      {/* HEADER */}
      <div className="flex justify-between items-center mb-1">
        <div className="font-semibold">
          {ticket.description || "Без описания"}
        </div>

        <div className={`text-sm font-medium ${statusColor[status]}`}>
          {ticket.status}
        </div>
      </div>

      {/* ОБОРУДОВАНИЕ */}
      {ticket.assets && (
        <div className="text-sm text-slate-500">
          {ticket.assets.name} — {ticket.assets.location}
        </div>
      )}

      {/* ID */}
      <div className="text-xs text-slate-400 mt-1">
        #{ticket.id}
      </div>

      {/* ACTIONS */}
      <div className="mt-3 flex gap-2">

        {/* START */}
        {["NEW", "ASSIGNED", "PAUSED"].includes(status) && (
          <button onClick={(e) => handleAction(startTicket, e)} 
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded">
            Начать
          </button>
        )}

        {/* STOP */}
        {status === "IN_PROGRESS" && (
          <button onClick={(e) => handleAction(stopTicket, e)} 
          className="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded">
            Остановить
          </button>
        )}

        {/* JOIN */}
        {["IN_PROGRESS", "PAUSED"].includes(status) && !isParticipant && (
          <button onClick={(e) => handleAction(joinTicket, e)} 
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">
            Присоединиться
          </button>
        )}

      </div>
    </div>
  );
}
