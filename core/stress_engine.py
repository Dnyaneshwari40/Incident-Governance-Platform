class StressEngine:
    """
    Computes deviation-based stress score for an incident
    using rolling statistical baseline.
    """

    @staticmethod
    def compute(current_incident, baseline):
        """
        current_incident: single incident object
        baseline: dictionary from BaselineEngine
        """

        if not baseline:
            return 0

        total_stress = 0

        # CPU Stress
        total_stress += StressEngine._metric_stress(
            current_incident.cpu_percent,
            baseline["cpu_mean"],
            baseline["cpu_std"],
        )

        # Memory Stress
        total_stress += StressEngine._metric_stress(
            current_incident.rss_MB,
            baseline["memory_mean"],
            baseline["memory_std"],
        )

        # Latency Stress
        total_stress += StressEngine._metric_stress(
            current_incident.stack_latency_ms,
            baseline["latency_mean"],
            baseline["latency_std"],
        )

        return total_stress

    @staticmethod
    def _metric_stress(value, mean, std):
        """
        Calculate stress for a single metric.
        """

        if std == 0:
            return 0

        if value > mean + 2 * std:
            return 2
        elif value > mean + 1 * std:
            return 1
        else:
            return 0
