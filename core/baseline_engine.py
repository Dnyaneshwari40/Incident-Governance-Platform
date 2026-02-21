import statistics


class BaselineEngine:
    """
    Computes rolling statistical baseline from recent incidents.
    """

    @staticmethod
    def compute(window_incidents):
        """
        window_incidents: list of incident objects or dicts
        Must contain:
            - cpu_percent
            - rss_MB
            - stack_latency_ms
        """

        if not window_incidents:
            return None

        cpu_values = [float(i.cpu_percent) for i in window_incidents]
        memory_values = [float(i.rss_MB) for i in window_incidents]
        latency_values = [float(i.stack_latency_ms) for i in window_incidents]

        baseline = {}

        # CPU
        baseline["cpu_mean"] = statistics.mean(cpu_values)
        baseline["cpu_std"] = (
            statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0
        )

        # Memory
        baseline["memory_mean"] = statistics.mean(memory_values)
        baseline["memory_std"] = (
            statistics.stdev(memory_values) if len(memory_values) > 1 else 0
        )

        # Latency
        baseline["latency_mean"] = statistics.mean(latency_values)
        baseline["latency_std"] = (
            statistics.stdev(latency_values) if len(latency_values) > 1 else 0
        )

        return baseline
