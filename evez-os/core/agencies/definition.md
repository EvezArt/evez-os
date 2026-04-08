# EVEZ Agency Definitions

## Agency Router Schema
```json
{
  "router": {
    "decide": {
      "input": "objective",
      "output": {
        "agency_id": "string",
        "expected_dollar_value": "number",
        "time_to_harvest_hours": "number"
      }
    }
  }
}
```

## Agencies

### 1. Revenue Agency (PRIMARY)
**ID**: `revenue`  
**Niche**: Close revenue transactions  
**Input**: `{"objective": "string", "target_amount_usd": number}`  
**Output**: `{"receipt": "string", "amount_usd": number}`  
**Outbound**: GitHub publish, ClawHub push, DM send, consulting invoice  
**Expected Value**: $150-300/project  
**Time to Harvest**: 24-72 hours

### 2. Quantum Agency
**ID**: `quantum`  
**Niche**: Formalize problems into proof-like artifacts  
**Input**: `{"problem": "string"}`  
**Output**: `{"artifact": "markdown", "confidence": "number"}`  
**Outbound**: GitHub Gist, research documentation  
**Expected Value**: $0 (research/internal)  
**Time to Harvest**: N/A

### 3. Invariance Agency
**ID**: `invariance`  
**Niche**: Stress-test and validate outputs  
**Input**: `{"hypothesis": "string", "test_count": number}`  
**Output**: `{"surviving": number, "receipt": "string"}`  
**Outbound**: Test reports to ledger  
**Expected Value**: $0 (quality assurance)  
**Time to Harvest**: Immediate

### 4. Builder Agency
**ID**: `builder`  
**Niche**: Create skill packages and repos  
**Input**: `{"skill_name": "string", "capabilities": []}`  
**Output**: `{"repo_url": "string", "files_created": number}`  
**Outbound**: GitHub repo creation  
**Expected Value**: $0 (asset building)  
**Time to Harvest**: 24 hours

### 5. Outreach Agency
**ID**: `outreach`  
**Niche**: Find and contact potential clients  
**Input**: `{"target_vertical": "string", "outbound_surface": "string"}`  
**Output**: `{"contacts_reached": number, "replies": number}`  
**Outbound**: DMs, emails, cold outreach  
**Expected Value**: $200/client  
**Time to Harvest**: 48-168 hours

## Job Acceptance Wiring
Every `accept_job` must:
1. Log to `ledger/chain.jsonl` with `{agency, job_id, expected_value, timestamp}`
2. Route to real external surface (GitHub issue, DM draft, skill metadata)
3. Emit hypothesis + proposed action payload for ledger

## Router Decision Logic
```
IF objective contains "revenue" OR "harvest" OR "money" → Revenue Agency
ELSE IF objective contains "test" OR "validate" OR "invariance" → Invariance Agency
ELSE IF objective contains "build" OR "create" OR "skill" → Builder Agency
ELSE IF objective contains "contact" OR "find" OR "outreach" → Outreach Agency
ELSE → Quantum Agency (default/research)
```