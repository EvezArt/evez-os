#!/usr/bin/env python3
"""
Browser Automation Workflows
Pre-built workflows for common tasks.
"""
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Callable

WORKFLOWS_PATH = Path(__file__).parent / "workflows.json"

@dataclass
class WorkflowStep:
    action: str      # click, type, navigate, wait, screenshot
    target: str      # selector, url, text
    value: str = ""  # for type actions

@dataclass  
class Workflow:
    name: str
    description: str
    steps: List[WorkflowStep]
    category: str = "general"

# Pre-built workflows
WORKFLOWS = [
    Workflow(
        name="search_amazon",
        description="Search Amazon for a product",
        category="shopping",
        steps=[
            WorkflowStep("navigate", "https://www.amazon.com"),
            WorkflowStep("wait", "input#twotabsearchbox"),
            WorkflowStep("type", "input#twotabsearchbox", "YOUR_SEARCH"),
            WorkflowStep("click", "input.nav-search-submit"),
            WorkflowStep("wait", ".s-result-list"),
            WorkflowStep("screenshot", "results"),
        ]
    ),
    Workflow(
        name="fill_contact_form",
        description="Fill out a contact form",
        category="forms",
        steps=[
            WorkflowStep("navigate", "TARGET_URL"),
            WorkflowStep("wait", "form"),
            WorkflowStep("type", "name", "Your Name"),
            WorkflowStep("type", "email", "your@email.com"),
            WorkflowStep("type", "message", "Your message"),
            WorkflowStep("click", "button[type=submit]"),
            WorkflowStep("wait", "success"),
        ]
    ),
    Workflow(
        name="scrape_prices",
        description="Scrape product prices from page",
        category="scraping",
        steps=[
            WorkflowStep("navigate", "TARGET_URL"),
            WorkflowStep("wait", ".product-price"),
            WorkflowStep("screenshot", "prices"),
            # Analysis happens after screenshot
        ]
    ),
    Workflow(
        name="sign_up_newsletter",
        description="Sign up for newsletter",
        category="marketing",
        steps=[
            WorkflowStep("navigate", "TARGET_URL"),
            WorkflowStep("wait", "input[type=email]"),
            WorkflowStep("type", "input[type=email]", "YOUR_EMAIL"),
            WorkflowStep("click", "button[type=submit]"),
            WorkflowStep("wait", "success-message"),
        ]
    ),
    Workflow(
        name="social_post",
        description="Post to Twitter/X",
        category="social",
        steps=[
            WorkflowStep("navigate", "https://twitter.com/compose/tweet"),
            WorkflowStep("wait", "div[contenteditable]"),
            WorkflowStep("type", "div[contenteditable]", "YOUR_POST_TEXT"),
            WorkflowStep("click", "button[data-testid=tweet]"),
        ]
    ),
]

def load_workflows() -> List[Workflow]:
    """Load saved workflows"""
    if WORKFLOWS_PATH.exists():
        data = json.loads(WORKFLOWS_PATH.read_text())
        # Convert back to Workflow objects
        return [Workflow(w["name"], w["description"], 
                   [WorkflowStep(s["action"], s["target"], s.get("value", "")) 
                    for s in w["steps"]],
                   w.get("category", "general")) 
                for w in data]
    return WORKFLOWS

def save_workflow(workflow: Workflow):
    """Save a custom workflow"""
    data = [{"name": w.name, "description": w.description,
            "steps": [{"action": s.action, "target": s.target, "value": s.value} 
                     for s in w.steps],
            "category": w.category}
           for w in load_workflows() + [workflow]]
    WORKFLOWS_PATH.write_text(json.dumps(data, indent=2))

def list_workflows() -> List[dict]:
    """List available workflows"""
    return [{"name": w.name, "description": w.description, 
             "category": w.category, "steps": len(w.steps)}
            for w in WORKFLOWS]

def get_workflow(name: str) -> Workflow:
    """Get workflow by name"""
    for w in WORKFLOWS:
        if w.name == name:
            return w
    raise ValueError(f"Workflow '{name}' not found")

def demo_workflows():
    """Show available workflows"""
    print("=" * 40)
    print("BROWSER AUTOMATION WORKFLOWS")
    print("=" * 40)
    
    for wf in list_workflows():
        print(f"\n📦 {wf['name']}")
        print(f"   {wf['description']}")
        print(f"   Category: {wf['category']} | Steps: {wf['steps']}")
    
    return WORKFLOWS

if __name__ == "__main__":
    demo_workflows()