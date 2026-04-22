#!/usr/bin/env python3
"""
Model Router - Route to best model for each task
"""
from typing import Dict

ROUTING = {
    "quick": "gpt-4o-mini",
    "reasoning": "claude-sonnet-4-20250514",
    "code": "anthropic-sonnet-4-20250514", 
    "creative": "gpt-4.1",
    "analysis": "gpt-4.1",
    "fast_summary": "gpt-4o-mini",
}

def route(task: str) -> str:
    task = task.lower()
    for key, model in ROUTING.items():
        if key in task:
            return model
    return "claude-sonnet-4-20250514"

def cost_estimate(model: str) -> float:
    costs = {"gpt-4o-mini": 0.001, "gpt-4.1": 0.01, "claude-sonnet-4-20250514": 0.015}
    return costs.get(model, 0.01)

if __name__ == "__main__":
    tasks = ["write email", "analyze code", "quick summary"]
    for t in tasks:
        print(f"Task: {t} -> Model: {route(t)}")
