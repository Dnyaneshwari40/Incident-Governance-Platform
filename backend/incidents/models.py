from django.db import models


class Incident(models.Model):
    """
    Stores raw incident metrics,
    adaptive severity decision,
    lifecycle state,
    and explainability.
    """

    # ---- Raw Metrics ----
    cpu_percent = models.FloatField()
    rss_MB = models.FloatField()
    stack_latency_ms = models.FloatField()
    final_score = models.FloatField()

    # ---- Decision Output ----
    severity = models.CharField(max_length=20, blank=True, null=True)
    recommended_action = models.CharField(max_length=100, blank=True, null=True)
    stress_score = models.FloatField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)

    # ---- Lifecycle ----
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("ACKNOWLEDGED", "Acknowledged"),
        ("RESOLVED", "Resolved"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="OPEN",
    )

    acknowledged_at = models.DateTimeField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    # ---- Timestamp ----
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Incident {self.id} - {self.severity} - {self.status}"
