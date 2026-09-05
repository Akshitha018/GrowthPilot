import random


def assign_customers(customers):
    """
    Randomly assign customers into three experiment groups.
    """

    assignments = []

    groups = [
        "CONTROL",
        "VARIANT_A",
        "VARIANT_B"
    ]

    shuffled_customers = customers.copy()

    random.shuffle(shuffled_customers)

    for index, customer in enumerate(shuffled_customers):

        group = groups[index % 3]

        assignments.append({
            "customer_id": customer.customer_id,
            "group": group
        })

    return assignments