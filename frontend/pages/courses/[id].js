import Link from "next/link";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";

import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

export default function CourseDetailPage() {
  const router = useRouter();
  const { id } = router.query;
  const { user } = useAuth();
  const [course, setCourse] = useState(null);
  const [error, setError] = useState("");
  const [enrolling, setEnrolling] = useState(false);
  const [enrolled, setEnrolled] = useState(false);

  useEffect(() => {
    if (!id) return;
    api
      .get(`/courses/${id}/`)
      .then(({ data }) => setCourse(data))
      .catch(() => setError("Kursni yuklashda xatolik yuz berdi."));
  }, [id]);

  useEffect(() => {
    if (!id || !user) return;
    api
      .get("/enrollments/", { params: { course: id } })
      .then(({ data }) => {
        const list = data.results ?? data;
        setEnrolled(list.length > 0);
      })
      .catch(() => {});
  }, [id, user]);

  const isOwner = user && course && course.teacher === user.id;
  const canAccessAllLessons = enrolled || isOwner || user?.role === "admin";

  const handleEnroll = async () => {
    if (!user) {
      router.push("/login");
      return;
    }
    setEnrolling(true);
    try {
      await api.post("/enrollments/", { course: id });
      setEnrolled(true);
    } catch {
      setError("Kursga yozilishda xatolik yuz berdi.");
    } finally {
      setEnrolling(false);
    }
  };

  if (error) return <p className="error">{error}</p>;
  if (!course) return <p>Yuklanmoqda...</p>;

  return (
    <div>
      <h1>{course.title}</h1>
      <p className="muted">{course.teacher_name}</p>
      <p>{course.description}</p>
      <div className="course-card-meta">
        <span className="badge">{course.level}</span>
        <span className="price">
          {Number(course.price) > 0 ? `${course.price} so'm` : "Bepul"}
        </span>
      </div>

      {!isOwner && (
        <button onClick={handleEnroll} disabled={enrolling || enrolled}>
          {enrolled ? "Yozildingiz" : enrolling ? "Yuborilmoqda..." : "Kursga yozilish"}
        </button>
      )}
      {isOwner && (
        <Link href={`/dashboard/courses/${id}`} className="link-btn">
          Kursni boshqarish
        </Link>
      )}

      <h2>Kurs dasturi</h2>
      {course.modules?.length === 0 && <p className="muted">Modullar hali qo&apos;shilmagan.</p>}
      <div className="modules">
        {course.modules?.map((m) => (
          <div key={m.id} className="module">
            <h3>{m.title}</h3>
            <ul className="list">
              {m.lessons.map((l) => {
                const locked = !l.is_free_preview && !canAccessAllLessons;
                return (
                  <li key={l.id} className={locked ? "lesson-locked" : ""}>
                    {locked ? (
                      <span>
                        🔒 {l.title} <span className="muted">({l.duration_minutes} daq)</span>
                      </span>
                    ) : (
                      <Link href={`/courses/${id}/lessons/${l.id}`}>
                        {l.title} <span className="muted">({l.duration_minutes} daq)</span>
                      </Link>
                    )}
                    {l.is_free_preview && <span className="badge free-badge">Bepul</span>}
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
