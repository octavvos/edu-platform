import { useRouter } from "next/router";
import { useEffect, useState } from "react";

import ProtectedRoute from "@/components/ProtectedRoute";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

function NewModuleForm({ courseId, onCreated }) {
  const [title, setTitle] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    setSubmitting(true);
    try {
      const { data } = await api.post(`/courses/${courseId}/modules/`, { title });
      onCreated(data);
      setTitle("");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="inline-form">
      <input
        placeholder="Yangi modul nomi"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <button type="submit" disabled={submitting}>
        {submitting ? "..." : "Modul qo'shish"}
      </button>
    </form>
  );
}

function NewLessonForm({ moduleId, onCreated }) {
  const [form, setForm] = useState({
    title: "",
    content_type: "text",
    content: "",
    video_url: "",
    duration_minutes: 10,
    is_free_preview: false,
  });
  const [submitting, setSubmitting] = useState(false);
  const [open, setOpen] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title.trim()) return;
    setSubmitting(true);
    try {
      const { data } = await api.post(`/modules/${moduleId}/lessons/`, form);
      onCreated(data);
      setForm({ title: "", content_type: "text", content: "", video_url: "", duration_minutes: 10, is_free_preview: false });
      setOpen(false);
    } finally {
      setSubmitting(false);
    }
  };

  if (!open) {
    return (
      <button type="button" className="link-btn add-lesson-btn" onClick={() => setOpen(true)}>
        + Dars qo&apos;shish
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="form lesson-form">
      <label>
        Dars nomi
        <input name="title" value={form.title} onChange={handleChange} required />
      </label>
      <label>
        Turi
        <select name="content_type" value={form.content_type} onChange={handleChange}>
          <option value="text">Matn</option>
          <option value="video">Video</option>
          <option value="quiz">Quiz</option>
        </select>
      </label>
      {form.content_type === "video" && (
        <label>
          Video URL
          <input name="video_url" value={form.video_url} onChange={handleChange} placeholder="https://..." />
        </label>
      )}
      <label>
        Matn / tavsif
        <textarea name="content" rows={3} value={form.content} onChange={handleChange} />
      </label>
      <label>
        Davomiyligi (daqiqa)
        <input type="number" name="duration_minutes" min="0" value={form.duration_minutes} onChange={handleChange} />
      </label>
      <label className="checkbox-label">
        <input type="checkbox" name="is_free_preview" checked={form.is_free_preview} onChange={handleChange} />
        Bepul preview sifatida ko&apos;rsatish
      </label>
      <div className="form-actions">
        <button type="submit" disabled={submitting}>
          {submitting ? "Saqlanmoqda..." : "Saqlash"}
        </button>
        <button type="button" className="secondary" onClick={() => setOpen(false)}>
          Bekor qilish
        </button>
      </div>
    </form>
  );
}

function ManageCourseContent() {
  const router = useRouter();
  const { id } = router.query;
  const { user } = useAuth();
  const [course, setCourse] = useState(null);
  const [error, setError] = useState("");
  const [publishing, setPublishing] = useState(false);

  const loadCourse = () => {
    if (!id) return;
    api
      .get(`/courses/${id}/`)
      .then(({ data }) => setCourse(data))
      .catch(() => setError("Kursni yuklashda xatolik yoki sizga tegishli emas."));
  };

  useEffect(loadCourse, [id]);

  if (error) return <p className="error">{error}</p>;
  if (!course) return <p>Yuklanmoqda...</p>;

  if (user && course.teacher !== user.id && user.role !== "admin") {
    return <p className="error">Bu kursni boshqarish huquqingiz yo&apos;q.</p>;
  }

  const submitForModeration = async () => {
    setPublishing(true);
    try {
      const { data } = await api.post(`/courses/${id}/submit-for-moderation/`);
      setCourse({ ...course, status: data.status, is_published: data.is_published });
    } finally {
      setPublishing(false);
    }
  };

  const publishCourse = async () => {
    setPublishing(true);
    try {
      const { data } = await api.post(`/courses/${id}/publish/`);
      setCourse({ ...course, status: data.status, is_published: data.is_published });
    } finally {
      setPublishing(false);
    }
  };

  const STATUS_LABELS = {
    draft: "Qoralama",
    moderation: "Moderatsiyada",
    published: "Nashr etilgan",
    rejected: "Rad etilgan",
  };

  const handleModuleCreated = (module) => {
    setCourse({ ...course, modules: [...course.modules, { ...module, lessons: [] }] });
  };

  const handleLessonCreated = (moduleId, lesson) => {
    setCourse({
      ...course,
      modules: course.modules.map((m) => (m.id === moduleId ? { ...m, lessons: [...m.lessons, lesson] } : m)),
    });
  };

  return (
    <div>
      <div className="manage-header">
        <div>
          <h1>{course.title}</h1>
          <p className="muted">{course.description}</p>
        </div>
        <div>
          <span className="badge" style={{ marginRight: 10 }}>
            {STATUS_LABELS[course.status] || course.status}
          </span>
          {course.status === "draft" && (
            <button className="secondary" onClick={submitForModeration} disabled={publishing}>
              Moderatsiyaga yuborish
            </button>
          )}
          {course.status === "moderation" && user?.role === "admin" && (
            <button className="secondary" onClick={publishCourse} disabled={publishing}>
              Tasdiqlash va nashr etish
            </button>
          )}
        </div>
      </div>

      <h2>Modullar va darslar</h2>
      {course.modules.length === 0 && <p className="muted">Hali modul qo&apos;shilmagan.</p>}
      <div className="modules">
        {course.modules.map((m) => (
          <div key={m.id} className="module">
            <h3>{m.title}</h3>
            <ul className="list">
              {m.lessons.map((l) => (
                <li key={l.id}>
                  {l.title}{" "}
                  <span className="muted">
                    ({l.content_type}, {l.duration_minutes} daq{l.is_free_preview ? ", bepul" : ""})
                  </span>
                </li>
              ))}
            </ul>
            <NewLessonForm moduleId={m.id} onCreated={(lesson) => handleLessonCreated(m.id, lesson)} />
          </div>
        ))}
      </div>

      <h3>Yangi modul qo&apos;shish</h3>
      <NewModuleForm courseId={id} onCreated={handleModuleCreated} />
    </div>
  );
}

export default function ManageCoursePage() {
  return (
    <ProtectedRoute>
      <ManageCourseContent />
    </ProtectedRoute>
  );
}
