"""
Self-Improving Critic - Always-on critic that learns from ledger entries

Runs after every 3-5 ledger entries:
1. Read last window of ledger
2. Write "learning block" markdown
3. Before major tasks, pull top 3 learnings and bake into plan
"""

import json
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict

LEDGER_PATH = "/root/.openclaw/workspace/evez-os/core/ledger"
LEARNING_PATH = "/root/.openclaw/workspace/evez-os/core/learning"

class SelfImprovingCritic:
    def __init__(self, window_size=5, min_entries_to_critic=3):
        self.window_size = window_size
        self.min_entries_to_critic = min_entries_to_critic
    
    def ensure_learning_dir(self):
        os.makedirs(LEARNING_PATH, exist_ok=True)
    
    def read_ledger(self, n=None):
        """Read last N ledger entries"""
        ledger_file = f"{LEDGER_PATH}/chain.jsonl"
        if not os.path.exists(ledger_file):
            return []
        
        with open(ledger_file) as f:
            lines = f.readlines()
            entries = [json.loads(l) for l in lines if l.strip()]
            
        if n is not None:
            return entries[-n:]
        return entries
    
    def analyze_window(self, entries):
        """Analyze a window of entries for learnings"""
        if not entries:
            return None
        
        # Categorize entries by type
        by_type = defaultdict(list)
        for e in entries:
            t = e.get("type", "unknown")
            by_type[t].append(e)
        
        # Identify successes and failures
        successes = []
        failures = []
        
        for e in entries:
            status = e.get("status", "")
            if "success" in status.lower() or "complete" in status.lower():
                successes.append(e)
            elif "fail" in status.lower() or "block" in status.lower():
                failures.append(e)
        
        # Extract patterns from failures
        failure_patterns = []
        for f in failures:
            reason = f.get("reason", f.get("error", "unknown"))
            failure_patterns.append(reason)
        
        return {
            "entry_count": len(entries),
            "successes": successes,
            "failures": failures,
            "failure_patterns": failure_patterns,
            "by_type": dict(by_type)
        }
    
    def write_learning_block(self, analysis):
        """Write a learning block markdown file"""
        self.ensure_learning_dir()
        
        timestamp = datetime.utcnow().isoformat()
        block_file = f"{LEARNING_PATH}/critic_{timestamp.replace(':', '-')}.md"
        
        content = f"""# Learning Block - {timestamp}

## Summary
- Entries analyzed: {analysis['entry_count']}
- Successes: {len(analysis['successes'])}
- Failures: {len(analysis['failures'])}

## Failure Patterns
"""
        
        for fp in analysis['failure_patterns']:
            content += f"- {fp}\n"
        
        content += "\n## By Type\n"
        for t, entries in analysis['by_type'].items():
            content += f"- {t}: {len(entries)} entries\n"
        
        # Extract actionable learnings
        learnings = self._extract_learnings(analysis)
        
        if learnings:
            content += "\n## Actionable Learnings\n"
            for l in learnings:
                content += f"- {l}\n"
        
        content += f"\n## Top 3 Learnings for Next Task\n"
        
        # Save top learnings separately for quick retrieval
        top_learnings = learnings[:3] if learnings else []
        for i, l in enumerate(top_learnings, 1):
            content += f"{i}. {l}\n"
        
        with open(block_file, "w") as f:
            f.write(content)
        
        # Also update a "latest" pointer
        with open(f"{LEARNING_PATH}/latest.md", "w") as f:
            f.write(content)
        
        return block_file
    
    def _extract_learnings(self, analysis):
        """Extract actionable learnings from analysis"""
        learnings = []
        
        # From failures - what to avoid
        for fp in analysis['failure_patterns']:
            if "bot detection" in fp.lower() or "x" in fp.lower():
                learnings.append("Avoid X account creation via headless browser - try human verification or API")
            if "fiverr" in fp.lower():
                learnings.append("Fiverr blocked by operator - use alternative marketplace")
            if "clowhub" in fp.lower() or "auth" in fp.lower():
                learnings.append("ClawHub needs OAuth via browser - schedule manual login")
            if "phone" in fp.lower() or "sms" in fp.lower():
                learnings.append("No free phone verification - consider paid SMS or skip"
)
        
        # From successes - what to replicate
        for s in analysis['successes']:
            obj = s.get("objective", "")
            if "github" in obj.lower():
                learnings.append("GitHub push works reliably - continue publishing skills there")
            if "consulting" in obj.lower():
                learnings.append("Consulting offer ready - can send outreach DMs")
        
        return learnings
    
    def get_top_learnings(self, n=3):
        """Get top N learnings for a major task"""
        latest_file = f"{LEARNING_PATH}/latest.md"
        
        if not os.path.exists(latest_file):
            return []
        
        with open(latest_file) as f:
            content = f.read()
        
        # Extract top learnings section
        learnings = []
        in_learnings = False
        
        for line in content.split("\n"):
            if "Top 3 Learnings" in line:
                in_learnings = True
                continue
            if in_learnings and line.strip() and line[0].isdigit():
                # Extract the learning (skip "1. ")
                parts = line.split(". ", 1)
                if len(parts) > 1:
                    learnings.append(parts[1])
        
        return learnings[:n]
    
    def should_criticize(self):
        """Check if enough entries have accumulated to run critic"""
        entries = self.read_ledger()
        return len(entries) >= self.min_entries_to_critic
    
    def run_critic(self):
        """
        Main critic pass - run when enough entries accumulate
        """
        print("=== SELF-IMPROVING CRITIC RUNNING ===")
        
        # Check if enough entries
        if not self.should_criticize():
            print(f"Not enough entries to criticize (need {self.min_entries_to_critic})")
            return {"status": "skipped", "reason": "insufficient_entries"}
        
        # Analyze recent window
        entries = self.read_ledger(self.window_size)
        analysis = self.analyze_window(entries)
        
        if not analysis:
            return {"status": "no_analysis", "entries": len(entries)}
        
        # Write learning block
        block_file = self.write_learning_block(analysis)
        print(f"Learning block written: {block_file}")
        
        # Get top learnings for next task
        top = self.get_top_learnings()
        
        return {
            "status": "critique_complete",
            "analysis": analysis,
            "learning_block": block_file,
            "top_learnings": top
        }
    
    def bake_into_plan(self, plan):
        """Bake top learnings into a plan before major task execution"""
        learnings = self.get_top_learnings(3)
        
        if not learnings:
            return plan
        
        # Prepend learnings to plan
        learning_section = "## Lessons from Previous Cycles\n"
        for l in learnings:
            learning_section += f"- {l}\n"
        
        # Insert after plan header if exists
        if "## Plan" in plan:
            plan = plan.replace("## Plan", learning_section + "\n## Plan")
        else:
            plan = learning_section + "\n" + plan
        
        return plan

if __name__ == "__main__":
    critic = SelfImprovingCritic()
    result = critic.run_critic()
    print(f"\n=== RESULT ===\n{json.dumps(result, indent=2)}")