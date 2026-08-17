import uuid

from django.db import models


class BaseModel(models.Model):
    """
    TZ 5.5.1 D-01/D-02: UUID primary key va nullable organization_id
    barcha asosiy modellarda — B2B/SSO keyin qo'shilganda schema
    qayta yozilmasligi uchun.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_id = models.UUIDField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
