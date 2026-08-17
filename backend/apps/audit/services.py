from .models import AuditLog


def log_action(*, actor, action: str, object_type: str, object_id="", before=None, after=None,
                ip_address=None, reason=""):
    return AuditLog.objects.create(
        actor=actor, action=action, object_type=object_type, object_id=str(object_id),
        before=before or {}, after=after or {}, ip_address=ip_address, reason=reason,
    )
