import { NavLink } from "react-router-dom";

export default function Sidebar() {
  return (
    <aside className="bg-slate-900 text-white w-64 min-h-screen p-6 flex flex-col">

      {/* LOGO */}
      <div className="mb-10 flex items-center gap-3">
        <img
          src="/assets/zas-trac_icon_ZT_v1.svg"
          className="h-10 w-10 object-contain brightness-0 invert opacity-90"
        />
        <span className="text-lg tracking-wide text-slate-300">
          ZAS‑TRAC
        </span>
      </div>

      {/* NAVIGATION */}
      <nav className="space-y-2">

        <NavLink
          to="/dispatcher"
          className={({ isActive }) =>
            `block px-4 py-2 rounded transition ${
              isActive
                ? "bg-slate-800 text-white"
                : "text-slate-300 hover:bg-slate-800 hover:text-white"
            }`
          }
        >
          Диспетчер
        </NavLink>

        <NavLink
          to="/my-tickets"
          className={({ isActive }) =>
            `block px-4 py-2 rounded transition ${
              isActive
                ? "bg-slate-800 text-white"
                : "text-slate-300 hover:bg-slate-800 hover:text-white"
            }`
          }
        >
          Мои заявки
        </NavLink>

      </nav>

      {/* FOOTER (опционально) */}
      <div className="mt-auto text-xs text-slate-500 pt-6">
        v0.1 ZAS‑TRAC
      </div>

    </aside>
  );
}