import { useRouter } from "next/router";
import { useState } from "react";

import { useAuth } from "@/context/AuthContext";

export default function OtpVerifyPage() {
  const router = useRouter();
  const { phone: phoneFromQuery } = router.query;
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { verifyOtp, requestOtp } = useAuth();

  const activePhone = phone || phoneFromQuery || "";

  const handleResend = async () => {
    setError("");
    setInfo("");
    try {
      const data = await requestOtp(activePhone, "register");
      setInfo(data.code ? `Kod (test): ${data.code}` : "OTP kod qayta yuborildi.");
    } catch {
      setError("OTP kodni yuborishda xatolik.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await verifyOtp(activePhone, code, "register");
      router.push("/dashboard");
    } catch {
      setError("OTP kod noto'g'ri yoki muddati o'tgan.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="form-page">
      <h1>Telefon raqamni tasdiqlash</h1>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Telefon
          <input
            value={activePhone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+998901234567"
            required
          />
        </label>
        <label>
          OTP kod
          <input value={code} onChange={(e) => setCode(e.target.value)} required />
        </label>
        {error && <p className="error">{error}</p>}
        {info && <p className="muted">{info}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? "Tekshirilmoqda..." : "Tasdiqlash"}
        </button>
        <button type="button" className="secondary" onClick={handleResend}>
          Kodni qayta yuborish
        </button>
      </form>
    </div>
  );
}
