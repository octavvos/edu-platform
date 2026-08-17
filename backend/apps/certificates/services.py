import logging

from apps.core.events import emit

from .models import Certificate

logger = logging.getLogger(__name__)


def issue_certificate(*, enrollment) -> Certificate:
    """
    G-04: kurs 100% tugatilganda avtomatik chaqiriladi.

    G-06: PDF shabloni (logo/imzo/matn/fon) — WeasyPrint orqali render
    qilish MVP'ning shu bosqichida ulanmagan (qo'shimcha system
    kutubxonalar talab qiladi). Certificate + QR-kod bilan
    verifikatsiya (G-05) ishlaydi; PDF generatsiyasi keyingi bosqichda
    shu funksiya ichiga qo'shiladi — API/model o'zgarmaydi.
    """
    certificate, created = Certificate.objects.get_or_create(enrollment=enrollment)
    if created:
        emit("certificate_issued", certificate_id=str(certificate.id), user_id=str(enrollment.student_id))
        logger.info("Certificate issued: %s", certificate.code)
    return certificate
