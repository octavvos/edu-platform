import Link from "next/link";
import { useRouter } from "next/router";
import { useState } from "react";

import { useAuth } from "@/context/AuthContext";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(username, password);
      router.push("/dashboard");
    } catch (err) {
      if (err.response) {
        setError("Login yoki parol noto'g'ri.");
      } else {
        setError("Serverga ulanib bo'lmadi. Backend ishlab turganini tekshiring.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="form-page">
      <h1>Kirish</h1>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} required />
        </label>
        <label>
          Parol
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? "Kirilmoqda..." : "Kirish"}
        </button>
      </form>
      <p className="muted">
        Akkountingiz yo&apos;qmi? <Link href="/register">Ro&apos;yxatdan o&apos;ting</Link>
      </p>
    </div>
  );
}
