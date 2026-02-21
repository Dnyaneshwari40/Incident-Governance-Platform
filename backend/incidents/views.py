from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from services.incident_service import IncidentService
from incidents.models import Incident
from core.escalation_engine import EscalationEngine


# -----------------------------
# 1️⃣ Process Incident
# -----------------------------
@api_view(["POST"])
def process_incident(request):
    data = request.data
    result = IncidentService.process_incident(data)
    return Response(result)


# -----------------------------
# 2️⃣ System Metrics API
# -----------------------------
@api_view(["GET"])
def system_metrics(request):

    now = timezone.now()
    last_24h = now - timedelta(hours=24)

    total_incidents = Incident.objects.count()
    open_incidents = Incident.objects.filter(status="OPEN").count()

    critical_last_24h = Incident.objects.filter(
        severity="CRITICAL",
        created_at__gte=last_24h
    ).count()

    # Stress Average
    stress_values = Incident.objects.exclude(stress_score__isnull=True)

    if stress_values.exists():
        avg_stress = round(
            sum(i.stress_score for i in stress_values) / stress_values.count(),
            2
        )
    else:
        avg_stress = 0

    # MTTA
    acknowledged_incidents = Incident.objects.exclude(
        acknowledged_at__isnull=True
    )

    if acknowledged_incidents.exists():
        total_ack_time = sum(
            (i.acknowledged_at - i.created_at).total_seconds()
            for i in acknowledged_incidents
        )
        mtta = round(total_ack_time / acknowledged_incidents.count() / 60, 2)
    else:
        mtta = 0

    # MTTR
    resolved_incidents = Incident.objects.exclude(
        resolved_at__isnull=True
    )

    if resolved_incidents.exists():
        total_resolve_time = sum(
            (i.resolved_at - i.created_at).total_seconds()
            for i in resolved_incidents
        )
        mttr = round(total_resolve_time / resolved_incidents.count() / 60, 2)
    else:
        mttr = 0

    escalation_active, escalation_message = EscalationEngine.check_escalation()

    return Response({
        "total_incidents": total_incidents,
        "open_incidents": open_incidents,
        "critical_last_24h": critical_last_24h,
        "average_stress_score": avg_stress,
        "mtta_minutes": mtta,
        "mttr_minutes": mttr,
        "escalation_active": escalation_active,
        "escalation_message": escalation_message,
    })


# -----------------------------
# 3️⃣ Acknowledge Incident
# -----------------------------
@api_view(["POST"])
def acknowledge_incident(request, incident_id):

    try:
        incident = Incident.objects.get(id=incident_id)
    except Incident.DoesNotExist:
        return Response(
            {"error": "Incident not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if incident.status == "RESOLVED":
        return Response(
            {"error": "Resolved incidents cannot be modified"},
            status=status.HTTP_400_BAD_REQUEST
        )

    incident.status = "ACKNOWLEDGED"
    incident.acknowledged_at = timezone.now()
    incident.save()

    return Response({
        "message": "Incident acknowledged",
        "incident_id": incident.id,
        "status": incident.status,
    })


# -----------------------------
# 4️⃣ Resolve Incident
# -----------------------------
@api_view(["POST"])
def resolve_incident(request, incident_id):

    try:
        incident = Incident.objects.get(id=incident_id)
    except Incident.DoesNotExist:
        return Response(
            {"error": "Incident not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if incident.status == "RESOLVED":
        return Response(
            {"error": "Incident already resolved"},
            status=status.HTTP_400_BAD_REQUEST
        )

    incident.status = "RESOLVED"
    incident.resolved_at = timezone.now()
    incident.save()

    return Response({
        "message": "Incident resolved",
        "incident_id": incident.id,
        "status": incident.status,
    })


# -----------------------------
# 5️⃣ Dashboard View (HTML)
# -----------------------------
def dashboard_view(request):

    now = timezone.now()
    last_24h = now - timedelta(hours=24)

    total_incidents = Incident.objects.count()
    open_incidents = Incident.objects.filter(status="OPEN").count()

    critical_last_24h = Incident.objects.filter(
        severity="CRITICAL",
        created_at__gte=last_24h
    ).count()

    # MTTA
    acknowledged_incidents = Incident.objects.exclude(
        acknowledged_at__isnull=True
    )

    if acknowledged_incidents.exists():
        total_ack_time = sum(
            (i.acknowledged_at - i.created_at).total_seconds()
            for i in acknowledged_incidents
        )
        mtta = round(total_ack_time / acknowledged_incidents.count() / 60, 2)
    else:
        mtta = 0

    # MTTR
    resolved_incidents = Incident.objects.exclude(
        resolved_at__isnull=True
    )

    if resolved_incidents.exists():
        total_resolve_time = sum(
            (i.resolved_at - i.created_at).total_seconds()
            for i in resolved_incidents
        )
        mttr = round(total_resolve_time / resolved_incidents.count() / 60, 2)
    else:
        mttr = 0

    escalation_active, _ = EscalationEngine.check_escalation()

    recent_incidents = Incident.objects.order_by("-created_at")[:10]

    # Severity Distribution
    severity_counts = {
        "LOW": Incident.objects.filter(severity="LOW").count(),
        "HIGH": Incident.objects.filter(severity="HIGH").count(),
        "CRITICAL": Incident.objects.filter(severity="CRITICAL").count(),
    }

    return render(request, "dashboard.html", {
        "total_incidents": total_incidents,
        "open_incidents": open_incidents,
        "critical_last_24h": critical_last_24h,
        "escalation_active": escalation_active,
        "mtta": mtta,
        "mttr": mttr,
        "recent_incidents": recent_incidents,
        "severity_counts": severity_counts,
    })

# -----------------------------
# Incident List View
# -----------------------------
def incident_list_view(request):

    incidents = Incident.objects.order_by("-created_at")

    return render(request, "incident_list.html", {
        "incidents": incidents
    })


# -----------------------------
# Health Check Endpoint
# -----------------------------
@api_view(["GET"])
def health_check(request):

    return Response({
        "status": "healthy",
        "service": "Incident Governance Platform",
        "database": "connected"
    })