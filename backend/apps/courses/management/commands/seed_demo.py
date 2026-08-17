from django.core.management.base import BaseCommand
from django.db import transaction

from apps.courses.models import Choice, Course, Lesson, Module, Question
from apps.enrollments.models import Enrollment
from apps.users.models import User

DEFAULT_PASSWORD = "Demo12345!"

TEACHER = {
    "username": "diyorbek",
    "email": "diyorbek@example.com",
    "first_name": "Diyorbek",
    "last_name": "Yusupov",
    "phone": "+998901234501",
}

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

COURSE_TITLE = "Dasturlash kursi: Scratch, Python, PostgreSQL, Django"
COURSE_DESCRIPTION = (
    "Scratch bilan dasturiy fikrlashdan boshlab, Python tili, algoritmlar, OOP, "
    "PostgreSQL ma'lumotlar bazasi, Django va Django REST Framework, Telegram bot "
    "yaratish va loyihani real serverga joylashtirishgacha bo'lgan to'liq yo'l. "
    "Kurs 8 oy davom etadi, haftasiga 3 kun, jami 96 ta dars (192 akademik soat)."
)

# Har bir element: (sarlavha, mazmuni, savol matni, to'g'ri javob, [3 ta noto'g'ri javob])
MODULES = [
    {
        "title": "Scratch bilan tanishuv va asosiy tushunchalar",
        "lessons": [
            (
                "Scratch bilan tanishuv. Harakat bloklari",
                "Scratch interfeysi. Sahna (Stage), Sprite, Bloklar paneli bilan tanishish. Birinchi "
                "kichik harakat: \"Mushukni yuritish\". Move, Turn, Go to bloklari. Sahna koordinatalari. "
                "Oddiy animatsiya. Mushukni chap/o'ng harakatlantirish. Mushukni aylantirish va 4 "
                "tomonga harakatlantirish.",
                "Scratch dasturida obyektlar qanday nomlanadi?",
                "Sprite",
                ["Widget", "Component", "Module"],
            ),
            (
                "Tovush va tashqi ko'rinish bloklari. Hodisalar (Events)",
                "Look (Ko'rinish) bloklari. Sound bloklari bilan tanishish. Kostyumlar (Costumes) "
                "almashishi. When green flag clicked. When key pressed. When sprite clicked. "
                "Mushukning \"salom berish\" animatsiyasi. Tugma bosilganda sprite harakat qiladigan "
                "mini mashq.",
                "Bayroqcha (green flag) bosilganda dasturni ishga tushiruvchi blok qanday ataladi?",
                "When green flag clicked",
                ["When key pressed", "When sprite clicked", "Forever"],
            ),
            (
                "Takrorlash bloklari. Shart operatorlari",
                "Forever, Repeat. Oddiy sikl (Loop) tushunchasi. If, If-else. To'qnashuv (touching) "
                "bloklari. Mushukning chetga urilib qaytishi (bounce effect). Mushuk to'siqqa tegsa "
                "\"oh!\" deydi.",
                "Sprite'ning boshqa obyektga tegib-tegmaganini tekshirish uchun qaysi blok ishlatiladi?",
                "touching",
                ["repeat", "forever", "if-else"],
            ),
            (
                "Sahna bilan ishlash",
                "Orqa fonlar almashishi. Yangi sahna qo'shish. Sahnalar o'rtasida o'tish. \"Kunning "
                "vaqtiga qarab fon o'zgaradi\" loyihasi.",
                "Scratch'da sahna foni qanday ataladi?",
                "Backdrop",
                ["Sprite", "Costume", "Stage script"],
            ),
            (
                "Oddiy o'yin yaratish — 1-qism",
                "O'yin turi: Sharchani tutish o'yini. Ball, tezlik, to'qnashuv tushunchasi. Tushayotgan "
                "sharcha sprite yaratiladi.",
                "\"Sharchani tutish\" o'yinida asosiy harakatlanuvchi obyekt nima?",
                "Tushayotgan sharcha",
                ["Fon rasmi", "Matn bloki", "Tovush fayli"],
            ),
            (
                "Oddiy o'yin yaratish — 2-qism",
                "Ball qo'shish. \"Game over\" holati. Tovush qo'shish. O'yin ishchi holatga keltiriladi.",
                "O'yin tugaganda ko'rsatiladigan holat qanday ataladi?",
                "Game over",
                ["Start screen", "Backdrop", "Sprite panel"],
            ),
            (
                "Matematik amallar bilan ishlash",
                "Random (tasodifiy sonlar). O'zgaruvchilar (Variables) bilan tanishish. Sprite ning "
                "tasodifiy joyga sakrashi.",
                "Scratch'da tasodifiy son hosil qilish uchun qaysi blok ishlatiladi?",
                "pick random",
                ["variable", "repeat", "touching"],
            ),
            (
                "Mini loyihalar kuni",
                "Mini animatsiya. Mini multfilm. Mini o'yin. Har guruh 1 loyihani boshlaydi.",
                "Mini loyihalar kunida har bir guruh nechta loyihadan boshlaydi?",
                "1 ta",
                ["2 ta", "3 ta", "5 ta"],
            ),
            (
                "Loyiha taqdimoti",
                "Har bir guruh o'z loyihasini taqdim etadi. O'qituvchi baholaydi. IT bo'yicha "
                "motivatsion suhbat. O'quvchi o'z o'yinini sinf oldida ko'rsatadi.",
                "Loyiha taqdimoti darsining asosiy maqsadi nima?",
                "O'z loyihasini sinf oldida taqdim etish",
                ["Yangi til o'rganish", "Test topshirish", "Kitob o'qish"],
            ),
        ],
    },
    {
        "title": "Python dasturlash tili va algoritmlari",
        "lessons": [
            (
                "(Python) Python bilan tanishuv",
                "Python tarixi va qo'llanish sohalari. Python interpreter qanday ishlaydi (compiled vs "
                "interpreted). Python va IDE o'rnatish (PyCharm, VS Code). Birinchi dastur: print() va "
                "input(). PEP8 va kod yozish madaniyati.",
                "Ekranga matn chiqarish uchun Python'da qaysi funksiya ishlatiladi?",
                "print()",
                ["input()", "echo()", "console.log()"],
            ),
            (
                "(Python) Sintaksis, o'zgaruvchilar va kommentariyalar",
                "O'zgaruvchi va nomlash qoidalari. Constants tushunchasi (UPPER_CASE). Comments: # va "
                "docstring. Type Conversion: int(), str(), float(), bool(). type() va isinstance() "
                "funksiyalari.",
                "Python'da bitta qatorli izoh (comment) qaysi belgi bilan boshlanadi?",
                "#",
                ["//", "/*", "--"],
            ),
            (
                "(Python) Stringlar va formatlash",
                "String yaratish va indekslash. String slicing ([start:stop:step]). F-strings, "
                "format(), % formatlash. Raw strings (r\"...\") va escape belgilari. String metodlari: "
                "upper(), lower(), strip(), split(), join(), replace(), find().",
                "String'ni bosh va oxiridagi bo'shliqlardan tozalash uchun qaysi metod ishlatiladi?",
                "strip()",
                ["split()", "join()", "find()"],
            ),
            (
                "(Python) Sonlar va operatorlar",
                "Numbers: int, float, complex. Arifmetik operatorlar (+, -, *, /, //, %, **). "
                "Comparison operatorlar. Logical operatorlar (and, or, not). Truthy va Falsy "
                "qiymatlar.",
                "Butun qismli (qoldiqsiz) bo'lish uchun qaysi operator ishlatiladi?",
                "//",
                ["/", "%", "**"],
            ),
            (
                "(Python) Shartli operatorlar va Control Flow",
                "if, elif, else tuzilmasi. Ichma-ich shartlar (nested if). Ternary operator (a if cond "
                "else b). match-case (Python 3.10+). Amaliy mashqlar.",
                "match-case konstruksiyasi Python'ning qaysi versiyasidan boshlab qo'shilgan?",
                "3.10",
                ["2.7", "3.0", "3.6"],
            ),
            (
                "(Python) while sikli",
                "while sikli tuzilishi va shartlari. break, continue, pass operatorlari. Cheksiz "
                "sikllar va ulardan chiqish. while-else konstruksiyasi. Amaliy mashqlar.",
                "Sikldan to'liq chiqish uchun qaysi operator ishlatiladi?",
                "break",
                ["continue", "pass", "return"],
            ),
            (
                "(Python) for sikli va range()",
                "for sikli sintaksisi. range() funksiyasi (start, stop, step). Iterables tushunchasi. "
                "Ichma-ich sikllar (nested loops). Amaliy: jadvallar va naqshlar.",
                "range() funksiyasi nechta asosiy parametrni qabul qiladi?",
                "3 ta: start, stop, step",
                ["1 ta", "2 ta", "4 ta"],
            ),
            (
                "(Python) Ro'yxatlar (List) — 1-qism",
                "List yaratish va indekslash. Slicing va elementlarni o'zgartirish. append(), "
                "insert(), extend(). remove(), pop(), del. len(), min(), max(), sum() funksiyalari.",
                "Ro'yxat oxiriga bitta element qo'shish uchun qaysi metod ishlatiladi?",
                "append()",
                ["extend()", "insert()", "remove()"],
            ),
            (
                "(Python) Ro'yxatlar (List) — 2-qism",
                "sort(), sorted(), reverse(). List ustida iterate qilish. List comprehension (asosiy "
                "va shartli). map(), filter(), reduce() bilan tanishuv. Element indeksini topish.",
                "Ro'yxatni asl holatini o'zgartirmasdan yangi saralangan ro'yxat qaytaruvchi funksiya "
                "qaysi?",
                "sorted()",
                ["sort()", "reverse()", "list()"],
            ),
            (
                "(Python) Tuple va unpacking",
                "Tuple yaratish va xususiyatlari (immutable). Tuple packing va unpacking. * bilan "
                "unpacking. Tuple metodlari: count(), index(). Tuple vs List — qachon qaysi biri "
                "kerak.",
                "List'dan farqli o'laroq, tuple qanday xususiyatga ega?",
                "Immutable (o'zgarmas)",
                ["Mutable (o'zgaruvchan)", "Kalit-qiymat saqlaydi", "Faqat sonlarni saqlaydi"],
            ),
            (
                "(Python) Set (To'plamlar)",
                "Set yaratish va uniqueness xususiyati. add(), remove(), discard(), pop(). Union, "
                "intersection, difference, symmetric difference. Subset, superset, disjoint sets. Set "
                "comprehension, Frozenset.",
                "Set (to'plam)ning asosiy xususiyati nima?",
                "Faqat unikal (takrorlanmas) elementlar saqlaydi",
                ["Tartiblangan indekslarga ega", "Kalit-qiymat juftligi saqlaydi", "O'zgarmas (immutable)"],
            ),
            (
                "(Python) Dictionary (Lug'atlar)",
                "Key-value tuzilmasi. Dict yaratish va elementga kirish. get(), keys(), values(), "
                "items(). update(), pop(), setdefault(). Ichma-ich dict (nested), Dict comprehension.",
                "Dictionary qanday tuzilmada ma'lumot saqlaydi?",
                "Key-value (kalit-qiymat)",
                ["Faqat indeks bo'yicha", "Faqat unikal qiymatlar", "Ikki o'lchamli massiv"],
            ),
            (
                "(Python) Funksiyalar — 1-qism",
                "def bilan funksiya yaratish. Parametrlar va return. Positional va keyword "
                "argumentlar. Default parameters. Docstring va funksiyani hujjatlash.",
                "Python'da funksiya qaysi kalit so'z bilan e'lon qilinadi?",
                "def",
                ["function", "func", "define"],
            ),
            (
                "(Python) Funksiyalar — 2-qism",
                "*args va **kwargs. Local va global scope. Lambda funksiyalar (qisqa). Funksiyalar "
                "bilan amaliy mashqlar.",
                "Funksiyaga cheklanmagan sonda keyword-argument qabul qilish uchun nima ishlatiladi?",
                "**kwargs",
                ["*args", "def", "lambda"],
            ),
            (
                "(Python) Exception handling",
                "Exception nima va qachon kerak. try, except, else, finally. Eng ko'p uchraydigan "
                "exceptionlar (ValueError, TypeError, ZeroDivisionError, IndexError, KeyError). raise "
                "bilan xato chiqarish. Bir nechta except bloklari.",
                "Songa 0 ga bo'lishda qaysi exception yuzaga keladi?",
                "ZeroDivisionError",
                ["ValueError", "KeyError", "IndexError"],
            ),
            (
                "(Python) Modullar va paketlar",
                "import, from ... import, as. __name__ va __main__. Module search path (sys.path). "
                "O'z modulini yaratish. Paket (package) tushunchasi va __init__.py, virtual muhit "
                "(venv).",
                "Python paketini (package) belgilash uchun papka ichida qaysi fayl bo'lishi kerak?",
                "__init__.py",
                ["main.py", "setup.py", "package.py"],
            ),
            (
                "(Python) Fayllar bilan ishlash",
                "open() va rejimlar (r, w, a, x). with open(...) konstruksiyasi (context manager). "
                "read(), readline(), readlines(), write(), writelines(). CSV fayllar (csv moduli). "
                "JSON fayllar (json moduli).",
                "Faylni ochib, avtomatik yopilishini ta'minlaydigan konstruksiya qaysi?",
                "with open(...)",
                ["try open(...)", "def open(...)", "import open(...)"],
            ),
            (
                "(Python) Git va GitHub asoslari",
                "Git va GitHub nima, qanday farqlari bor. git init, add, commit, push, pull. GitHub "
                "akkaunt va repository. .gitignore va README.md. Har dars yangi commit bilan GitHub'ga "
                "yuklash.",
                "Lokal repozitoriyani GitHub'dagi masofaviy repozitoriyaga yuklash uchun qaysi buyruq "
                "ishlatiladi?",
                "git push",
                ["git pull", "git init", "git clone"],
            ),
            (
                "(Python) OOP — Class va Object",
                "Procedural vs OOP yondashuv. Class va object tushunchalari. __init__ va self. "
                "Instance va class atributlari. Static methods va class methods (@staticmethod, "
                "@classmethod).",
                "Yangi obyekt yaratilganda avtomatik chaqiriladigan konstruktor metod qaysi?",
                "__init__",
                ["__str__", "__call__", "__new__"],
            ),
            (
                "(Python) Encapsulation va Property",
                "Public, protected (_), private (__) atributlar. Name mangling tushunchasi. @property "
                "dekoratori. Getter, setter, deleter. Read-only property.",
                "Python'da private atributni belgilash uchun nechta pastki chiziq ishlatiladi?",
                "2 ta (__)",
                ["1 ta (_)", "3 ta (___)", "0 ta"],
            ),
            (
                "(Python) Inheritance (Meros olish)",
                "Bir tomonlama meros olish. super() funksiyasi. Method overriding. isinstance() va "
                "issubclass(). Method Resolution Order (MRO) asoslari.",
                "Ota (parent) klass metodini bola (child) klassdan chaqirish uchun nima ishlatiladi?",
                "super()",
                ["self()", "parent()", "base()"],
            ),
            (
                "(Python) Multiple inheritance va Mixin",
                "Multiple inheritance. MRO chuqur (C3 linearization). Diamond problem. Mixin "
                "classlari va amaliy ishlatilishi. Composition vs Inheritance.",
                "Bir nechta ota-klassdan meros olishda yuzaga keladigan murakkab holat qanday ataladi?",
                "Diamond problem",
                ["Mixin error", "MRO exception", "Composition conflict"],
            ),
            (
                "(Python) Polymorphism va Abstract Class",
                "Polimorfizm tushunchasi va Duck typing. Operator overloading. abc moduli, ABC, "
                "@abstractmethod. Abstract class yaratish. Interface tushunchasi Python'da.",
                "Abstrakt klass yaratish uchun qaysi modul ishlatiladi?",
                "abc",
                ["abstract", "typing", "collections"],
            ),
            (
                "(Python) Magic / Dunder metodlar",
                "__str__ va __repr__ (farqlari). __len__, __getitem__, __setitem__, __delitem__. "
                "__eq__, __lt__, __gt__, __hash__. __bool__, __call__, __del__. Amaliy: o'z konteyner "
                "classini yozish.",
                "Obyektni print() qilganda foydalanuvchiga tushunarli matn qaytaradigan dunder metod "
                "qaysi?",
                "__str__",
                ["__len__", "__init__", "__call__"],
            ),
            (
                "(Python) References va Memory boshqaruvi",
                "References (obyektlar xotirada qanday yashaydi). Dynamic typing chuqur. Mutable vs "
                "Immutable obyektlar. is vs == operatorlari farqi. None tushunchasi, Garbage "
                "collection asoslari, id() va sys.getsizeof().",
                "Ikki obyektning xotiradagi bir xil manzilga ishora qilishini tekshirish uchun qaysi "
                "operator ishlatiladi?",
                "is",
                ["==", "in", "as"],
            ),
            (
                "(Python) Sonlar chuqur va Sequence types",
                "Integer types (Python'da int cheksiz). decimal moduli (aniq hisoblar uchun). float "
                "muammolari (0.1 + 0.2 ≠ 0.3). fractions moduli. Sequence types umumiy xususiyatlari, "
                "collections.abc.",
                "Moliyaviy hisob-kitoblarda aniq natija olish uchun qaysi modul tavsiya etiladi?",
                "decimal",
                ["fractions", "random", "math"],
            ),
            (
                "(Python) Closures va Decoratorlar — 1-qism",
                "Funksiya — birinchi sinf obyekti. Closures (yopilmalar) chuqur. nonlocal "
                "o'zgaruvchilar. Oddiy decorator yozish. @ sintaksisi va functools.wraps, amaliy: "
                "timer, logger.",
                "Ichki funksiyada tashqi funksiya o'zgaruvchisini o'zgartirish uchun qaysi kalit so'z "
                "ishlatiladi?",
                "nonlocal",
                ["global", "local", "static"],
            ),
            (
                "(Python) Decoratorlar — 2-qism",
                "Argumentli decoratorlar (decorator factory). Class decoratorlar. Bir nechta "
                "decoratorlarni birlashtirish. functools.lru_cache (caching). @property ni decorator "
                "sifatida qayta ko'rish.",
                "Funksiya natijalarini keshlash (caching) uchun functools'dan qaysi decorator "
                "ishlatiladi?",
                "lru_cache",
                ["wraps", "property", "cached_property"],
            ),
            (
                "(Python) Iteratorlar va Generatorlar",
                "Iterable vs Iterator farqi. __iter__ va __next__ metodlari. yield va generator "
                "funksiya. Generator expressions, yield from. Lazy evaluation va memory afzalliklari.",
                "Generator funksiya yaratish uchun qaysi kalit so'z ishlatiladi?",
                "yield",
                ["return", "iter", "next"],
            ),
            (
                "(Python) Funksional dasturlash va Named Tuples",
                "map(), filter(), reduce() chuqur. zip(), enumerate(), any(), all(). sorted() va key "
                "parametri. collections.namedtuple va typing.NamedTuple. dataclasses moduli "
                "(asoslari).",
                "Ro'yxat elementlarini indeksi bilan birga aylanib chiqish uchun qaysi funksiya "
                "ishlatiladi?",
                "enumerate()",
                ["zip()", "map()", "filter()"],
            ),
            (
                "(Python) Context Managers va Standart kutubxona",
                "with statement chuqur. __enter__ va __exit__ metodlari. contextlib.contextmanager "
                "decorator. collections (Counter, defaultdict, deque, OrderedDict). itertools, "
                "functools foydali funksiyalari.",
                "Context manager yaratishda qaysi ikkita dunder metod ishlatiladi?",
                "__enter__ va __exit__",
                ["__init__ va __del__", "__str__ va __repr__", "__get__ va __set__"],
            ),
            (
                "(Python) Descriptors va Meta Programming",
                "Descriptors tushunchasi (__get__, __set__, __delete__). Data va non-data "
                "descriptors. Metaclasses asoslari. Amaliy: o'z descriptor yozish. Meta programming "
                "qachon kerak.",
                "Python'da barcha klasslarning \"klassi\" (metaclass) nima deb ataladi?",
                "type",
                ["object", "class", "meta"],
            ),
            (
                "(Python) Concurrency — Multithreading",
                "Concurrency vs Parallelism farqi. Threading moduli — Thread yaratish. Lock, RLock, "
                "Semaphore. Race condition va deadlock. GIL (Global Interpreter Lock), "
                "concurrent.futures.ThreadPoolExecutor.",
                "Python'da bir vaqtda faqat bitta thread bayt-kodni bajarishini ta'minlovchi mexanizm "
                "qanday ataladi?",
                "GIL",
                ["Lock", "Semaphore", "Deadlock"],
            ),
            (
                "(Python) Concurrency — Multiprocessing",
                "Process va Thread farqi. multiprocessing moduli. Pool va parallel hisoblash. "
                "Inter-process communication (Queue, Pipe). concurrent.futures.ProcessPoolExecutor.",
                "Jarayonlar (process) o'rtasida ma'lumot almashish uchun qaysi vositalar ishlatiladi?",
                "Queue va Pipe",
                ["Lock va Semaphore", "Thread va GIL", "yield va return"],
            ),
            (
                "(Python) Async I/O — 1-qism (asoslar)",
                "Sinxron va asinxron farqi. asyncio kirish. async va await sintaksisi. Coroutine va "
                "event loop. asyncio.run() va asyncio.sleep(), birinchi async dastur.",
                "Asinxron funksiyani e'lon qilish uchun qaysi kalit so'z ishlatiladi?",
                "async",
                ["await", "yield", "thread"],
            ),
            (
                "(Python) Async I/O — 2-qism (amaliyot)",
                "asyncio.gather(), asyncio.create_task(). aiohttp bilan async HTTP so'rovlar. "
                "aiofiles bilan async fayl o'qish. Async iterators va async context managers. Sync vs "
                "Async vs Threading taqqoslash.",
                "Bir nechta coroutine'ni bir vaqtda parallel bajarish uchun qaysi funksiya "
                "ishlatiladi?",
                "asyncio.gather()",
                ["asyncio.sleep()", "asyncio.run()", "async def"],
            ),
        ],
    },
    {
        "title": "Database — PostgreSQL",
        "lessons": [
            (
                "(Database) Database va PostgreSQL kirish",
                "Database va RDBMS tushunchasi. PostgreSQL nima va afzalliklari (MySQL bilan farqi). "
                "PostgreSQL va pgAdmin o'rnatish. psql buyruq satri va asosiy buyruqlar. Birinchi "
                "database yaratish (CREATE DATABASE).",
                "Yangi ma'lumotlar bazasi yaratish uchun qaysi SQL buyrug'i ishlatiladi?",
                "CREATE DATABASE",
                ["NEW DATABASE", "MAKE DATABASE", "INIT DATABASE"],
            ),
            (
                "(Database) Jadval yaratish, Field turlari va Sequences",
                "CREATE TABLE sintaksisi va Primary Key. Field turlari: int, bigint, decimal, "
                "varchar, text, date, timestamp, boolean, uuid, json/jsonb. SERIAL, BIGSERIAL "
                "(auto-increment) va IDENTITY column. CREATE TABLE AS va SELECT INTO.",
                "PostgreSQL'da avtomatik ortib boruvchi (auto-increment) ustun uchun qaysi tur "
                "ishlatiladi?",
                "SERIAL",
                ["AUTOINC", "IDENTITY_KEY", "INDEX"],
            ),
            (
                "(Database) INSERT va UPSERT",
                "INSERT INTO bilan yozuv qo'shish. Bir nechta yozuvni birga qo'shish (VALUES). "
                "RETURNING ifodasi. UPSERT (INSERT ... ON CONFLICT DO UPDATE / DO NOTHING). Amaliy: "
                "ma'lumot to'plamini bazaga yuklash.",
                "Yozuv mavjud bo'lsa yangilash, bo'lmasa qo'shish uchun qaysi konstruksiya "
                "ishlatiladi?",
                "INSERT ... ON CONFLICT",
                ["UPDATE ... WHERE", "DELETE ... USING", "SELECT ... INTO"],
            ),
            (
                "(Database) SELECT asoslari",
                "SELECT * va aniq ustunlarni tanlash. WHERE bilan filterlash. Operatorlar: =, <>, <, "
                ">, <=, >=. AND, OR, NOT. Column aliases (AS), LIMIT, OFFSET.",
                "Natijalar sonini cheklash uchun qaysi kalit so'z ishlatiladi?",
                "LIMIT",
                ["WHERE", "OFFSET", "AS"],
            ),
            (
                "(Database) UPDATE va DELETE",
                "UPDATE sintaksisi va SET. Bir nechta ustunni birga yangilash. UPDATE ... FROM. "
                "DELETE FROM va WHERE shart bilan. DELETE ... USING (JOIN bilan), TRUNCATE bilan "
                "farqi, RETURNING.",
                "Mavjud yozuvdagi qiymatni o'zgartirish uchun qaysi buyruq ishlatiladi?",
                "UPDATE",
                ["INSERT", "DELETE", "SELECT"],
            ),
            (
                "(Database) Constraints va ALTER TABLE",
                "NOT NULL, UNIQUE, DEFAULT, CHECK. PRIMARY KEY va FOREIGN KEY. ALTER TABLE — ustun "
                "qo'shish/o'chirish. Field turini o'zgartirish. Constraint qo'shish/o'chirish, "
                "RENAME, DROP TABLE.",
                "Ustunga bo'sh (NULL) qiymat kiritilishini taqiqlash uchun qaysi cheklov ishlatiladi?",
                "NOT NULL",
                ["UNIQUE", "DEFAULT", "CHECK"],
            ),
            (
                "(Database) Chuqur SELECT — saralash, qidirish, NULL",
                "ORDER BY (ASC, DESC, NULLS FIRST/LAST). DISTINCT va DISTINCT ON. LIKE, ILIKE "
                "(case-insensitive). IN, NOT IN, BETWEEN. IS NULL, IS NOT NULL, CASE WHEN ... THEN ... "
                "END.",
                "Katta-kichik harflarga sezgir bo'lmagan qidiruv uchun qaysi operator ishlatiladi?",
                "ILIKE",
                ["LIKE", "IN", "BETWEEN"],
            ),
            (
                "(Database) Munosabatlar va JOIN turlari",
                "One-to-One, One-to-Many, Many-to-Many tushunchalari. FOREIGN KEY va ON DELETE "
                "CASCADE. ER diagramma asoslari. INNER JOIN, LEFT JOIN, RIGHT JOIN. FULL OUTER JOIN, "
                "CROSS JOIN, SELF JOIN, table aliases.",
                "Faqat ikkala jadvalda ham mos keluvchi yozuvlarni qaytaruvchi JOIN turi qaysi?",
                "INNER JOIN",
                ["LEFT JOIN", "RIGHT JOIN", "CROSS JOIN"],
            ),
            (
                "(Database) Aggregatsiya, GROUP BY va Set operatorlari",
                "COUNT, SUM, AVG, MIN, MAX. GROUP BY va HAVING. UNION, UNION ALL. INTERSECT va "
                "EXCEPT. Amaliy: hisobotlar yaratish.",
                "GROUP BY natijasini shartga ko'ra filterlash uchun qaysi kalit so'z ishlatiladi?",
                "HAVING",
                ["WHERE", "ORDER BY", "LIMIT"],
            ),
            (
                "(Database) Subquery va CTE",
                "Subquery (ichki so'rovlar). ANY, ALL, EXISTS operatorlari. WITH (CTE) — Common Table "
                "Expression. Murakkab so'rovlarni soddalashtirish. Recursive CTE asoslari.",
                "WITH kalit so'zi yordamida yaratiladigan vaqtinchalik natija to'plami qanday "
                "ataladi?",
                "CTE (Common Table Expression)",
                ["Subquery", "View", "Index"],
            ),
            (
                "(Database) Transaksiyalar, Index va optimizatsiya",
                "Transaksiyalar: BEGIN, COMMIT, ROLLBACK. ACID tamoyillari, SAVEPOINT. Index nima va "
                "qachon kerak. Index turlari (B-tree, Hash, GIN), CREATE INDEX, DROP INDEX. EXPLAIN "
                "ANALYZE bilan so'rov tahlili.",
                "Transaksiyadagi o'zgarishlarni bekor qilish uchun qaysi buyruq ishlatiladi?",
                "ROLLBACK",
                ["COMMIT", "BEGIN", "SAVEPOINT"],
            ),
            (
                "(Database) Python + psycopg2 va yakuniy mini loyiha",
                "psycopg2 o'rnatish va Python'dan ulanish. cursor, execute(), fetchone(), fetchall(). "
                "Parametrlangan so'rovlar (SQL injection himoyasi). Connection pooling asoslari. "
                "Yakuniy mini loyiha: Python + PostgreSQL bilan to'liq CRUD ilova, GitHub'ga yuklash.",
                "SQL so'rovlariga foydalanuvchi kiritgan ma'lumotni xavfsiz qo'shish uchun nima "
                "ishlatiladi?",
                "Parametrlangan so'rovlar",
                ["String concatenation", "f-string bilan to'g'ridan-to'g'ri qo'shish", "eval() funksiyasi"],
            ),
        ],
    },
    {
        "title": "Django, HTML, Jinja, REST Framework va Telegram Bot",
        "lessons": [
            (
                "(Django) Django bilan tanishuv va o'rnatish",
                "Django nima, framework va kutubxona farqi. MVT arxitekturasi (Model-View-Template). "
                "Virtual muhit (venv) yaratish. Django o'rnatish va loyiha yaratish. runserver, loyiha "
                "tuzilishi (manage.py, settings.py, urls.py, wsgi.py).",
                "Django qaysi arxitektura naqshiga asoslangan?",
                "MVT (Model-View-Template)",
                ["MVC (Model-View-Controller)", "MVVM", "Microservices"],
            ),
            (
                "(Django) Sozlamalar va App yaratish",
                "settings.py ni chuqur ko'rib chiqish. INSTALLED_APPS, DATABASES, LANGUAGE_CODE, "
                "TIME_ZONE, DEBUG, ALLOWED_HOSTS. App yaratish (startapp). manage.py buyruqlari "
                "(migrate, createsuperuser, makemigrations).",
                "Yangi Django app yaratish uchun qaysi buyruq ishlatiladi?",
                "python manage.py startapp",
                ["python manage.py createapp", "python manage.py newapp", "python manage.py init"],
            ),
            (
                "(Django) URL va View",
                "URL routing (urls.py) — path(), re_path(). Loyiha va app urls.py larini ulash "
                "(include()). Funksional view (FBV) yozish. HttpResponse qaytarish. URL parametrlari, "
                "name= parametri.",
                "App'ning urls.py faylini asosiy loyiha urls.py'ga ulash uchun qaysi funksiya "
                "ishlatiladi?",
                "include()",
                ["path()", "import()", "connect()"],
            ),
            (
                "(Django) Models — 1-qism (yaratish)",
                "Model class yaratish. Field turlari: CharField, IntegerField, TextField, DateField, "
                "DateTimeField, BooleanField, EmailField, URLField. Field parametrlari. Meta class, "
                "__str__ metodi. makemigrations va migrate.",
                "Model o'zgarishlarini ma'lumotlar bazasiga qo'llash uchun ketma-ket qaysi ikki "
                "buyruq ishlatiladi?",
                "makemigrations va migrate",
                ["startapp va runserver", "collectstatic va migrate", "createsuperuser va migrate"],
            ),
            (
                "(Django) Models — 2-qism (munosabatlar)",
                "ForeignKey (One-to-Many) va on_delete parametri. OneToOneField. ManyToManyField. "
                "related_name va Reverse lookup. Migratsiyalar va munosabatlar, admin panelda "
                "ko'rsatish.",
                "Bir-ko'p (One-to-Many) munosabatni ifodalash uchun qaysi field turi ishlatiladi?",
                "ForeignKey",
                ["OneToOneField", "ManyToManyField", "TextField"],
            ),
            (
                "(Django) Django ORM",
                "QuerySet API: all(), filter(), get(), exclude(), order_by(), count(). first(), "
                "last(), exists(). create(), save(), delete(), update(). Bog'liq ob'ektlar bilan "
                "ishlash. Django shell bilan amaliyot.",
                "Berilgan shartga mos bir nechta obyektni qaytarish uchun QuerySet metodi qaysi?",
                "filter()",
                ["get()", "exists()", "count()"],
            ),
            (
                "(Django) Templates va render() (HTML asoslari bilan)",
                "templates/ papkasi va TEMPLATES sozlamasi. HTML asoslari: <!DOCTYPE>, <html>, "
                "<head>, <body>, h1-h6, p, a, img, ul, ol, div, span. render() funksiyasi va kontekst. "
                "View'dan template'ga ma'lumot uzatish.",
                "View'dan HTML sahifasini kontekst bilan qaytarish uchun qaysi funksiya ishlatiladi?",
                "render()",
                ["redirect()", "HttpResponse()", "include()"],
            ),
            (
                "(Django) DTL — sintaksis va filterlar",
                "DTL (Django Template Language) sintaksisi: {{ }}, {% %}, {# #}. Filterlar: upper, "
                "lower, length, default, date, truncatechars, join. Bir nechta filterlarni "
                "birlashtirish.",
                "Django Template'da izoh yozish uchun qaysi belgi ishlatiladi?",
                "{# #}",
                ["{{ }}", "{% %}", "<!-- -->"],
            ),
            (
                "(Django) DTL — shartlar, sikllar, inheritance",
                "Shartlar: {% if %}, {% elif %}, {% else %}, {% endif %}. Sikllar: {% for %} va "
                "forloop o'zgaruvchisi. Template inheritance: {% extends %}, {% block %}. {% include "
                "%} va {% url %}.",
                "Bir template'ni boshqasidan meros olish (inheritance) uchun qaysi teg ishlatiladi?",
                "{% extends %}",
                ["{% include %}", "{% block %}", "{% url %}"],
            ),
            (
                "(Django) Jinja template tili",
                "Jinja nima va Django'da qachon kerak (DTL bilan farqlari). Sintaksis va asosiy "
                "konstruksiyalar. Django'da Jinja2 backend qo'shish. Macro ({% macro %}) va "
                "kengaytirilgan filterlar.",
                "Jinja'da qayta ishlatiluvchi shablon bo'lagi yaratish uchun qaysi konstruksiya "
                "ishlatiladi?",
                "{% macro %}",
                ["{% block %}", "{% extends %}", "{% include %}"],
            ),
            (
                "(Django) CSS asoslari",
                "CSS sintaksisi va selektorlar (class, id, element, descendant). CSS ulash usullari. "
                "Box model: margin, padding, border, width, height. Rang, font, text formatlash. "
                "Display turlari.",
                "CSS Box model tarkibiga kirmaydigan element qaysi?",
                "font-family",
                ["margin", "padding", "border"],
            ),
            (
                "(Django) Bootstrap va Static fayllar",
                "Bootstrap CDN orqali ulash va asosiy tushunchalar. Grid tizimi. Bootstrap "
                "komponentlari: navbar, card, button, form, modal. STATIC_URL, STATICFILES_DIRS, "
                "{% load static %} ishlatish.",
                "Template ichida statik fayllardan foydalanish uchun avval qaysi teg yuklanadi?",
                "{% load static %}",
                ["{% extends static %}", "{% include static %}", "{% import static %}"],
            ),
            (
                "(Django) Django Admin chuqur",
                "Admin panelni sozlash, ModelAdmin class. list_display, list_filter, search_fields, "
                "ordering. list_editable, list_per_page. fieldsets va readonly_fields. Inline "
                "modellar, custom admin actions.",
                "Admin panelda ro'yxat sahifasida qaysi ustunlar ko'rsatilishini belgilaydigan "
                "atribut qaysi?",
                "list_display",
                ["list_filter", "search_fields", "fieldsets"],
            ),
            (
                "(Django) Forms — 1-qism (Form class)",
                "Django Form class va field turlari. GET va POST so'rovlari. Form'ni template'da "
                "ko'rsatish. Form validatsiyasi (is_valid(), cleaned_data). CSRF himoyasi.",
                "Formadagi ma'lumotlar to'g'riligini tekshirish uchun qaysi metod chaqiriladi?",
                "is_valid()",
                ["clean()", "save()", "validate()"],
            ),
            (
                "(Django) Forms — 2-qism (ModelForm)",
                "ModelForm yaratish va Meta class. ModelForm bilan CRUD (Create, Update). Custom "
                "validatsiya: clean_<field>() va clean() metodlari. Form widgets. Bootstrap bilan "
                "formani chiroyli qilish.",
                "Modelga bevosita bog'langan formani yaratish uchun qaysi klass ishlatiladi?",
                "ModelForm",
                ["Form", "ModelSerializer", "ModelAdmin"],
            ),
            (
                "(Django) Class-Based Views — 1-qism",
                "FBV vs CBV taqqoslash. View base class. TemplateView, RedirectView. ListView va "
                "DetailView. URL bilan ulash (MyView.as_view()), get_context_data() va "
                "get_queryset().",
                "Ro'yxat sahifasini ko'rsatish uchun tayyor Class-Based View qaysi?",
                "ListView",
                ["DetailView", "TemplateView", "RedirectView"],
            ),
            (
                "(Django) Class-Based Views — 2-qism (CRUD)",
                "CreateView, UpdateView, DeleteView. FormView. success_url va get_success_url(). "
                "Mixinlar (LoginRequiredMixin, PermissionRequiredMixin). Mini CRUD ilova.",
                "Faqat tizimga kirgan foydalanuvchilarga view'ni ochish uchun qaysi mixin "
                "ishlatiladi?",
                "LoginRequiredMixin",
                ["PermissionRequiredMixin", "FormView", "UpdateView"],
            ),
            (
                "(Django) Authentication (kirish/chiqish)",
                "django.contrib.auth tizimi va User modeli. Login va Logout view'lar (built-in CBV). "
                "LOGIN_URL, LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL. Password hashing va xavfsizlik.",
                "Django'da autentifikatsiya tizimi qaysi ilova (app) orqali ta'minlanadi?",
                "django.contrib.auth",
                ["django.contrib.admin", "django.contrib.sessions", "django.contrib.messages"],
            ),
            (
                "(Django) Ro'yxatdan o'tish va Authorization",
                "Registration — UserCreationForm. Custom registration form. @login_required decorator "
                "va LoginRequiredMixin. Permissions va Groups. @permission_required decorator, "
                "Password reset.",
                "Funksional view'ni faqat tizimga kirgan foydalanuvchilar uchun cheklash uchun qaysi "
                "decorator ishlatiladi?",
                "@login_required",
                ["@permission_required", "@csrf_exempt", "@api_view"],
            ),
            (
                "(Django) Custom User Model",
                "Django'ning default User modeli kamchiliklari. Custom User Model (AbstractUser vs "
                "AbstractBaseUser). Email bilan login. AUTH_USER_MODEL sozlamasi. Qo'shimcha field "
                "qo'shish.",
                "Loyiha boshida custom user modelini ulash uchun settings.py'da qaysi sozlama "
                "ishlatiladi?",
                "AUTH_USER_MODEL",
                ["USER_MODEL", "DEFAULT_USER", "AUTH_MODEL"],
            ),
            (
                "(Django) Media fayllar (rasm/file upload)",
                "MEDIA_URL va MEDIA_ROOT sozlamalari. ImageField va FileField. Pillow kutubxonasi. "
                "Form orqali fayl yuklash (enctype=\"multipart/form-data\"). Rasm validatsiyasi va "
                "o'lcham cheklash.",
                "Rasm fayllari bilan ishlash uchun Django qaysi tashqi kutubxonaga tayanadi?",
                "Pillow",
                ["NumPy", "OpenCV", "Matplotlib"],
            ),
            (
                "(Django) Pagination, Search va Filter",
                "Paginator class (Page, paginate_by). CBV'da paginate_by parametri. Bootstrap "
                "pagination. Qidiruv funksiyasi (Q obyektlari bilan). GET parametrlari, filtering va "
                "sortlash.",
                "Katta ro'yxatni sahifalarga bo'lib ko'rsatish uchun qaysi Django klassi ishlatiladi?",
                "Paginator",
                ["Filter", "QuerySet", "Serializer"],
            ),
            (
                "(Django) Django ORM chuqur",
                "Q obyektlari (murakkab OR/AND so'rovlar). F obyektlari. select_related va "
                "prefetch_related (N+1 muammosi). annotate va aggregate (Count, Sum, Avg). values() "
                "va values_list().",
                "ForeignKey bog'lanishlarida N+1 muammosini oldini olish uchun qaysi metod "
                "ishlatiladi?",
                "select_related()",
                ["annotate()", "aggregate()", "values()"],
            ),
            (
                "(Django) Email, Cache, Sessions va xavfsizlik",
                "Email yuborish (send_mail, SMTP sozlash). Sessions ishlatish. Cookies bilan ishlash. "
                "Cache framework asoslari. Xavfsizlik: SQL injection, XSS, CSRF, .env fayl, "
                "DEBUG=False, ALLOWED_HOSTS.",
                "Production muhitida xavfsizlik uchun DEBUG sozlamasi qanday bo'lishi kerak?",
                "False",
                ["True", "None", "Auto"],
            ),
            (
                "(Django) REST API va DRF kirish",
                "REST API tamoyillari (HTTP metodlari: GET, POST, PUT, PATCH, DELETE). Status kodlari "
                "(200, 201, 400, 401, 403, 404, 500). JSON formati. DRF o'rnatish, Browsable API.",
                "Yangi resurs muvaffaqiyatli yaratilganda qaytariladigan HTTP status kodi qaysi?",
                "201",
                ["200", "204", "404"],
            ),
            (
                "(Django) Serializers — 1-qism",
                "Serializer nima va qachon kerak. Serializer class va field turlari. serialize va "
                "deserialize jarayoni. ModelSerializer (Meta class, fields, exclude). read_only_fields "
                "va write_only_fields.",
                "Modelga asoslangan serializer yaratish uchun DRF'da qaysi klass ishlatiladi?",
                "ModelSerializer",
                ["ModelForm", "ModelAdmin", "ModelView"],
            ),
            (
                "(Django) Serializers — 2-qism (validatsiya va nested)",
                "Serializer validatsiyasi: validate_<field>() va validate(). raise "
                "serializers.ValidationError. create() va update() metodlarini override qilish. "
                "Nested serializerlar. SerializerMethodField.",
                "Serializer'da bitta maydonni maxsus tekshirish uchun qaysi nomlash qoidasi "
                "ishlatiladi?",
                "validate_<field>()",
                ["check_<field>()", "clean_<field>()", "verify_<field>()"],
            ),
            (
                "(Django) APIView va Generic Views",
                "@api_view decorator (FBV uslubi). Request va Response obyektlari. APIView class (CBV "
                "uslubi). Generic Views: ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, "
                "DestroyAPIView.",
                "Funksional API view yaratishda qaysi decorator ishlatiladi?",
                "@api_view",
                ["@login_required", "@action", "@permission_classes"],
            ),
            (
                "(Django) ViewSet va Routers + GitHub jamoa ishi",
                "ModelViewSet va ReadOnlyModelViewSet. Router bilan URL avtomatizatsiyasi "
                "(DefaultRouter, SimpleRouter). @action decorator bilan custom endpoint. GitHub: "
                "branch, checkout, merge, Pull Request, kod review.",
                "ViewSet'lar uchun URL'larni avtomatik generatsiya qiladigan DRF klassi qaysi?",
                "DefaultRouter",
                ["URLPatterns", "APIView", "ModelSerializer"],
            ),
            (
                "(Django) Authentication (DRF)",
                "DRF authentication tushunchasi. SessionAuthentication va BasicAuthentication. "
                "TokenAuthentication. JWT (djangorestframework-simplejwt), token olish/yangilash. "
                "Token blacklist va logout.",
                "Zamonaviy DRF loyihalarida token-based autentifikatsiya uchun qaysi kutubxona keng "
                "qo'llaniladi?",
                "djangorestframework-simplejwt",
                ["django-cors-headers", "django-filter", "drf-spectacular"],
            ),
            (
                "(Django) Permissions",
                "DRF permissions tushunchasi. AllowAny, IsAuthenticated, IsAdminUser. "
                "IsAuthenticatedOrReadOnly, DjangoModelPermissions. Object-level permissions. Custom "
                "Permission class yozish.",
                "Faqat tizimga kirgan foydalanuvchilarga ruxsat beruvchi standart DRF permission "
                "klassi qaysi?",
                "IsAuthenticated",
                ["AllowAny", "IsAdminUser", "IsAuthenticatedOrReadOnly"],
            ),
            (
                "(Django) Filtering, Search, Ordering, Pagination",
                "SearchFilter (qidiruv). OrderingFilter (saralash). django-filter kutubxonasi "
                "(DjangoFilterBackend, filterset_fields). PageNumberPagination va "
                "LimitOffsetPagination.",
                "Model maydonlari bo'yicha avtomatik filterlashni ta'minlovchi kutubxona qaysi?",
                "django-filter",
                ["django-cors-headers", "djangorestframework-simplejwt", "Pillow"],
            ),
            (
                "(Django) Throttling, CORS va Swagger + GitHub konflikt",
                "Rate limiting (Throttling) — AnonRateThrottle, UserRateThrottle. django-cors-headers "
                "o'rnatish va sozlash. Swagger/OpenAPI hujjatlari (drf-spectacular). GitHub: merge "
                "conflict yechish, git rebase asoslari.",
                "Boshqa domendan (frontend) API'ga so'rov yuborishga ruxsat berish uchun qaysi "
                "kutubxona ishlatiladi?",
                "django-cors-headers",
                ["django-filter", "drf-spectacular", "djangorestframework-simplejwt"],
            ),
            (
                "(Django) Telegram Bot — 1-qism (Aiogram asoslari)",
                "Telegram bot nima va qanday ishlaydi. BotFather orqali bot yaratish va token olish. "
                "Aiogram o'rnatish. Birinchi bot: /start, /help buyruqlari, handler'lar. Polling "
                "rejimi, Inline va Reply tugmalar.",
                "Telegram'da yangi bot yaratish va token olish uchun qaysi maxsus bot ishlatiladi?",
                "BotFather",
                ["Aiogram", "ngrok", "webhook"],
            ),
            (
                "(Django) Telegram Bot — 2-qism (Django + ngrok + Webhook)",
                "Polling vs Webhook farqi (production'da webhook). Django + Aiogram integratsiyasi. "
                "Bot uchun view yaratish (POST endpoint). ngrok o'rnatish va ishga tushirish. HTTPS "
                "URL olish va Telegram'ga webhook o'rnatish.",
                "Lokal serverni vaqtinchalik ochiq HTTPS manzilga chiqarish uchun qaysi vosita "
                "ishlatiladi?",
                "ngrok",
                ["BotFather", "Aiogram", "Certbot"],
            ),
            (
                "(Django) Telegram Bot — 3-qism (Django ORM bilan to'liq bot)",
                "Bot orqali Django modellariga ma'lumot qo'shish. Django ORM'ni async kontekstda "
                "ishlatish (sync_to_async). FSM (Finite State Machine) — ko'p bosqichli dialog. "
                "Foydalanuvchi ma'lumotlarini bazaga saqlash.",
                "Sinxron Django ORM chaqiruvlarini async botda ishlatish uchun qaysi funksiya "
                "ishlatiladi?",
                "sync_to_async",
                ["async_to_sync", "asyncio.run", "await_orm"],
            ),
        ],
    },
    {
        "title": "Deployment — Linux server",
        "lessons": [
            (
                "(Deploy) Linux va VPS asoslari",
                "Linux Ubuntu terminal asosiy buyruqlari (ls, cd, pwd, mkdir, rm, cp, mv, cat, nano). "
                "Fayl tizimi va ruxsatlar (chmod, chown), foydalanuvchilar (sudo, adduser). Paketlar "
                "boshqaruvi (apt update, apt install). VPS sotib olish, SSH orqali ulanish, firewall "
                "(ufw).",
                "Fayl/papka ruxsatlarini o'zgartirish uchun Linux buyrug'i qaysi?",
                "chmod",
                ["chown", "sudo", "apt"],
            ),
            (
                "(Deploy) Server tayyorlash va loyihani ishga tushirish",
                "Server'ga paketlar o'rnatish: Python, pip, venv, PostgreSQL, Nginx, Git. Loyihani "
                "GitHub'dan klonlash, venv va requirements.txt o'rnatish. Production sozlamalari "
                "(DEBUG=False, ALLOWED_HOSTS, STATIC_ROOT), migrate, collectstatic. Gunicorn, Nginx "
                "reverse proxy, systemd service.",
                "Production muhitida Django ilovasini WSGI serveri sifatida ishga tushirish uchun "
                "ko'pincha qaysi vosita ishlatiladi?",
                "Gunicorn",
                ["runserver", "ngrok", "psql"],
            ),
            (
                "(Deploy) Domain, SSL, Telegram Bot Webhook va monitoring",
                "Domen ulash: domen sotib olish va DNS sozlash (A record VPS IP'ga). Nginx config'da "
                "server_name, SSL sertifikat (Certbot, Let's Encrypt), HTTPS. .env fayl va "
                "python-decouple. Telegram bot webhook'ni production'da o'rnatish. Loglar va "
                "monitoring, server xavfsizligi.",
                "Bepul SSL sertifikat olish uchun keng qo'llaniladigan xizmat qaysi?",
                "Let's Encrypt / Certbot",
                ["ngrok", "BotFather", "pgAdmin"],
            ),
        ],
    },
]

LESSON_DURATION_MINUTES = 90


class Command(BaseCommand):
    help = "Bitta to'liq dasturlash kursini (Scratch/Python/PostgreSQL/Django, 96 dars, testlar bilan) yaratadi."

    @transaction.atomic
    def handle(self, *args, **options):
        teacher, created = User.objects.get_or_create(
            username=TEACHER["username"],
            defaults={**TEACHER, "role": User.Role.TEACHER, "is_phone_verified": True},
        )
        if created:
            teacher.set_password(DEFAULT_PASSWORD)
            teacher.save()
        self.stdout.write(f"Teacher: {teacher.username} ({'created' if created else 'exists'})")

        student_objs = {}
        for data in STUDENTS:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={**data, "role": User.Role.STUDENT, "is_phone_verified": True},
            )
            if created:
                user.set_password(DEFAULT_PASSWORD)
                user.save()
            student_objs[data["username"]] = user
            self.stdout.write(f"Student: {user.username} ({'created' if created else 'exists'})")

        # Faqat bitta kurs qolishi kerak — boshqa nomdagi eski kurslarni (agar bo'lsa) tozalaymiz.
        # Bu kursning o'zi allaqachon mavjud bo'lsa, uni qayta yaratmaymiz — aks holda har
        # restart'da ID'lar siljib, talabalarning enrollment/progress ma'lumotlari yo'qoladi.
        deleted_count, _ = Course.objects.exclude(title=COURSE_TITLE).delete()
        if deleted_count:
            self.stdout.write(f"Boshqa eski kurslar tozalandi: {deleted_count} ta obyekt o'chirildi.")

        course, course_created = Course.objects.get_or_create(
            title=COURSE_TITLE,
            defaults={
                "description": COURSE_DESCRIPTION,
                "teacher": teacher,
                "level": Course.Level.BEGINNER,
                "price": 1500000,
                "is_published": True,
            },
        )
        self.stdout.write(f"Course: {course.title} ({'created' if course_created else 'exists'})")

        if not course_created:
            self.stdout.write(self.style.SUCCESS("Kurs allaqachon mavjud — modul/dars/test qayta yaratilmadi."))
            javohir = student_objs.get("javohir")
            if javohir:
                Enrollment.objects.get_or_create(student=javohir, course=course, defaults={"progress_percent": 15})
            self.stdout.write(self.style.SUCCESS("Demo ma'lumotlar tayyor."))
            self.stdout.write(f"Barcha demo foydalanuvchilar paroli: {DEFAULT_PASSWORD}")
            return

        lesson_index = 0
        for m_order, module_data in enumerate(MODULES):
            module = Module.objects.create(course=course, title=module_data["title"], order=m_order)
            for l_order, (title, content, question_text, correct, wrong_choices) in enumerate(
                module_data["lessons"]
            ):
                lesson = Lesson.objects.create(
                    module=module,
                    title=title,
                    content_type=Lesson.ContentType.TEXT,
                    content=content,
                    duration_minutes=LESSON_DURATION_MINUTES,
                    order=l_order,
                    is_free_preview=(l_order == 0),
                )

                question = Question.objects.create(lesson=lesson, text=question_text, order=0)
                all_choices = [correct, *wrong_choices]
                correct_position = lesson_index % len(all_choices)
                ordered_choices = wrong_choices.copy()
                ordered_choices.insert(correct_position, correct)
                for c_order, choice_text in enumerate(ordered_choices):
                    Choice.objects.create(
                        question=question,
                        text=choice_text,
                        is_correct=(choice_text == correct),
                        order=c_order,
                    )

                lesson_index += 1

        self.stdout.write(self.style.SUCCESS(f"{lesson_index} ta dars va test savoli yaratildi."))

        javohir = student_objs.get("javohir")
        if javohir:
            enrollment, created = Enrollment.objects.get_or_create(student=javohir, course=course)
            if created:
                enrollment.progress_percent = 15
                enrollment.save(update_fields=["progress_percent"])
            self.stdout.write(f"Enrollment: javohir -> {course.title}")

        self.stdout.write(self.style.SUCCESS("Demo ma'lumotlar tayyor."))
        self.stdout.write(f"Barcha demo foydalanuvchilar paroli: {DEFAULT_PASSWORD}")
