import { useNavigate } from "react-router-dom";

export default function Header() {
  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/login");
  }

  return (
    <header className="bg-white shadow-sm px-6 h-16 flex items-center justify-between">

      <div className="text-lg font-semibold text-slate-700">
        ZAS‑TRAC
      </div>

      <div className="flex items-center gap-6">

        
        <img
        src="/assets/henkel.svg"
        className="h-8 opacity-80"
        alt="Henkel"
        />


        <button
          onClick={handleLogout}
          className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded"
        >
          Выход
        </button>

      </div>
    </header>
  );
}
