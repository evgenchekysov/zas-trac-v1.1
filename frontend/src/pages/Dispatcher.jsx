import { useEffect, useState } from "react";
import { getTickets } from "../api/tickets";
import Layout from "../components/Layout";

export default function Dispatcher() {
  const [tickets, setTickets] = useState([]);

  useEffect(() => {
    async function load() {
      const data = await getTickets();

      if (data?.error === "unauthorized") {
        window.location.href = "/login";
        return;
      }

      if (Array.isArray(data)) {
        setTickets(data);
      }
    }

    load();
  }, []);

  return (
    <Layout>

      <h1 className="text-2xl font-semibold text-slate-700 mb-6">
        ДИСПЕТЧЕРСКАЯ
      </h1>

      {tickets.length === 0 ? (
        <div className="text-center text-slate-500">
          Нет заявок
        </div>
      ) : (
        <div className="space-y-3">
          {tickets.map((t) => (
            <div
              key={t.id}
              className="bg-white p-4 rounded shadow flex justify-between"
            >
              <div>
                <div className="font-bold">#{t.id}</div>

                <div className="text-sm text-slate-500">
                  {t.description || "Без описания"}
                </div>

                <div className="text-xs mt-1 text-blue-500">
                  {t.status}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button className="bg-blue-500 text-white px-2 rounded">
                  START
                </button>

                <button className="bg-green-600 text-white px-2 rounded">
                  DONE
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

    </Layout>
  );
}
