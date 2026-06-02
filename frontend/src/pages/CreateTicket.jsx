import { useEffect, useState } from "react";

const API = "https://ominous-rotary-phone-jjxjxr7jv76jfg4x-8080.app.github.dev";

export default function CreateTicket() {
  const [description, setDescription] = useState("");
  const [assets, setAssets] = useState([]);
  const [assetQr, setAssetQr] = useState("");

  const [search, setSearch] = useState("");
  const [filtered, setFiltered] = useState([]);

  const [loading, setLoading] = useState(false);
  const [successData, setSuccessData] = useState(null);
  const [error, setError] = useState(null);

  // загрузка оборудования
  useEffect(() => {
    fetch(`${API}/api/assets`)
      .then(r => r.json())
      .then(setAssets)
      .catch(console.error);
  }, []);

  // умный поиск
  useEffect(() => {
    if (!search) {
      setFiltered([]);
      return;
    }

    const lower = search.toLowerCase();

    const result = assets.filter(a =>
      a.name.toLowerCase().includes(lower) ||
      a.location.toLowerCase().includes(lower)
    );

    setFiltered(result.slice(0, 8));
  }, [search, assets]);

  // создание
  async function handleSubmit() {
    setError(null);

    if (!assetQr) {
      setError("Выберите оборудование");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(`${API}/tickets/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          description: description || null,
          asset_qr: assetQr
        })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data?.error || "Ошибка сервера");
      }

      const selected = assets.find(a => a.qr_code === assetQr);

      setSuccessData({
        description,
        asset: selected,
        time: new Date()
      });

      setDescription("");
      setAssetQr("");
      setSearch("");

    } catch (e) {
      setError(e.message);
    }

    setLoading(false);
  }

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">

      <div className="bg-white w-full max-w-sm rounded-xl shadow p-5">

        {/* HEADER */}
        <div className="flex items-center justify-between mb-5">
          <button
            onClick={() => window.location.href = "/"}
            className="text-blue-600 text-sm"
          >
            ← Назад
          </button>

          <h1 className="text-lg font-semibold text-slate-700">
            Новая заявка
          </h1>

          <div />
        </div>

        {/* SUCCESS */}
        {successData && (
          <div className="bg-green-50 border border-green-200 text-green-800 p-4 rounded mb-4">
            <div className="font-semibold mb-2">
              ✅ Заявка создана
            </div>

            <div className="text-sm space-y-1">
              <div><b>Оборудование:</b> {successData.asset?.name}</div>
              <div><b>Описание:</b> {successData.description || "—"}</div>
              <div><b>Время:</b> {successData.time.toLocaleString("ru-RU")}</div>
            </div>

            <button
              onClick={() => window.location.href = "/"}
              className="mt-4 w-full bg-green-600 text-white py-2 rounded"
            >
              Закрыть
            </button>
          </div>
        )}

        {/* ERROR */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-2 rounded mb-3 text-sm">
            ❌ {error}
          </div>
        )}

        {/* FORM */}
        {!successData && (
          <div className="flex flex-col gap-3">

            {/* ПОИСК */}
            <div>
              <div className="text-sm text-slate-800 mb-1">
                Оборудование
              </div>

              <input
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setAssetQr("");
                }}
                placeholder="Начните вводить..."
                
                className="text-sm text-slate-800 mb-1 w-full p-3 border border-slate-800 rounded bg-white
                focus:outline-none focus:ring-2 focus:ring-blue-500"

              />

              {/* СПИСОК */}
              {filtered.length > 0 && (
                <div className="border rounded mt-1 bg-white shadow max-h-40 overflow-auto">

                  {filtered.map(a => (
                    <div
                      key={a.qr_code}
                      onClick={() => {
                        setAssetQr(a.qr_code);
                        setSearch(`${a.name} — ${a.location}`);
                        setFiltered([]);
                      }}
                      className="p-2 hover:bg-slate-100 cursor-pointer text-sm"
                    >
                      {a.name} — {a.location}
                    </div>
                  ))}

                </div>
              )}

              {/* выбран */}
              {assetQr && (
                <div className="text-xs text-green-600 mt-1">
                  ✅ выбрано
                </div>
              )}
            </div>

            {/* ОПИСАНИЕ */}
            <div>
              <div className="text-sm text-slate-800 mb-1">
                Описание
              </div>

              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                
                className="text-sm text-red-800 mb-1 w-full p-3 border border-slate-800 rounded bg-white
                 focus:outline-none focus:ring-2 focus:ring-blue-500"

                rows={4}
                placeholder="Опишите проблему..."
              />
            </div>

            {/* КНОПКА */}
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="mt-2 bg-blue-600 hover:bg-blue-500 text-white py-3 rounded font-semibold"
            >
              {loading ? "Создание..." : "Создать заявку"}
            </button>

          </div>
        )}

      </div>
    </div>
  );
}
