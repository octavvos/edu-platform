import Link from "next/link";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";

import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

function toEmbedUrl(url) {
  if (!url) return null;
  const ytMatch = url.match(/(?:youtu\.be\/|youtube\.com\/watch\?v=|youtube\.com\/embed\/)([\w-]+)/);
  if (ytMatch) return `https://www.youtube.com/embed/${ytMatch[1]}`;
  return url;
}

export default function LessonViewPage() {
  const router = useRouter();
  const { id: courseId, lessonId } = router.query;
  const { user, loading: authLoading } = useAuth();
  const [lesson, setLesson] = useState(null);
  const [course, setCourse] = useState(null);
  const [status, setStatus] = useState("loading"); // loading | ok | forbidden | notfound

  useEffect(() => {
    if (!lessonId || authLoading) return;

    api
      .get(`/lessons/${lessonId}/`)
      .then(({ data }) => {
        setLesson(data);
        setStatus("ok");
      })
      .catch((err) => {
        setStatus(err?.response?.status === 404 ? "forbidden" : "notfound");
      });

    if (courseId) {
      api.get(`/courses/${courseId}/`).then(({ data }) => setCourse(data)).catch(() => {});
    }
  }, [lessonId, courseId, authLoading]);

  if (status === "loading") return <p>Yuklanmoqda...</p>;

  if (status === "forbidden") {
    return (
      <div className="form-page">
        <h1>Bu darsga ruxsat yo&apos;q</h1>
        <p className="muted">
          Ushbu darsni ko&apos;rish uchun kursga yozilishingiz kerak, yoki u faqat bepul preview
          sifatida ochilmagan.
        </p>
        <Link href={courseId ? `/courses/${courseId}` : "/"} className="link-btn">
          Kurs sahifasiga qaytish
        </Link>
        {!user && (
          <p className="muted">
            Avval <Link href="/login">tizimga kiring</Link> yoki{" "}
            <Link href="/register">ro&apos;yxatdan o&apos;ting</Link>.
          </p>
        )}
      </div>
    );
  }

  if (status === "notfound" || !lesson) {
    return <p className="error">Dars topilmadi.</p>;
  }

  const embedUrl = toEmbedUrl(lesson.video_url);

  return (
    <div className="lesson-view">
      <Link href={`/courses/${courseId}`} className="back-link">
        ← {course ? course.title : "Kursga qaytish"}
      </Link>
      <h1>{lesson.title}</h1>
      <p className="muted">
        {lesson.duration_minutes} daqiqa
        {lesson.is_free_preview && <span className="badge free-badge">Bepul preview</span>}
      </p>

      {embedUrl && (
        <div className="video-wrapper">
          <iframe
            src={embedUrl}
            title={lesson.title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      )}

      {lesson.content && <p className="lesson-content">{lesson.content}</p>}
    </div>
  );
}
