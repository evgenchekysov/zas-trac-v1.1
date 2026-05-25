import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {

  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      navigate("/dispatcher");
    }
  }, []);

  async function handleLogin() {
    const res = await fetch(
      `${import.meta.env.VITE_SUPABASE_URL}/auth/v1/token?grant_type=password`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          apikey: import.meta.env.VITE_SUPABASE_ANON_KEY,
        },
        body: JSON.stringify({ email, password }),
      }
    );

    const data = await res.json();

    if (data.access_token) {
      localStorage.setItem("token", data.access_token);
      navigate("/dispatcher");
    } else {
      alert("Ошибка входа");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">

      <div className="bg-white p-8 rounded-xl shadow-md w-96 text-center">

        <img
          src="/assets/henkel.svg"
          className="mx-auto mb-6 h-10 object-contain"
        />

        <h1 className="text-2xl font-semibold mb-6 text-slate-800">
          Вход в ZAS‑TRAC
        </h1>

        <input
          type="email"
          placeholder="Email"
          className="w-full mb-3 p-2 border border-slate-300 rounded"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Пароль"
          className="w-full mb-5 p-2 border border-slate-300 rounded"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          onClick={handleLogin}
          className="w-full bg-blue-600 text-white py-2 rounded"
        >
          Войти
        </button>

      </div>
    </div>
  );
}
