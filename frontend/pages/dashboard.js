import Link from "next/link";
import { useEffect, useState } from "react";

import ProtectedRoute from "@/components/ProtectedRoute";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

function DashboardContent() {
  const { user } = useAuth();
  const [enrollments, setEnrollments] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;

    if (user.role === "teacher") {
      api
        .get("/courses/", { params: { teacher: user.id } })
        .then(({ data }) => setCourses(data.results ?? data))
        .finally(() => setLoading(false));
    } else {
      api
        .get("/enrollments/")
        .then(({ data }) => setEnrollments(data.results ?? data))
        .finally(() => setLoading(false));
    }
  }, [user]);

  return (
    <div>
      <h1>Dashboard</h1>
      <p className="muted">
        Xush kelibsiz, {user.first_name || user.username} ({user.role})
      </p>

      {loading && <p>Yuklanmoqda...</p>}

      {!loading && user.role === "teacher" && (
        <section>
          <div className="manage-header">
            <h2>Mening kurslarim</h2>
            <Link href="/dashboard/courses/new" className="link-btn primary-link">
              + Yangi kurs yaratish
            </Link>
          </div>
          {courses.length === 0 && <p className="muted">Siz hali kurs yaratmagansiz.</p>}
          <ul className="list">
            {courses.map((c) => (
              <li key={c.id}>
                <Link href={`/dashboard/courses/${c.id}`}>{c.title}</Link> —{" "}
                {{
                  draft: "Qoralama",
                  moderation: "Moderatsiyada",
                  published: "Nashr etilgan",
                  rejected: "Rad etilgan",
                }[c.status] || c.status}
              </li>
            ))}
          </ul>
        </section>
      )}

      {!loading && user.role !== "teacher" && (
        <section>
          <h2>Mening kurslarim</h2>
          {enrollments.length === 0 && <p className="muted">Siz hali hech qaysi kursga yozilmagansiz.</p>}
          <ul className="list">
            {enrollments.map((e) => (
              <li key={e.id}>
                {e.course_title} — {e.progress_percent}% ({e.status})
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
