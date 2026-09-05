from typing import Dict, Any


def make_growth_decision(
    analysis: Dict[str, Any]
) -> Dict[str, Any]:

    groups = analysis["groups"]
    winner = analysis["winner"]
    improvement = analysis["improvement_percent"]

    # Total number of customers
    total_customers = sum(
        len(group["customers"])
        for group in groups.values()
    )

    # Total conversions
    total_conversions = sum(
        group["conversions"]
        for group in groups.values()
    )

    # -----------------------------------------------------
    # NOT ENOUGH DATA
    # -----------------------------------------------------

    if total_customers < 30:

        return {
            "decision": "KEEP_TESTING",
            "winner": winner,
            "confidence": "LOW",
            "reason": (
                f"Only {total_customers} customers have been "
                "included in the experiment."
            ),
            "recommendation": (
                "Continue the experiment and collect more customer data "
                "before making a scaling decision."
            )
        }


    # -----------------------------------------------------
    # NO CONVERSIONS
    # -----------------------------------------------------

    if total_conversions == 0:

        return {
            "decision": "KEEP_TESTING",
            "winner": winner,
            "confidence": "LOW",
            "reason": "No conversions have been recorded yet.",
            "recommendation": (
                "Continue running the experiment until meaningful "
                "conversion data is collected."
            )
        }


    # -----------------------------------------------------
    # VARIANT SIGNIFICANTLY BETTER
    # -----------------------------------------------------

    if winner != "CONTROL" and improvement >= 20:

        return {
            "decision": "SCALE",
            "winner": winner,
            "confidence": "HIGH",
            "improvement_percent": improvement,
            "reason": (
                f"{winner} is currently performing "
                f"{improvement}% better than CONTROL."
            ),
            "recommendation": (
                f"Increase exposure to {winner} and consider "
                "rolling it out to a larger customer segment."
            )
        }


    # -----------------------------------------------------
    # VARIANT SLIGHTLY BETTER
    # -----------------------------------------------------

    if winner != "CONTROL" and improvement > 0:

        return {
            "decision": "KEEP_TESTING",
            "winner": winner,
            "confidence": "MEDIUM",
            "improvement_percent": improvement,
            "reason": (
                f"{winner} is currently performing better than CONTROL, "
                "but the improvement is relatively small."
            ),
            "recommendation": (
                "Continue the experiment and collect more data "
                "before scaling the variant."
            )
        }


    # -----------------------------------------------------
    # CONTROL WINS
    # -----------------------------------------------------

    if winner == "CONTROL":

        return {
            "decision": "KEEP_TESTING",
            "winner": "CONTROL",
            "confidence": "MEDIUM",
            "improvement_percent": improvement,
            "reason": (
                "CONTROL is currently performing better than the "
                "tested variants."
            ),
            "recommendation": (
                "Continue testing until enough data is available "
                "to determine whether the variants should be stopped."
            )
        }


    # -----------------------------------------------------
    # FALLBACK
    # -----------------------------------------------------

    return {
        "decision": "KEEP_TESTING",
        "winner": winner,
        "confidence": "LOW",
        "reason": "There is not enough evidence for a final decision.",
        "recommendation": (
            "Continue collecting experiment results."
        )
    }