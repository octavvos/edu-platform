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

const SUBMISSION_STATUS_LABELS = {
  submitted: "Tekshirilmoqda",
  under_review: "Ko'rib chiqilmoqda",
  needs_revision: "Qayta ishlash kerak",
  accepted: "Qabul qilindi",
};

function HomeworkBox({ lessonId }) {
  const [homework, setHomework] = useState(null);
  const [submission, setSubmission] = useState(null);
  const [content, setContent] = useState("");
  const [link, setLink] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    api
      .get("/homeworks/", { params: { lesson: lessonId } })
      .then(({ data }) => {
        const hw = (data.results ?? data)[0];
        setHomework(hw || null);
        if (hw) {
          return api.get("/submissions/", { params: { homework: hw.id } }).then(({ data: subs }) => {
            const list = subs.results ?? subs;
            if (list.length > 0) setSubmission(list[0]);
          });
        }
      })
      .finally(() => setLoaded(true));
  }, [lessonId]);

  if (!loaded || !homework) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const { data } = await api.post("/submissions/", { homework: homework.id, content, link });
      setSubmission(data);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="quiz">
      <h2>Uy vazifasi</h2>
      <div className="quiz-question">
        <p className="quiz-question-text">{homework.instructions}</p>
        {homework.deadline && (
          <p className="muted">Muddat: {new Date(homework.deadline).toLocaleString("uz-UZ")}</p>
        )}
      </div>

      {submission && (
        <div className="module">
          <p>
            Holat: <strong>{SUBMISSION_STATUS_LABELS[submission.status] || submission.status}</strong>
            {submission.is_late && <span className="badge" style={{ marginLeft: 8 }}>Kech topshirilgan</span>}
          </p>
          {submission.score !== null && submission.score !== undefined && (
            <p>Baho: <strong>{submission.score}/100</strong></p>
          )}
          {submission.feedback && <p className="muted">Fikr-mulohaza: {submission.feedback}</p>}
        </div>
      )}

      {(!submission || submission.status === "needs_revision") && (
        <form onSubmit={handleSubmit} className="form">
          <label>
            Yechim (matn)
            <textarea rows={4} value={content} onChange={(e) => setContent(e.target.value)} />
          </label>
          <label>
            Havola (GitHub, fayl va h.k.)
            <input value={link} onChange={(e) => setLink(e.target.value)} placeholder="https://..." />
          </label>
          <button type="submit" disabled={submitting}>
            {submitting ? "Yuborilmoqda..." : submission ? "Qayta topshirish" : "Topshirish"}
          </button>
        </form>
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
  const [enrollment, setEnrollment] = useState(null);
  const [completing, setCompleting] = useState(false);
  const [progress, setProgress] = useState(null);

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

    if (courseId && user) {
      api
        .get("/enrollments/", { params: { course: courseId } })
        .then(({ data }) => {
          const list = data.results ?? data;
          if (list.length > 0) setEnrollment(list[0]);
        })
        .catch(() => {});
    }
  }, [lessonId, courseId, authLoading, user]);

  const markComplete = async () => {
    if (!enrollment) return;
    setCompleting(true);
    try {
      const { data } = await api.post(`/enrollments/${enrollment.id}/progress/`, {
        lesson: lessonId,
        status: "completed",
      });
      setProgress(data.enrollment_progress_percent);
    } finally {
      setCompleting(false);
    }
  };

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

      {enrollment && (
        <div className="form-actions" style={{ margin: "20px 0" }}>
          <button onClick={markComplete} disabled={completing}>
            {completing ? "Saqlanmoqda..." : "Darsni tugatdim"}
          </button>
          {progress !== null && <span className="muted">Kurs progressi: {progress}%</span>}
        </div>
      )}

      <Quiz lessonId={lessonId} questions={lesson.questions} />
      {user && lesson.has_homework && <HomeworkBox lessonId={lessonId} />}
    </div>
  );
}
