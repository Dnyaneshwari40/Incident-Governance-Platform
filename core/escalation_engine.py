from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from incidents.models import Incident


class EscalationEngine:
    """
    Detects systemic escalation events.
    If multiple CRITICAL incidents occur within
    configured time window → trigger escalation.
    """

    @staticmethod
    def check_escalation():
        """
        Returns:
            (bool, str)
            escalation_active, escalation_message
        """

        window_minutes = settings.ESCALATION_WINDOW_MINUTES
        threshold = settings.ESCALATION_THRESHOLD

        window_start = timezone.now() - timedelta(minutes=window_minutes)

        critical_count = Incident.objects.filter(
            severity="CRITICAL",
            created_at__gte=window_start
        ).count()

        if critical_count >= threshold:
            return True, (
                f"{critical_count} critical incidents detected "
                f"in last {window_minutes} minutes"
            )

        return False, None
