class SeverityEngine:
    """
    Combines confidence score and stress score
    to determine final severity.
    """

    MIN_WINDOW_SIZE = 30

    @staticmethod
    def infer(final_score, stress_score, window_size):
        """
        final_score: float
        stress_score: int
        window_size: int
        """

        # ------------------------
        # Bootstrapping Phase
        # ------------------------
        if window_size < SeverityEngine.MIN_WINDOW_SIZE:
            return SeverityEngine._fallback_severity(final_score)

        # ------------------------
        # Adaptive Phase
        # ------------------------

        # Low confidence
        if final_score < 0.3:
            return "LOW"

        # Medium confidence
        if 0.3 <= final_score < 0.7:
            if stress_score >= 2:
                return "HIGH"
            return "MEDIUM"

        # High confidence
        if final_score >= 0.7:
            if stress_score >= 3:
                return "CRITICAL"
            elif stress_score >= 1:
                return "HIGH"
            return "HIGH"

        return "LOW"

    @staticmethod
    def _fallback_severity(final_score):
        """
        Used when rolling baseline is unstable.
        """

        if final_score < 0.3:
            return "LOW"
        elif final_score < 0.7:
            return "MEDIUM"
        else:
            return "HIGH"
