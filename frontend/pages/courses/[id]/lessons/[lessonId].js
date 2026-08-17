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

function Quiz({ lessonId, questions }) {
  const [selected, setSelected] = useState({});
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  if (!questions || questions.length === 0) return null;

  const handleSelect = (questionId, choiceId) => {
    if (result) return;
    setSelected({ ...selected, [questionId]: choiceId });
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const { data } = await api.post(`/lessons/${lessonId}/check-quiz/`, { answers: selected });
      setResult(data);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRetry = () => {
    setResult(null);
    setSelected({});
  };

  const allAnswered = questions.every((q) => selected[q.id] !== undefined);

  return (
    <div className="quiz">
      <h2>Bilimingizni tekshiring</h2>
      {questions.map((q) => (
        <div key={q.id} className="quiz-question">
          <p className="quiz-question-text">{q.text}</p>
          <div className="quiz-choices">
            {q.choices.map((c) => {
              const isSelected = selected[q.id] === c.id;
              let choiceClass = "quiz-choice";
              if (isSelected) choiceClass += " selected";
              if (result) {
                const isCorrect = result.correct_choices[q.id] === c.id;
                if (isCorrect) choiceClass += " correct";
                else if (isSelected) choiceClass += " incorrect";
              }
              return (
                <button
                  type="button"
                  key={c.id}
                  className={choiceClass}
                  onClick={() => handleSelect(q.id, c.id)}
                  disabled={!!result}
                >
                  {c.text}
                </button>
              );
            })}
          </div>
        </div>
      ))}

      {!result && (
        <button onClick={handleSubmit} disabled={!allAnswered || submitting}>
          {submitting ? "Tekshirilmoqda..." : "Javoblarni yuborish"}
        </button>
      )}

      {result && (
        <div className="quiz-result">
          <p>
            Natija: <strong>{result.correct} / {result.total}</strong> to&apos;g&apos;ri javob
          </p>
          <button type="button" className="secondary" onClick={handleRetry}>
            Qayta urinish
          </button>
        </div>
      )}
    </div>
  );
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

      <Quiz lessonId={lessonId} questions={lesson.questions} />
    </div>
  );
}
