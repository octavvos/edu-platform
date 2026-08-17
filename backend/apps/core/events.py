"""
TZ 5.1 / D-07: modullar bir-birining modellariga to'g'ridan-to'g'ri
murojaat qilmaydi — domain event orqali bog'lanadi. Masalan `payments`
moduli `enrollment`ni import qilmaydi: u faqat `payment_succeeded`
event chiqaradi, `enrollment` esa unga obuna bo'ladi.

MVP uchun sodda, jarayon ichidagi (in-process) sinxron dispatcher.
Kelajakda Celery/queue orqali asinxron qilish uchun `emit()` ning
signature'i o'zgarmaydi — faqat implementatsiyasi almashadi.
"""

import logging

logger = logging.getLogger(__name__)

_HANDLERS: dict[str, list] = {}


def subscribe(event_name):
    """Dekorator: funksiyani `event_name` hodisasiga obuna qiladi."""

    def decorator(func):
        _HANDLERS.setdefault(event_name, []).append(func)
        return func

    return decorator


def emit(event_name, **payload):
    """Hodisani chiqaradi — barcha obuna bo'lgan handler'larni chaqiradi."""
    for handler in _HANDLERS.get(event_name, []):
        try:
            handler(**payload)
        except Exception:
            logger.exception("Event handler failed: %s -> %s", event_name, handler)
