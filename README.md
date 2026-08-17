# Edu Platform

B2B2C ta'lim platformasi (marketplace LMS). Backend — Django REST Framework
(TZ 3.0'dagi qatlamli arxitektura: `models` / `selectors` / `services` /
`api`), Frontend — Next.js, infratuzilma — Docker (PostgreSQL, Redis, Nginx).

## Stack

- **Backend:** Django 5, Django REST Framework, SimpleJWT, PostgreSQL, Redis
- **Frontend:** Next.js (React), Axios
- **Infra:** Docker, docker compose, Nginx (reverse proxy)

## Loyiha tuzilishi

```
edu-platform/
├── backend/
│   ├── config/                 # settings, urls (/api/v1/ + versiyasiz /api/ alias)
│   └── apps/
│       ├── core/                # BaseModel (UUID PK), domain-event bus (subscribe/emit)
│       ├── accounts/             # User, JWT + OTP auth (eski "users" app o'rniga)
│       ├── rbac/                 # Permission, Role, RoleAssignment (scope: global/course/org)
│       ├── catalog/               # Category, Review
│       ├── courses/               # Course, Module, Lesson, VideoAsset
│       ├── enrollments/            # Enrollment, Progress, DripRule
│       ├── assessments/             # Question, Choice, Attempt, Answer (quiz)
│       ├── assignments/              # Homework, Submission (uy vazifasi)
│       ├── certificates/              # Certificate (100% progress'da avtomatik)
│       ├── payments/                   # Order, Payment, LedgerEntry, Promo
│       ├── notifications/               # Notification (in-app)
│       └── audit/                        # AuditLog, FeatureFlag
├── frontend/
│   ├── pages/
│   ├── components/
│   ├── context/
│   └── lib/
├── nginx/                # Nginx konfiguratsiyasi (asosiy kirish nuqtasi — :80)
└── docker-compose.yml
```

Modullar bir-birining modellarini to'g'ridan-to'g'ri import qilmaydi — bog'liq
bo'lgan joylarda `apps/core/events.py` orqali domain-event ishlatiladi
(masalan: to'lov muvaffaqiyatli bo'lganda `payments` → `payment_succeeded`
hodisasini chiqaradi, `enrollments` unga obuna bo'lib talabani avtomatik
kursga yozadi; kurs 100% tugallansa `enrollments` → `course_completed`,
`certificates` obuna bo'lib sertifikat chiqaradi).

## Ishga tushirish (Docker)

```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
docker compose up -d --build
```

Konteyner birinchi marta ko'tarilganda `entrypoint.sh` avtomatik migratsiya,
`seed_demo` (demo foydalanuvchilar + to'liq kurs) va `collectstatic`ni
bajaradi.

- **Sayt (asosiy kirish):** http://localhost — barcha so'rovlar shu orqali
  o'tishi kerak (Nginx), aks holda CORS/static fayllar ishlamaydi
- Backend API: http://localhost:8000/api/
- Django admin: http://localhost:8000/admin/
- Frontend (to'g'ridan-to'g'ri, ishlab chiqish uchun): http://localhost:3000

## Demo ma'lumotlar

Bitta to'liq kurs oldindan yuklangan: **"Dasturlash kursi: Scratch, Python,
PostgreSQL, Django"** — 5 modul, 96 dars, har birida test savoli, har modul
oxirida amaliy uy vazifasi.

| Login | Parol | Rol |
|---|---|---|
| `admin` | `AdminPass123!` | super_admin (moderatsiya, publish) |
| `diyorbek` | `Demo12345!` | teacher (kurs egasi) |
| `javohir` | `Demo12345!` | student (kursga yozilgan, progress bor) |
| `nilufar` | `Demo12345!` | student (kursni 100% tugatgan, sertifikati bor) |

## Asosiy foydalanuvchi oqimlari

- **Katalog → kurs → to'lov** — bepul kurs bevosita yoziladi, pullik kurs
  `/checkout/{kursId}` orqali buyurtma yaratadi (demo rejimida to'lov darhol
  tasdiqlanadi va talaba avtomatik kursga yoziladi)
- **Dars ko'rish** — video/matn, oxirida quiz; "Darsni tugatdim" tugmasi
  progress'ni yozadi; modul oxirida uy vazifasi topshiriladi
- **Sertifikat** — kurs 100% tugallanganda avtomatik chiqadi, `/certificates`
  sahifasida ko'rinadi, `/verify/{kod}` orqali ochiq tekshiriladi
- **O'qituvchi** — `/dashboard/courses/new` bilan kurs yaratadi, modul/dars
  qo'shadi, moderatsiyaga yuboradi; `/dashboard/submissions` orqali uy
  vazifalarini baholaydi
- **Admin** — `/dashboard/moderation` orqali moderatsiyadagi kurslarni
  ko'rib, tasdiqlaydi/nashr etadi

## To'lov provayderi

`PAYMENT_PROVIDER=manual` (standart, `.env`) — real Payme hisobi ulanmagani
uchun har qanday buyurtma darhol "to'landi" deb belgilanadi, real pul
harakati yo'q. Payme merchant kalitlari (`PAYME_MERCHANT_ID`,
`PAYME_SECRET_KEY`) kelganda `PAYMENT_PROVIDER=payme` qilib
`backend/apps/payments/providers.py` dagi `PaymeProvider` to'ldiriladi —
qolgan kod (services/API) o'zgarmaydi.

## Lokal ishga tushirish (Docker'siz)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API endpointlari (qisqacha)

Barchasi `/api/v1/...` ostida, `/api/...` — versiyasiz alias (eski
frontend/integratsiyalar uchun).

| Method | URL | Tavsif |
|---|---|---|
| POST | `/api/auth/register/` | Ro'yxatdan o'tish |
| POST | `/api/auth/login/` | JWT login (access/refresh) |
| POST | `/api/auth/token/refresh/` | Access tokenni yangilash |
| POST | `/api/auth/otp/request/` `/verify/` | OTP tasdiqlash |
| GET | `/api/auth/me/` | Joriy foydalanuvchi profili |
| GET/POST | `/api/courses/` | Kurslar ro'yxati / yaratish (teacher) |
| POST | `/api/courses/{id}/submit-for-moderation/` | Moderatsiyaga yuborish |
| POST | `/api/courses/{id}/publish/` | Nashr etish (admin) |
| GET/POST | `/api/courses/{id}/modules/`, `/api/modules/{id}/lessons/` | Modul/dars |
| POST | `/api/lessons/{id}/check-quiz/` | Quiz javoblarini tekshirish |
| GET/POST | `/api/enrollments/` | Kursga yozilish (bepul) |
| POST | `/api/enrollments/{id}/progress/` | Dars progressini belgilash |
| GET/POST | `/api/homeworks/`, `/api/submissions/` | Uy vazifasi va topshirish |
| POST | `/api/submissions/{id}/grade/` | Baholash (teacher/mentor) |
| GET | `/api/certificates/` | O'z sertifikatlarim |
| GET | `/api/verify/{code}/` | Sertifikatni tekshirish (ochiq) |
| POST | `/api/orders/` | Buyurtma yaratish va to'lash |
| GET | `/api/notifications/`, POST `/mark-read/` | Bildirishnomalar |

## Bilinadigan cheklovlar

Ushbu MVP TZ'ning arxitekturaviy asosini (RBAC, domain events, to'lov/
sertifikat/uy vazifasi oqimlari) to'liq amalga oshiradi, lekin quyidagilar
real hisob/vaqt talab qilgani uchun stub holida qoldirilgan: real Payme
integratsiyasi, Eskiz.uz SMS (OTP hozircha konsolga/logga yoziladi), Bunny
Stream video (HLS/watermark), Celery/Beat (hodisalar hozircha sinxron
ishlaydi), 2FA, PDF sertifikat generatsiyasi.

## Litsenziya

MVP maqsadlarida ishlab chiqilgan, ichki foydalanish uchun.
