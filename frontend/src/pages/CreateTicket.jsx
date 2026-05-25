import { useState } from "react";

export default function CreateTicket() {
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    setLoading(true);

    try {
      await fetch("/tickets/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          description: description || null
        }),
      });

      // ✅ после создания → назад на landing
      window.location.href = "/";

    } catch (err) {
      console.error(err);
      alert("Ошибка создания заявки");
    }

    setLoading(false);
  }

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center">

      <div className="bg-white p-10 rounded-xl shadow-md w-[420px]">

        {/* LOGO */}
        <div className="flex justify-center mb-6">
          <img src="/assets/henkel.svg" className="h-10" />
        </div>

        {/* TITLE */}
        <h1 className="text-xl font-semibold text-slate-700 text-center mb-6">
          Создание заявки
        </h1>

        {/* FORM */}
        <div className="flex flex-col gap-4">

          <textarea
            placeholder="Описание неисправности..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="bg-slate-200 p-3 rounded resize-none"
            rows={4}
          />

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-500 transition
                       text-white py-3 rounded font-semibold"
          >
            {loading ? "Создание..." : "Создать заявку"}
          </button>

          <button
            onClick={() => window.location.href = "/"}
            className="text-slate-500 text-sm"
          >
            Назад
          </button>

        </div>

      </div>

    </div>
  );
}
