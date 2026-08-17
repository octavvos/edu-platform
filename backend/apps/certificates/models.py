import secrets
import uuid

from django.db import models


def generate_code():
    return secrets.token_hex(8).upper()


class Certificate(models.Model):
    """G-04..G-06: kurs 100% tugatilgan va yakuniy test o'tilgan holda avtomatik generatsiya."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.OneToOneField(
        "enrollments.Enrollment", on_delete=models.CASCADE, related_name="certificate",
    )
    code = models.CharField(max_length=32, unique=True, default=generate_code)
    pdf_file = models.FileField(upload_to="certificates/", null=True, blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate({self.code})"
