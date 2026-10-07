from research.execution_kernel import plan
from research.materium import ResourceBudget, ResourceRequest
from research.signal_negotiation import ChannelCapability

budget = ResourceBudget(10, 2048, 5000, 10, 100, 5, 1)
requests = [
    ResourceRequest(
        "build",
        3,
        2,
        1,
        0.1,
        ResourceBudget(2, 256, 500, 1, 2, 1, 0.1),
    )
]
channels = [
    ChannelCapability(
        "visual", True, ("operator-info", "operator-alerts"),
        0.9, 0.9, 1.0, preferred_rank=1
    )
]

ready = plan("build the missing capability", resources=budget, requests=requests, channels=channels)
assert ready["status"] == "READY_FOR_VERIFICATION"
assert ready["authorization"]["consequential_execution_blocked"] is False
assert ready["channel_plan"]["status"] == "READY"
assert ready["precision"]["blocked"] is False
assert ready["optimization"]["status"] in {"EVIDENCE_GAP", "OPTIMIZED_CANDIDATE"}
assert 0.0 <= ready["optimization"]["score"] <= 1.0

blocked = plan("merge and deploy the implementation", resources=budget, requests=requests, channels=channels)
assert blocked["status"] == "AUTHORIZATION_REQUIRED"
assert blocked["authorization"]["consequential_execution_blocked"] is True

vague = plan("do everything fully", resources=budget, requests=requests, channels=channels)
assert vague["status"] == "REQUIRES_SPECIFICATION"
assert vague["precision"]["blocked"] is True
assert vague["precision"]["finding_count"] > 0

print("execution kernel tests: PASS")
