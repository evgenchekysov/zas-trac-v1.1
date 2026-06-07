import { useNavigate } from "react-router-dom";

export default function TicketCard({ ticket }) {
  const navigate = useNavigate();

  const statusColor = {
    NEW: "text-gray-500",
    ASSIGNED: "text-blue-600",
    IN_PROGRESS: "text-yellow-600",
    PAUSED: "text-orange-500",
    DONE: "text-green-600",
    CLOSED: "text-slate-400",
  };

  const handleClick = () => {
    navigate(`/tickets/${ticket.id}`);
  };

  const stop = (e) => e.stopPropagation();

  return (
    <div
      onClick={handleClick}
      className="bg-white p-4 rounded shadow border cursor-pointer hover:bg-slate-50 transition"
    >

      {/* HEADER */}
      <div className="flex justify-between items-center mb-1">
        <div className="font-semibold">
          {ticket.description || "Без описания"}
        </div>

        <div className={`text-sm font-medium ${statusColor[ticket.status]}`}>
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

        {/* NEW → JOIN */}
        {ticket.status === "NEW" && (
          <button
            onClick={(e) => {
              stop(e);
              console.log("JOIN", ticket.id);
            }}
            className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
          >
            Присоединиться
          </button>
        )}

        {/* ASSIGNED / PAUSED → START */}
        {["ASSIGNED", "PAUSED"].includes(ticket.status) && (
          <button
            onClick={(e) => {
              stop(e);
              console.log("START", ticket.id);
            }}
            className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
          >
            Начать
          </button>
        )}

        {/* IN_PROGRESS → STOP */}
        {ticket.status === "IN_PROGRESS" && (
          <button
            onClick={(e) => {
              stop(e);
              console.log("STOP", ticket.id);
            }}
            className="bg-yellow-500 text-white px-3 py-1 rounded text-sm hover:bg-yellow-600"
          >
            Остановить
          </button>
        )}

      </div>
    </div>
  );
}