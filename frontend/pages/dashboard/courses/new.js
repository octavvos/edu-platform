import { useRouter } from "next/router";
import { useState } from "react";

import ProtectedRoute from "@/components/ProtectedRoute";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

function NewCourseForm() {
  const router = useRouter();
  const { user } = useAuth();
  const [form, setForm] = useState({
    title: "",
    description: "",
    level: "beginner",
    price: 0,
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (user && user.role !== "teacher" && user.role !== "admin") {
    return <p className="error">Faqat o&apos;qituvchilar kurs yaratishi mumkin.</p>;
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const { data } = await api.post("/courses/", form);
      router.push(`/dashboard/courses/${data.id}`);
    } catch (err) {
      setError("Kurs yaratishda xatolik yuz berdi.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="form-page">
      <h1>Yangi kurs yaratish</h1>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Kurs nomi
          <input name="title" value={form.title} onChange={handleChange} required />
        </label>
        <label>
          Tavsif
          <textarea name="description" rows={4} value={form.description} onChange={handleChange} />
        </label>
        <label>
          Daraja
          <select name="level" value={form.level} onChange={handleChange}>
            <option value="beginner">Boshlang&apos;ich</option>
            <option value="intermediate">O&apos;rta</option>
            <option value="advanced">Yuqori</option>
          </select>
        </label>
        <label>
          Narxi (so&apos;m, bepul uchun 0)
          <input type="number" name="price" min="0" value={form.price} onChange={handleChange} />
        </label>
        <p className="muted">
          Kurs qoralama sifatida yaratiladi. Modul/dars qo&apos;shib bo&apos;lgach, uni
          moderatsiyaga yuborasiz.
        </p>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? "Yaratilmoqda..." : "Kursni yaratish"}
        </button>
      </form>
    </div>
  );
}

export default function NewCoursePage() {
  return (
    <ProtectedRoute>
      <NewCourseForm />
    </ProtectedRoute>
  );
}
