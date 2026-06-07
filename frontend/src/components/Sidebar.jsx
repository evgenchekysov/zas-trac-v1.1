import { NavLink } from "react-router-dom";

export default function Sidebar() {
  const menu = [
    { label: "Заявки", path: "/work" },
    { label: "Диспетчерская", path: "/dispatcher" },
    { label: "Таймлайн", path: "/timeline" },
    { label: "Отчёты", path: "/reports" },
    { label: "Аналитика", path: "/analytics" },
    { label: "Настройки", path: "/settings" },
  ];

  const linkClass = ({ isActive }) =>
    `block px-4 py-2 rounded transition ${
      isActive
        ? "bg-slate-800 text-white"
        : "text-slate-300 hover:bg-slate-800 hover:text-white"
    }`;

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

      {/* NAV */}
      <nav className="space-y-2">
        {menu.map(item => (
          <NavLink key={item.path} to={item.path} className={linkClass}>
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* BACK */}
      <div className="mt-auto pt-6">
        <button
          onClick={() => window.history.back()}
          className="w-full text-left px-4 py-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded transition"
        >
          ← Назад
        </button>
      </div>

    </aside>
  );
}