export default function TicketCard({ ticket }) {
  const statusColor = {
    NEW: "text-gray-500",
    ASSIGNED: "text-blue-600",
    IN_PROGRESS: "text-yellow-600",
    DONE: "text-green-600",
    CLOSED: "text-slate-400",
  };

  return (
    <div className="bg-white p-4 rounded shadow hover:shadow-md transition border">

      <div className="flex justify-between items-center">

        {/* У тебя description вместо title */}
        <div className="font-semibold">
          {ticket.description || "Без описания"}
        </div>

        <div className={`text-sm ${statusColor[ticket.status]}`}>
          {ticket.status}
        </div>

      </div>

    </div>
  );
}
