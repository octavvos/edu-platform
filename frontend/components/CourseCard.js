import Link from "next/link";

export default function CourseCard({ course }) {
  return (
    <Link href={`/courses/${course.id}`} className="course-card">
      <div className="course-card-cover">
        {course.cover_image ? (
          <img src={course.cover_image} alt={course.title} />
        ) : (
          <div className="course-card-placeholder">{course.title[0]}</div>
        )}
      </div>
      <div className="course-card-body">
        <h3>{course.title}</h3>
        <p className="muted">{course.teacher_name || "Instruktor"}</p>
        <div className="course-card-meta">
          <span className="badge">{course.level}</span>
          <span className="price">
            {Number(course.price) > 0 ? `${course.price} so'm` : "Bepul"}
          </span>
        </div>
      </div>
    </Link>
  );
}
