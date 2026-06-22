---
name: git-version-control
description: |
  Git-based version control for OpenClaw system configuration changes.
  
  Provides two core capabilities:
  (1) SAVE - Create a checkpoint before sensitive operations (git add & commit)
  (2) ROLLBACK - Revert to a previous state if issues occur (git reset)
  
  Use when:
  - Before making sensitive configuration changes
  - Before installing/removing skills
  - Before modifying core files (SOUL.md, AGENTS.md, MEMORY.md, etc.)
  - User requests to undo recent changes
  - System state needs recovery after errors
---

# Git Version Control | OpenClaw Configuration Protection

> Protect your OpenClaw environment with git-based checkpoints and rollback capability.

## Overview

OpenClaw configuration directory (`~/.openclaw/`) is a git repository. This skill provides safe version control for system configuration changes.

**Protected files include**:
- `workspace/SOUL.md`, `AGENTS.md`, `USER.md`, `IDENTITY.md`
- `workspace/skills/` - installed skills
- `workspace/memory/` - memory files
- `openclaw.json` - main configuration
- `cron/jobs.json` - cron jobs

**Excluded from version control**:
- Session logs (`*.jsonl`, `*.jsonl.lock`)
- SQLite databases (`*.sqlite`)
- Temporary files
- Credentials (sensitive)

---

## Core Operations

### 1. SAVE - Create Checkpoint

Create a git commit before making sensitive changes. This provides a recovery point.

**When to use**:
- Before modifying core configuration files
- Before installing/uninstalling skills
- Before making bulk memory changes
- User explicitly requests a save point

**Command Flow**:
```bash
cd ~/.openclaw

# Check current status
git status

# Add all tracked files (respecting .gitignore)
git add -A

# Create commit with descriptive message
git commit -m "checkpoint: {description of pending change}"
```

**Implementation**:
```
When user says: "save before..." or "create checkpoint"

1. Generate descriptive commit message based on context
2. Run: git add -A
3. Run: git commit -m "checkpoint: {description}"
4. Report commit hash and file count to user
```

**Example**:
```
User: "Save before I install a new skill"
Action:
  git add -A
  git commit -m "checkpoint: before installing new skill"
Output: "✓ Checkpoint created: abc1234 (5 files changed)"
```

---

### 2. ROLLBACK - Restore Previous State

Revert to a previous commit when issues occur.

**When to use**:
- User reports system issues after recent changes
- User explicitly requests rollback
- Configuration corruption detected
- After a failed skill installation

**Rollback Options**:

| Option | Command | Effect |
|--------|---------|--------|
| Soft reset | `git reset --soft HEAD~1` | Undo commit, keep changes staged |
| Mixed reset | `git reset --mixed HEAD~1` | Undo commit, keep changes unstaged |
| Hard reset | `git reset --hard HEAD~1` | Completely undo commit and changes |

**Recommended default**: `--hard` for full rollback

**Implementation**:
```
When user says: "rollback" or "undo last change" or "restore previous"

1. Show recent commits for user to choose
   git log --oneline -10
   
2. Confirm which commit to restore to
   "Rollback to commit X? This will discard: {list changes}"
   
3. Execute rollback
   git reset --hard {commit-hash}
   
4. Report result
   "✓ Rolled back to commit abc1234"
```

**Example**:
```
User: "Rollback to before the skill installation"
Action:
  git log --oneline -5
  # Show: abc1234 checkpoint: before skill install
  #       def5678 previous config
  git reset --hard abc1234
Output: "✓ Rolled back to 'before skill install' (abc1234)"
```

---

## Helper Operations

### View History

```bash
# Show recent commits
git log --oneline -10

# Show what changed in last commit
git show --stat HEAD

# Compare current state to last commit
git diff HEAD
```

### Check Status

```bash
# See uncommitted changes
git status

# See diff summary
git diff --stat
```

### List Protected Files

Files tracked for version control (in git):
```bash
git ls-files
```

---

## .gitignore Configuration

Ensure `~/.openclaw/.gitignore` excludes volatile/sensitive files:

```gitignore
# Session logs (volatile)
*.jsonl
*.jsonl.lock
*.jsonl.reset.*

# Databases (volatile)
*.sqlite
*.sqlite-journal

# Credentials (sensitive)
credentials/
*.pem
*.key

# Temporary files
*.tmp
*.temp
.DS_Store

# Logs
logs/

# Delivery queue
delivery-queue/
```

---

## Decision Tree

```
User requests sensitive operation
        ↓
    Is SAVE needed?
    ┌─────┴─────┐
   Yes          No
    ↓            ↓
 SAVE first   Execute directly
    ↓
Execute operation
    ↓
  Success?
  ┌─────┴─────┐
 Yes          No
  ↓            ↓
 Done      ROLLBACK?
           ┌─────┴─────┐
          Yes          No
           ↓            ↓
       Rollback     Debug manually
```

---

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| self-improvement | Record rollback events as learnings |
| skill-creator | Auto-SAVE before creating new skills |
| healthcheck | Check git status during health checks |

---

## Safety Guidelines

### ✅ Best Practices

1. **Always SAVE before risky operations**
   - Installing skills from external sources
   - Modifying AGENTS.md, SOUL.md
   - Bulk memory updates

2. **Use descriptive commit messages**
   ```
   checkpoint: before installing news skill
   checkpoint: before modifying SOUL.md persona
   checkpoint: before cron job changes
   ```

3. **Verify before ROLLBACK**
   - Show what will be lost
   - Confirm with user for hard reset

### ❌ Avoid

1. **Don't rollback without confirmation**
   - Hard reset destroys uncommitted changes
   - Always warn user about data loss

2. **Don't commit sensitive data**
   - Check .gitignore excludes credentials
   - Never add `credentials/` to git

3. **Don't use for session data**
   - Session logs are excluded intentionally
   - Focus on configuration, not runtime data

---

## Quick Reference

| Action | Command | Alias |
|--------|---------|-------|
| SAVE checkpoint | `git add -A && git commit -m "checkpoint: {desc}"` | `save` |
| ROLLBACK | `git reset --hard HEAD~1` | `rollback` |
| View history | `git log --oneline -10` | `history` |
| Check status | `git status` | `status` |
| Compare diff | `git diff HEAD` | `diff` |

---

## Example Session

```
User: Install a new skill from ClawHub

Agent (internal):
  1. SAVE checkpoint first
     $ git add -A
     $ git commit -m "checkpoint: before installing {skill-name}"
     ✓ Checkpoint: abc1234

  2. Install skill
     $ clawhub install {skill-name}
     
  3. Verify success
     ✓ Skill installed successfully
     
User: That skill broke something, rollback!

Agent:
  1. Show options
     $ git log --oneline -3
     abc1234 checkpoint: before installing {skill-name}
     def5678 previous state
     
  2. Confirm rollback
     "Rollback to abc1234? This will remove the newly installed skill."
     
  3. Execute
     $ git reset --hard abc1234
     ✓ Rolled back successfully
```

---

_Last updated: 2026-03-05_
