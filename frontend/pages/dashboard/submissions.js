import { useEffect, useState } from "react";

import ProtectedRoute from "@/components/ProtectedRoute";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

const STATUS_LABELS = {
  submitted: "Tekshirilmoqda",
  under_review: "Ko'rib chiqilmoqda",
  needs_revision: "Qayta ishlash kerak",
  accepted: "Qabul qilindi",
};

function GradeForm({ submission, onGraded }) {
  const [score, setScore] = useState(80);
  const [feedback, setFeedback] = useState("");
  const [gradeStatus, setGradeStatus] = useState("accepted");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const { data } = await api.post(`/submissions/${submission.id}/grade/`, {
        score: Number(score),
        feedback,
        status: gradeStatus,
      });
      onGraded(data);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="form lesson-form">
      <label>
        Baho (0-100)
        <input type="number" min="0" max="100" value={score} onChange={(e) => setScore(e.target.value)} />
      </label>
      <label>
        Fikr-mulohaza
        <textarea rows={2} value={feedback} onChange={(e) => setFeedback(e.target.value)} />
      </label>
      <label>
        Qaror
        <select value={gradeStatus} onChange={(e) => setGradeStatus(e.target.value)}>
          <option value="accepted">Qabul qilish</option>
          <option value="needs_revision">Qayta ishlashga qaytarish</option>
        </select>
      </label>
      <button type="submit" disabled={submitting}>
        {submitting ? "Saqlanmoqda..." : "Baholash"}
      </button>
    </form>
  );
}

function SubmissionsContent() {
  const { user } = useAuth();
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    api
      .get("/submissions/")
      .then(({ data }) => setSubmissions(data.results ?? data))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  if (user && !(user.role === "teacher" || user.role === "mentor" || user.role === "admin" || user.role === "super_admin")) {
    return <p className="error">Bu sahifaga faqat o&apos;qituvchi/mentor kirishi mumkin.</p>;
  }

  const handleGraded = (graded) => {
    setSubmissions(submissions.map((s) => (s.id === graded.id ? graded : s)));
  };

  const pending = submissions.filter((s) => s.status === "submitted" || s.status === "under_review");
  const graded = submissions.filter((s) => s.status === "accepted" || s.status === "needs_revision");

  return (
    <div>
      <h1>Uy vazifalarini tekshirish</h1>
      {loading && <p>Yuklanmoqda...</p>}

      {!loading && (
        <>
          <h2>Navbatda ({pending.length})</h2>
          {pending.length === 0 && <p className="muted">Tekshirilmagan topshiriqlar yo&apos;q.</p>}
          <div className="modules">
            {pending.map((s) => (
              <div key={s.id} className="module">
                <h3>{s.homework_lesson_title}</h3>
                <p className="muted">O&apos;quvchi: {s.student_username}</p>
                {s.content && <p className="lesson-content">{s.content}</p>}
                {s.link && (
                  <p>
                    <a href={s.link} target="_blank" rel="noreferrer">{s.link}</a>
                  </p>
                )}
                {s.is_late && <span className="badge">Kech topshirilgan</span>}
                <GradeForm submission={s} onGraded={handleGraded} />
              </div>
            ))}
          </div>

          <h2 style={{ marginTop: 32 }}>Baholangan ({graded.length})</h2>
          <ul className="list">
            {graded.map((s) => (
              <li key={s.id}>
                {s.homework_lesson_title} — {s.student_username}
                <span>
                  {STATUS_LABELS[s.status]} {s.score !== null && `(${s.score}/100)`}
                </span>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

export default function SubmissionsPage() {
  return (
    <ProtectedRoute>
      <SubmissionsContent />
    </ProtectedRoute>
  );
}
