import { useNavigate } from "react-router-dom";
import UserBlock from "./UserBlock";

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
        className="text-lg font-semibold text-slate-700 cursor-pointer flex items-center gap-4"
      >
        <span>ZAS‑TRAC</span>

        <div className="h-4 w-px bg-slate-300" />

        <UserBlock />
      </div>


       <div className="flex items-center gap-6">

        <button
          onClick={() => navigate("/create")}
          className="bg-blue-600 text-white px-3 py-1 rounded"
        >
          Новая заявка
        </button>

        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-3 py-1 rounded"
        >
          Выход
        </button>

        <img
          src="/assets/henkel.svg"
          className="h-10 opacity-80"
          alt="Henkel"
        />

      </div>

    </header>
  );
}