import Link from "next/link";
import { useEffect, useState } from "react";

import ProtectedRoute from "@/components/ProtectedRoute";
import api from "@/lib/api";

function CertificatesContent() {
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/certificates/")
      .then(({ data }) => setCertificates(data.results ?? data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1>Sertifikatlarim</h1>
      {loading && <p>Yuklanmoqda...</p>}
      {!loading && certificates.length === 0 && (
        <p className="muted">Hali sertifikatingiz yo&apos;q. Kursni 100% yakunlaganingizdan so&apos;ng bu yerda paydo bo&apos;ladi.</p>
      )}
      <div className="modules">
        {certificates.map((c) => (
          <div key={c.id} className="module">
            <h3>{c.course_title}</h3>
            <p className="muted">
              Kod: <strong>{c.code}</strong> — berilgan sana: {new Date(c.issued_at).toLocaleDateString("uz-UZ")}
            </p>
            <Link href={`/verify/${c.code}`} className="link-btn primary-link">
              Tekshirish sahifasini ko&apos;rish →
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function CertificatesPage() {
  return (
    <ProtectedRoute>
      <CertificatesContent />
    </ProtectedRoute>
  );
}
