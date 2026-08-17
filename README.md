# Edu Platform — MVP

Online ta'lim platformasi uchun MVP. Backend — Django REST Framework, Frontend — Next.js, infratuzilma — Docker (PostgreSQL, Redis, Nginx).

## Stack

- **Backend:** Django 5, Django REST Framework, SimpleJWT, PostgreSQL, Redis
- **Frontend:** Next.js (React), Axios
- **Infra:** Docker, docker-compose, Nginx (reverse proxy)

## Loyiha tuzilishi

```
edu-platform/
├── backend/            # Django REST API
│   ├── config/         # settings, urls, wsgi/asgi
│   └── apps/
│       ├── users/          # User, RBAC, JWT + OTP auth
│       ├── courses/        # Course, Module, Lesson
│       └── enrollments/    # Enrollment
├── frontend/           # Next.js ilova
│   ├── pages/
│   ├── components/
│   ├── context/
│   └── lib/
├── nginx/               # Nginx konfiguratsiyasi
└── docker-compose.yml
```

## Ma'lumotlar modeli

- **User** — custom user model (`role`: admin / teacher / student, `phone`, `is_phone_verified`)
- **Course** — kurs (owner = teacher)
- **Module** — kurs ichidagi bo'lim
- **Lesson** — modul ichidagi dars
- **Enrollment** — student <-> course bog'lanishi (status, progress)

## Autentifikatsiya

- **JWT** (`djangorestframework-simplejwt`) — login/refresh/access token
- **OTP** — telefon raqam orqali ro'yxatdan o'tish/kirishni tasdiqlash (`/api/auth/otp/request/`, `/api/auth/otp/verify/`)
- **RBAC** — `IsAdmin`, `IsTeacher`, `IsStudent`, `IsCourseOwnerOrReadOnly` permission klasslari

## Ishga tushirish (Docker)

```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
docker-compose up --build
```

- Backend: http://localhost:8000/api/
- Django admin: http://localhost:8000/admin/
- Frontend: http://localhost:3000
- Nginx (reverse proxy): http://localhost

Birinchi ishga tushirishda migratsiya va superuser avtomatik `entrypoint.sh` orqali bajariladi.

## Lokal ishga tushirish (Docker'siz)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API endpointlari (qisqacha)

| Method | URL | Tavsif |
|---|---|---|
| POST | `/api/auth/register/` | Ro'yxatdan o'tish |
| POST | `/api/auth/login/` | JWT login (access/refresh) |
| POST | `/api/auth/token/refresh/` | Access tokenni yangilash |
| POST | `/api/auth/otp/request/` | OTP kod yuborish |
| POST | `/api/auth/otp/verify/` | OTP kodni tasdiqlash |
| GET | `/api/auth/me/` | Joriy foydalanuvchi profili |
| GET/POST | `/api/courses/` | Kurslar ro'yxati / yaratish (teacher) |
| GET/PUT/DELETE | `/api/courses/{id}/` | Kurs detail |
| GET/POST | `/api/courses/{id}/modules/` | Kurs modullari |
| GET/POST | `/api/modules/{id}/lessons/` | Modul darslari |
| GET/POST | `/api/enrollments/` | Kursga yozilish / yozilganlar ro'yxati |

## Litsenziya

MVP maqsadlarida ishlab chiqilgan, ichki foydalanish uchun.
