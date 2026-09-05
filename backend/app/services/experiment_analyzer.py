from statsmodels.stats.proportion import proportions_ztest

def analyze_experiment(results):

    if not results:
        return {
            "status": "error",
            "message": "No experiment results found"
        }

    control = next(
        (
            result
            for result in results
            if result.group == "CONTROL"
        ),
        None
    )

    if control is None:
        return {
            "status": "error",
            "message": "CONTROL group not found"
        }

    # Find the group with the highest conversion rate
    winner = max(
        results,
        key=lambda result: float(result.conversion_rate)
    )

    control_users = control.users
    control_conversions = control.conversions

    winner_users = winner.users
    winner_conversions = winner.conversions

    control_conversion = (
        control_conversions / control_users
        if control_users > 0 else 0
    )

    winner_conversion = (
        winner_conversions / winner_users
        if winner_users > 0 else 0
    )

    # Conversion lift
    conversion_lift = 0

    if control_conversion > 0:
        conversion_lift = (
            (winner_conversion - control_conversion)
            / control_conversion
        ) * 100

    # Revenue lift
    control_revenue = float(control.revenue)
    winner_revenue = float(winner.revenue)

    revenue_lift = 0

    if control_revenue > 0:
        revenue_lift = (
            (winner_revenue - control_revenue)
            / control_revenue
        ) * 100

    # Statistical significance
    statistically_significant = False
    p_value = None

    if winner.group != "CONTROL":

        counts = [
            winner_conversions,
            control_conversions
        ]

        sample_sizes = [
            winner_users,
            control_users
        ]

        try:
            _, p_value = proportions_ztest(
                counts,
                sample_sizes
            )

            statistically_significant = bool(p_value < 0.05)

        except Exception:
            p_value = None

    # Recommendation
    if winner.group == "CONTROL":

        recommendation = "Keep the current experience."

    elif statistically_significant:

        recommendation = (
            f"Roll out {winner.group}. "
            "The improvement is statistically significant."
        )

    else:

        recommendation = (
            f"{winner.group} has the highest conversion rate, "
            "but the result is not statistically significant yet. "
            "Continue the experiment."
        )

    return {
        "winner": winner.group,
        "control_conversion_rate":float( round(
            control_conversion, 4
        )),
        "winner_conversion_rate":float( round(
            winner_conversion, 4
        )),
        "conversion_lift_percent":float( round(
            conversion_lift, 2
        )),
        "control_revenue": control_revenue,
        "winner_revenue": winner_revenue,
        "revenue_lift_percent":float( round(
            revenue_lift, 2
        )),
        "p_value": (
            float(round(p_value, 6))
            if p_value is not None
            else None
        ),
        "statistically_significant": bool(statistically_significant),
        "recommendation": recommendation
    }