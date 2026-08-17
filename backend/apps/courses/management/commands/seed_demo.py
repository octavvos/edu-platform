from django.core.management.base import BaseCommand
from django.db import transaction

from apps.courses.models import Course, Lesson, Module
from apps.enrollments.models import Enrollment
from apps.users.models import User

TEACHERS = [
    {
        "username": "diyorbek",
        "email": "diyorbek@example.com",
        "first_name": "Diyorbek",
        "last_name": "Yusupov",
        "phone": "+998901234501",
    },
    {
        "username": "malika",
        "email": "malika@example.com",
        "first_name": "Malika",
        "last_name": "Karimova",
        "phone": "+998901234502",
    },
]

STUDENTS = [
    {
        "username": "javohir",
        "email": "javohir@example.com",
        "first_name": "Javohir",
        "last_name": "Rustamov",
        "phone": "+998901234601",
    },
    {
        "username": "nilufar",
        "email": "nilufar@example.com",
        "first_name": "Nilufar",
        "last_name": "Ergasheva",
        "phone": "+998901234602",
    },
]

COURSES = [
    {
        "teacher": "diyorbek",
        "title": "Python dasturlash asoslari",
        "description": (
            "Python tilining sintaksisi, ma'lumotlar turlari, funksiyalar va "
            "obyektga yo'naltirilgan dasturlashning asoslarini noldan o'rganing."
        ),
        "level": Course.Level.BEGINNER,
        "price": 0,
        "modules": [
            {
                "title": "Kirish va o'rnatish",
                "lessons": [
                    ("Python nima va u nima uchun kerak", Lesson.ContentType.VIDEO, True),
                    ("Python va muharrirni o'rnatish", Lesson.ContentType.VIDEO, False),
                    ("Birinchi dasturingiz: Hello, World!", Lesson.ContentType.TEXT, False),
                ],
            },
            {
                "title": "O'zgaruvchilar va ma'lumot turlari",
                "lessons": [
                    ("O'zgaruvchilar va nomlash qoidalari", Lesson.ContentType.TEXT, False),
                    ("Sonlar, satrlar, ro'yxatlar", Lesson.ContentType.VIDEO, False),
                    ("Amaliy mashqlar", Lesson.ContentType.QUIZ, False),
                ],
            },
        ],
    },
    {
        "teacher": "diyorbek",
        "title": "Django bilan Web dasturlash",
        "description": (
            "Django framework yordamida to'liq funksional web-ilova qurishni "
            "o'rganasiz: modellar, view'lar, REST API va autentifikatsiya."
        ),
        "level": Course.Level.INTERMEDIATE,
        "price": 250000,
        "modules": [
            {
                "title": "Django asoslari",
                "lessons": [
                    ("Loyihani sozlash va tuzilishi", Lesson.ContentType.VIDEO, True),
                    ("Modellar va migratsiyalar", Lesson.ContentType.TEXT, False),
                    ("Admin panel bilan ishlash", Lesson.ContentType.VIDEO, False),
                ],
            },
            {
                "title": "REST API yaratish",
                "lessons": [
                    ("Django REST Framework kirish", Lesson.ContentType.VIDEO, False),
                    ("Serializers va ViewSets", Lesson.ContentType.TEXT, False),
                ],
            },
        ],
    },
    {
        "teacher": "malika",
        "title": "Frontend: HTML, CSS, JavaScript",
        "description": (
            "Zamonaviy veb-saytlar yaratish uchun kerak bo'lgan HTML, CSS va "
            "JavaScript asoslarini amaliy loyihalar orqali o'rganing."
        ),
        "level": Course.Level.BEGINNER,
        "price": 150000,
        "modules": [
            {
                "title": "HTML va CSS asoslari",
                "lessons": [
                    ("HTML tuzilishi va teglar", Lesson.ContentType.VIDEO, True),
                    ("CSS bilan stillashtirish", Lesson.ContentType.VIDEO, False),
                    ("Flexbox va Grid", Lesson.ContentType.TEXT, False),
                ],
            },
            {
                "title": "JavaScript asoslari",
                "lessons": [
                    ("O'zgaruvchilar va funksiyalar", Lesson.ContentType.TEXT, False),
                    ("DOM bilan ishlash", Lesson.ContentType.VIDEO, False),
                ],
            },
        ],
    },
    {
        "teacher": "malika",
        "title": "Raqamli marketing asoslari",
        "description": (
            "SMM, kontent marketing va reklama kampaniyalarini rejalashtirish "
            "hamda tahlil qilish bo'yicha amaliy bilimlar."
        ),
        "level": Course.Level.BEGINNER,
        "price": 100000,
        "modules": [
            {
                "title": "Marketing strategiyasi",
                "lessons": [
                    ("Maqsadli auditoriyani aniqlash", Lesson.ContentType.VIDEO, True),
                    ("Kontent-reja tuzish", Lesson.ContentType.TEXT, False),
                ],
            },
        ],
    },
]

DEFAULT_PASSWORD = "Demo12345!"


class Command(BaseCommand):
    help = "Namuna foydalanuvchilar, kurslar, modullar va darslarni yaratadi (demo uchun)."

    @transaction.atomic
    def handle(self, *args, **options):
        teacher_objs = {}
        for data in TEACHERS:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    **data,
                    "role": User.Role.TEACHER,
                    "is_phone_verified": True,
                },
            )
            if created:
                user.set_password(DEFAULT_PASSWORD)
                user.save()
            teacher_objs[data["username"]] = user
            self.stdout.write(f"Teacher: {user.username} ({'created' if created else 'exists'})")

        student_objs = {}
        for data in STUDENTS:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    **data,
                    "role": User.Role.STUDENT,
                    "is_phone_verified": True,
                },
            )
            if created:
                user.set_password(DEFAULT_PASSWORD)
                user.save()
            student_objs[data["username"]] = user
            self.stdout.write(f"Student: {user.username} ({'created' if created else 'exists'})")

        for course_data in COURSES:
            teacher = teacher_objs[course_data["teacher"]]
            course, created = Course.objects.get_or_create(
                title=course_data["title"],
                defaults={
                    "teacher": teacher,
                    "description": course_data["description"],
                    "level": course_data["level"],
                    "price": course_data["price"],
                    "is_published": True,
                },
            )
            self.stdout.write(f"Course: {course.title} ({'created' if created else 'exists'})")

            if not created:
                continue

            for m_order, module_data in enumerate(course_data["modules"]):
                module = Module.objects.create(course=course, title=module_data["title"], order=m_order)
                for l_order, (title, content_type, is_free) in enumerate(module_data["lessons"]):
                    Lesson.objects.create(
                        module=module,
                        title=title,
                        content_type=content_type,
                        content=(
                            f"\"{title}\" darsi matni. Bu yerda dars bo'yicha to'liq "
                            "tushuntirish, misollar va qo'shimcha materiallar joylashadi."
                        ),
                        video_url="https://www.youtube.com/embed/dQw4w9WgXcQ" if content_type == Lesson.ContentType.VIDEO else "",
                        duration_minutes=10 + l_order * 5,
                        order=l_order,
                        is_free_preview=is_free,
                    )

        # Demo enrollment: javohir -> Python asoslari, Frontend
        javohir = student_objs["javohir"]
        for title in ["Python dasturlash asoslari", "Frontend: HTML, CSS, JavaScript"]:
            course = Course.objects.filter(title=title).first()
            if course:
                enrollment, created = Enrollment.objects.get_or_create(student=javohir, course=course)
                if created:
                    enrollment.progress_percent = 35
                    enrollment.save(update_fields=["progress_percent"])

        self.stdout.write(self.style.SUCCESS("Demo ma'lumotlar tayyor."))
        self.stdout.write(f"Barcha demo foydalanuvchilar paroli: {DEFAULT_PASSWORD}")
