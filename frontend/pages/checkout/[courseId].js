import Link from "next/link";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";

import ProtectedRoute from "@/components/ProtectedRoute";
import api from "@/lib/api";

function CheckoutContent() {
  const router = useRouter();
  const { courseId } = router.query;
  const [course, setCourse] = useState(null);
  const [promoCode, setPromoCode] = useState("");
  const [status, setStatus] = useState("idle"); // idle | paying | done | error
  const [order, setOrder] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!courseId) return;
    api.get(`/courses/${courseId}/`).then(({ data }) => setCourse(data)).catch(() => {});
  }, [courseId]);

  const pay = async () => {
    setStatus("paying");
    setError("");
    try {
      const { data } = await api.post("/orders/", {
        course: courseId,
        promo_code: promoCode || undefined,
      });
      setOrder(data.order);
      if (data.checkout?.checkout_url) {
        window.location.href = data.checkout.checkout_url;
        return;
      }
      setStatus("done");
    } catch (err) {
      setError(err?.response?.data?.detail || "To'lovni amalga oshirishda xatolik yuz berdi.");
      setStatus("error");
    }
  };

  if (!course) return <p>Yuklanmoqda...</p>;

  if (status === "done" && order) {
    return (
      <div className="form-page">
        <h1>To&apos;lov muvaffaqiyatli</h1>
        <p className="muted">
          Buyurtma holati: <strong>{order.status}</strong>. Kursga yozildingiz — darslarni
          boshlashingiz mumkin.
        </p>
        <Link href={`/courses/${courseId}`} className="link-btn primary-link">
          Kursga o&apos;tish →
        </Link>
      </div>
    );
  }

  return (
    <div className="form-page">
      <h1>To&apos;lovni tasdiqlash</h1>
      <div className="module" style={{ marginBottom: 20 }}>
        <h3>{course.title}</h3>
        <p className="price">
          {Number(course.price) > 0 ? `${course.price} ${course.currency || "so'm"}` : "Bepul"}
        </p>
      </div>

      <div className="form">
        <label>
          Promokod (bo&apos;lsa)
          <input value={promoCode} onChange={(e) => setPromoCode(e.target.value)} placeholder="PROMO2026" />
        </label>
        {error && <p className="error">{error}</p>}
        <button onClick={pay} disabled={status === "paying"}>
          {status === "paying" ? "Yuborilmoqda..." : "To'lash va kursga yozilish"}
        </button>
        <p className="muted" style={{ fontSize: "0.85rem" }}>
          Demo rejimida to&apos;lov darhol tasdiqlanadi (real Payme integratsiyasi ulanmagan).
        </p>
      </div>
    </div>
  );
}

export default function CheckoutPage() {
  return (
    <ProtectedRoute>
      <CheckoutContent />
    </ProtectedRoute>
  );
}
