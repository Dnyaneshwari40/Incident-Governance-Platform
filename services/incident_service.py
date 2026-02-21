from datetime import timedelta
from django.utils import timezone

from core.orchestrator import IncidentOrchestrator
from core.escalation_engine import EscalationEngine
from incidents.models import Incident


class IncidentService:
    """
    Service layer:
    - Saves raw incident
    - Fetches rolling window
    - Runs adaptive decision engine
    - Stores decision output
    - Checks system-wide escalation
    - Returns structured response
    """

    ROLLING_WINDOW_MINUTES = 10

    @staticmethod
    def process_incident(data):

        # 1️⃣ Save raw incident first
        incident = Incident.objects.create(
            cpu_percent=data["cpu_percent"],
            rss_MB=data["rss_MB"],
            stack_latency_ms=data["stack_latency_ms"],
            final_score=data["final_score"],
        )

        # 2️⃣ Fetch rolling window incidents
        window_start = timezone.now() - timedelta(
            minutes=IncidentService.ROLLING_WINDOW_MINUTES
        )

        window_incidents = Incident.objects.filter(
            created_at__gte=window_start
        )

        # 3️⃣ Run adaptive decision engine
        orchestrator = IncidentOrchestrator()
        decision_output = orchestrator.process(
            incident,
            window_incidents
        )

        # 4️⃣ Update incident with decision results
        incident.severity = decision_output.get("severity")
        incident.recommended_action = decision_output.get("action")
        incident.stress_score = decision_output.get("stress_score")
        incident.reason = decision_output.get("reason")
        incident.save()

        # 5️⃣ Check system-wide escalation
        escalation_active, escalation_message = EscalationEngine.check_escalation()

        # 6️⃣ Return structured response
        return {
            "incident_id": incident.id,
            "severity": incident.severity,
            "recommended_action": incident.recommended_action,
            "stress_score": incident.stress_score,
            "reason": incident.reason,
            "status": incident.status,
            "escalation_active": escalation_active,
            "escalation_message": escalation_message,
        }
