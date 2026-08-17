import logging

from .models import Notification

logger = logging.getLogger(__name__)


def notify(*, user, type: str, title: str, body: str = "") -> Notification:
    notification = Notification.objects.create(user=user, type=type, title=title, body=body)
    logger.info("[NOTIFY STUB] %s -> %s: %s", user, type, title)
    return notification
