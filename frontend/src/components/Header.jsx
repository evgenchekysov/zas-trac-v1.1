import { useNavigate } from "react-router-dom";

export default function Header() {
  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/login");
  }

  return (
    <header className="bg-white shadow-sm px-6 h-16 flex items-center justify-between">

      {/* логотип / переход */}
      <div
        onClick={() => navigate("/")}
        className="text-lg font-semibold text-slate-700 cursor-pointer"
      >
        ZAS‑TRAC
      </div>

      <div className="flex items-center gap-6">

        {/* ✅ новая кнопка */}
        <button
          onClick={() => navigate("/create")}
          className="bg-blue-600 text-white px-3 py-1 rounded"
        >
          + Заявка
        </button>

        {/* логотип */}
        <img
          src="/assets/henkel.svg"
          className="h-8 opacity-80"
          alt="Henkel"
        />

        {/* выход */}
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-3 py-1 rounded"
        >
          Выход
        </button>

      </div>
    </header>
  );
}