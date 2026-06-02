export default function TicketCard({ ticket }) {
  const statusColor = {
    NEW: "text-gray-500",
    ASSIGNED: "text-blue-600",
    IN_PROGRESS: "text-yellow-600",
    DONE: "text-green-600",
    CLOSED: "text-slate-400",
  };

  return (
    <div className="bg-white p-4 rounded shadow border">

      {/* HEADER */}
      <div className="flex justify-between items-center mb-1">
        <div className="font-semibold">
          {ticket.description || "Без описания"}
        </div>

        <div className={`text-sm font-medium ${statusColor[ticket.status]}`}>
          {ticket.status}
        </div>
      </div>

      {/* ✅ ОБОРУДОВАНИЕ */}
      {ticket.assets && (
        <div className="text-sm text-slate-500">
          {ticket.assets.name} — {ticket.assets.location}
        </div>
      )}

      {/* ДОП. */}
      <div className="text-xs text-slate-400 mt-1">
        #{ticket.id}
      </div>

    </div>
  );
}
