from django.urls import path
from .views import (
    process_incident,
    system_metrics,
    acknowledge_incident,
    resolve_incident,
)

urlpatterns = [
    path("incident/", process_incident),
    path("metrics/", system_metrics),
    path("incident/<int:incident_id>/ack/", acknowledge_incident),
    path("incident/<int:incident_id>/resolve/", resolve_incident),
]

