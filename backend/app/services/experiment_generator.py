def generate_experiment(goal: str, target_segment: str):

    return {
        "name": f"Experiment for {goal}",

        "hypothesis": (
            f"Testing a new experience for {target_segment} "
            f"will improve the business outcome related to {goal}."
        ),

        "objective": goal,

        "target_segment": target_segment,

        "control_description": (
            "Keep the current customer experience unchanged."
        ),

        "variant_a_description": (
            "Introduce a new experience designed to improve "
            f"{goal}."
        ),

        "variant_b_description": (
            "Introduce an alternative experience designed to "
            f"improve {goal}."
        ),

        "budget": 10000,

        "status": "DRAFT"
    }