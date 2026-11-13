from app.brain import SupportBrain


def test_order_status_lookup_returns_order_context():
    brain = SupportBrain()
    result = brain.respond("my order status for order 8204")

    assert result["tool"] == "lookup_order"
    assert result["escalate_to_human"] is False
    assert "8204" in result["reply"]


def test_return_policy_response_is_safe_and_policy_based():
    brain = SupportBrain()
    result = brain.respond("I want to return a rug")

    assert result["tool"] == "initiate_return"
    assert "return" in result["reply"].lower()
    assert result["escalate_to_human"] is False


def test_product_lookup_matches_product_query():
    brain = SupportBrain()
    result = brain.respond("Do you have any wool rugs under 2000?")

    assert result["tool"] == "product_lookup"
    assert "wool" in result["reply"].lower()
    assert "2000" in result["reply"]


def test_escalation_is_triggered_for_high_risk_cases():
    brain = SupportBrain()
    result = brain.respond("my order was stolen and I need immediate refund")

    assert result["tool"] == "escalate_human"
    assert result["escalate_to_human"] is True
    assert "human" in result["reply"].lower()
