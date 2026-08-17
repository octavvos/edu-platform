import { useRouter } from "next/router";
import { useState } from "react";

import { useAuth } from "@/context/AuthContext";

export default function RegisterPage() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    phone: "",
    role: "student",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await register(form);
      router.push(`/otp-verify?phone=${encodeURIComponent(form.phone)}`);
    } catch (err) {
      const data = err?.response?.data;
      setError(data ? JSON.stringify(data) : "Ro'yxatdan o'tishda xatolik yuz berdi.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="form-page">
      <h1>Ro&apos;yxatdan o&apos;tish</h1>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Username
          <input name="username" value={form.username} onChange={handleChange} required />
        </label>
        <label>
          Email
          <input type="email" name="email" value={form.email} onChange={handleChange} required />
        </label>
        <label>
          Telefon (+998...)
          <input name="phone" value={form.phone} onChange={handleChange} required />
        </label>
        <label>
          Parol
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Rol
          <select name="role" value={form.role} onChange={handleChange}>
            <option value="student">Student</option>
            <option value="teacher">Teacher</option>
          </select>
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? "Yuborilmoqda..." : "Ro'yxatdan o'tish"}
        </button>
      </form>
    </div>
  );
}
