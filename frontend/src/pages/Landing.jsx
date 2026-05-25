export default function Landing() {
  const token = localStorage.getItem("token");

  function handleLogin() {
    if (token) {
      window.location.href = "/dispatcher";
    } else {
      window.location.href = "/login";
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center">

      <div className="bg-white p-10 rounded-xl shadow-md w-[420px]">

        {/* LOGO */}
        <div className="flex justify-center mb-6">
          <img
            src="/assets/henkel.svg"
            className="h-10"
          />
        </div>

        {/* TITLE */}
        <h1 className="text-2xl font-semibold text-slate-700 text-center mb-8">
          ZAS‑TRAC
        </h1>

        {/* ACTIONS */}
        <div className="flex flex-col gap-4">

          {/* CREATE BUTTON */}
          <button
            className="bg-blue-600 hover:bg-blue-500 transition
                       text-white py-3 rounded font-semibold"
            onClick={() => window.location.href = "/create"}
          >
            Создать заявку
          </button>

          {/* LOGIN BUTTON */}
          <button
            className="bg-slate-300 hover:bg-slate-400 transition
                       text-slate-800 py-3 rounded"
            onClick={handleLogin}
          >
            Войти
          </button>

        </div>

      </div>

    </div>
  );
}