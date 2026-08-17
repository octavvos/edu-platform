import Link from "next/link";
import { useEffect, useState } from "react";

import ProtectedRoute from "@/components/ProtectedRoute";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

function ModerationContent() {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/courses/", { params: { status: "moderation" } })
      .then(({ data }) => setCourses(data.results ?? data))
      .finally(() => setLoading(false));
  }, []);

  if (user && user.role !== "admin" && user.role !== "super_admin") {
    return <p className="error">Bu sahifaga faqat admin kirishi mumkin.</p>;
  }

  return (
    <div>
      <h1>Moderatsiya navbati</h1>
      {loading && <p>Yuklanmoqda...</p>}
      {!loading && courses.length === 0 && (
        <p className="muted">Moderatsiyaga yuborilgan kurslar yo&apos;q.</p>
      )}
      <ul className="list">
        {courses.map((c) => (
          <li key={c.id}>
            <Link href={`/dashboard/courses/${c.id}`}>{c.title}</Link>
            <span className="muted">{c.teacher_name}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function ModerationPage() {
  return (
    <ProtectedRoute>
      <ModerationContent />
    </ProtectedRoute>
  );
}
