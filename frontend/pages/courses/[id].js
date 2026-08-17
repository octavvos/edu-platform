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

      <button onClick={handleEnroll} disabled={enrolling || enrolled}>
        {enrolled ? "Yozildingiz" : enrolling ? "Yuborilmoqda..." : "Kursga yozilish"}
      </button>

      <h2>Kurs dasturi</h2>
      {course.modules?.length === 0 && <p className="muted">Modullar hali qo&apos;shilmagan.</p>}
      <div className="modules">
        {course.modules?.map((m) => (
          <div key={m.id} className="module">
            <h3>{m.title}</h3>
            <p className="muted">{m.lessons_count} dars</p>
          </div>
        ))}
      </div>
    </div>
  );
}
