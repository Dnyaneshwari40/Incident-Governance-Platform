from core.baseline_engine import BaselineEngine
from core.stress_engine import StressEngine
from core.severity_engine import SeverityEngine
from core.action_engine import ActionEngine


class IncidentOrchestrator:
    """
    Coordinates:
    - Rolling baseline computation
    - Stress scoring
    - Severity inference
    - Action recommendation
    - Explainability reasoning
    """

    @staticmethod
    def process(current_incident, window_incidents):
        """
        current_incident: Incident model instance
        window_incidents: queryset of Incident instances (last 10 min)
        """

        # Convert queryset to list (safe for len + iteration)
        window_list = list(window_incidents)
        window_size = len(window_list)

        # 1️⃣ Compute rolling baseline
        baseline = BaselineEngine.compute(window_list)

        # 2️⃣ Compute stress score
        stress_score = StressEngine.compute(current_incident, baseline)

        # 3️⃣ Infer severity
        severity = SeverityEngine.infer(
            final_score=current_incident.final_score,
            stress_score=stress_score,
            window_size=window_size
        )

        # 4️⃣ Recommend action
        action = ActionEngine.recommend(severity)

        # 5️⃣ Generate explainable reason
        reason = (
            f"Final score={current_incident.final_score:.2f}, "
            f"Stress score={stress_score:.2f}, "
            f"Window size={window_size}"
        )

        return {
            "severity": severity,
            "action": action,
            "stress_score": stress_score,
            "reason": reason,
        }
