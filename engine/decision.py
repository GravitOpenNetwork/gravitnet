# Gravit Engine — Decision Module Stub

def decide(policy, risk):
    """
    Stub implementation of decision logic combining policy and risk.
    """
    if policy.get("status") == "APPROVED" and risk < 0.5:
        return "APPROVED"
    return "REJECTED"
