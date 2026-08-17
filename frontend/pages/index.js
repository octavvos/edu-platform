import { useEffect, useState } from "react";

import CourseCard from "@/components/CourseCard";
import api from "@/lib/api";

export default function CatalogPage() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/courses/", { params: { is_published: true } })
      .then(({ data }) => setCourses(data.results ?? data))
      .catch(() => setError("Kurslarni yuklashda xatolik yuz berdi."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1>Kurslar katalogi</h1>
      {loading && <p>Yuklanmoqda...</p>}
      {error && <p className="error">{error}</p>}
      <div className="grid">
        {courses.map((course) => (
          <CourseCard key={course.id} course={course} />
        ))}
      </div>
      {!loading && courses.length === 0 && <p className="muted">Hozircha kurslar mavjud emas.</p>}
    </div>
  );
}
