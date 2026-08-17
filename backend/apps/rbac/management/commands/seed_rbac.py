from django.core.management.base import BaseCommand

from apps.rbac.models import Permission, Role

PERMISSIONS = [
    ("course.view", "Kursni ko'rish"),
    ("course.create", "Kurs yaratish"),
    ("course.edit_own", "O'z kursini tahrirlash"),
    ("course.edit_any", "Istalgan kursni tahrirlash"),
    ("course.publish", "Kursni nashr qilish"),
    ("course.moderate", "Kurs moderatsiyasi"),
    ("assignment.grade", "Uy vazifasiga baho qo'yish"),
    ("payment.view_own", "O'z to'lovlarini ko'rish"),
    ("payment.view_any", "Barcha to'lovlarni ko'rish"),
    ("payment.refund", "To'lovni qaytarish"),
    ("user.block", "Foydalanuvchini bloklash"),
    ("user.impersonate", "Foydalanuvchi nomidan kirish"),
    ("role.assign", "Rol tayinlash"),
    ("report.view", "Hisobotlarni ko'rish"),
    ("settings.manage", "Tizim sozlamalarini boshqarish"),
]

# TZ 3.2-band (huquqlar matritsasi) asosida
ROLE_PERMISSIONS = {
    "student": ["course.view", "payment.view_own"],
    "teacher": [
        "course.view", "course.create", "course.edit_own",
        "assignment.grade", "payment.view_own",
    ],
    "mentor": ["course.view", "assignment.grade"],
    "admin": [
        "course.view", "course.edit_any", "course.publish", "course.moderate",
        "assignment.grade", "payment.view_any", "payment.refund",
        "user.block", "report.view",
    ],
    "super_admin": [codename for codename, _ in PERMISSIONS],
}


class Command(BaseCommand):
    help = "RBAC: standart Permission va Role'larni (3.2-bo'lim, huquqlar matritsasi) yaratadi."

    def handle(self, *args, **options):
        perm_objs = {}
        for codename, description in PERMISSIONS:
            perm, created = Permission.objects.get_or_create(
                codename=codename, defaults={"description": description}
            )
            perm_objs[codename] = perm
            if created:
                self.stdout.write(f"Permission: {codename} (created)")

        for role_name, codenames in ROLE_PERMISSIONS.items():
            role, created = Role.objects.get_or_create(name=role_name)
            role.permissions.set([perm_objs[c] for c in codenames])
            self.stdout.write(f"Role: {role_name} ({'created' if created else 'updated'}, {len(codenames)} ta huquq)")

        self.stdout.write(self.style.SUCCESS("RBAC seed tayyor."))
