export default function UserBlock() {
  // ⚠️ DEV временно
  const user = localStorage.getItem("user") || "dev_user";

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 rounded">

      {/* иконка */}
      <div className="w-6 h-6 bg-slate-400 rounded-full" />

      {/* имя */}
      <span className="text-sm text-slate-700">
        {user}
      </span>

    </div>
  );
}