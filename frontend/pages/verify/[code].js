import { useRouter } from "next/router";
import { useEffect, useState } from "react";

import api from "@/lib/api";

export default function VerifyCertificatePage() {
  const router = useRouter();
  const { code } = router.query;
  const [certificate, setCertificate] = useState(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!code) return;
    api
      .get(`/verify/${code}/`)
      .then(({ data }) => setCertificate(data))
      .catch(() => setNotFound(true));
  }, [code]);

  return (
    <div className="form-page">
      <h1>Sertifikatni tekshirish</h1>

      {!certificate && !notFound && <p>Tekshirilmoqda...</p>}

      {notFound && (
        <div className="module">
          <p className="error">Bu kod bo&apos;yicha sertifikat topilmadi.</p>
          <p className="muted">Kodni qayta tekshiring: {code}</p>
        </div>
      )}

      {certificate && (
        <div className="module">
          <span className="badge free-badge">Haqiqiy sertifikat</span>
          <h3 style={{ marginTop: 12 }}>{certificate.course_title}</h3>
          <p>
            <strong>{certificate.student_name}</strong> ushbu kursni muvaffaqiyatli yakunladi.
          </p>
          <p className="muted">O&apos;qituvchi: {certificate.teacher_name}</p>
          <p className="muted">
            Berilgan sana: {new Date(certificate.issued_at).toLocaleDateString("uz-UZ")}
          </p>
          <p className="muted">Kod: {certificate.code}</p>
        </div>
      )}
    </div>
  );
}
