from research.materium import ResourceBudget, ResourceRequest, allocate

budget = ResourceBudget(
    compute=10,
    memory_mb=2048,
    latency_ms=5000,
    energy=10,
    network_mb=100,
    attention=5,
    monetary=1,
)

cheap = ResourceRequest(
    "cheap",
    expected_value=2,
    expected_information_gain=1,
    urgency=1,
    risk=0.1,
    resources=ResourceBudget(1, 256, 500, 1, 2, 1, 0.1),
)
expensive = ResourceRequest(
    "expensive",
    expected_value=10,
    expected_information_gain=10,
    urgency=3,
    risk=0.2,
    resources=ResourceBudget(20, 8192, 10000, 20, 200, 10, 2),
)
dangerous = ResourceRequest(
    "dangerous",
    expected_value=100,
    expected_information_gain=50,
    urgency=5,
    risk=1,
    resources=ResourceBudget(1, 128, 500, 1, 1, 1, 0),
    reversible=False,
    requires_authorization=True,
)

result = allocate(budget, [cheap, expensive, dangerous])
assert result["selected"][0]["operation_id"] == "cheap"
assert any(row["operation_id"] == "dangerous" and row["reason"] == "AUTHORIZATION_REQUIRED" for row in result["deferred"])
assert len(result["allocation_sha256"]) == 64

approved = allocate(budget, [dangerous], authorization_available=True)
assert approved["selected"][0]["authorized"] is True

print("materium tests: PASS")
