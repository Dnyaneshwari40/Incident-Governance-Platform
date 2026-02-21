class ActionEngine:
    """
    Maps severity level to operational action.
    """

    ACTION_MAP = {
        "LOW": "Log incident only",
        "MEDIUM": "Log and monitor closely",
        "HIGH": "Notify operations team",
        "CRITICAL": "Immediate alert and escalate",
    }

    @staticmethod
    def recommend(severity):
        """
        Returns recommended action for given severity.
        """
        return ActionEngine.ACTION_MAP.get(
            severity,
            "Log incident only"
        )
