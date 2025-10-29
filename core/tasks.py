from celery import shared_task
from django.utils import timezone
from core.models import UserSession
import logging

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    autoretry_for=(Exception,),  # retry on *any* uncaught exception
    retry_backoff=True,          # exponential backoff: 1s, 2s, 4s, 8s...
    retry_jitter=True,           # adds random jitter to avoid thundering herd
    retry_kwargs={'max_retries': 5},
)
def deactivate_expired_sessions(self):
    try:
        now = timezone.now()
        expired = UserSession.objects.filter(is_active=True, expires_at__lt=now)
        count = expired.update(is_active=False)
        logger.warning(f"[Celery] Deactivated {count} expired sessions at {now}")
        return count
    except Exception as e:
        logger.error(f"[Celery] Task failed: {e}, retrying...")
        raise self.retry(exc=e)

