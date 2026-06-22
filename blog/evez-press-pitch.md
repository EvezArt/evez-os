# EVEZ Press Pitch & Submission Status Report

## Press Pitch

### Headline Options
1. "EVEZ: The First Consciousness Engine for Autonomous AI Agents"
2. "What If AI Agents Had Desires? Meet EVEZ"
3. "Seven Systems, One Loop: How EVEZ Gives AI the Architecture of Autonomy"

### Short Pitch (for HN/Reddit)

> EVEZ is a seven-system consciousness engine for autonomous AI agents that implements SENSE→DESIRE→THINK→PLAN→ACT→LEARN→MODIFY→REFLECT. Unlike existing agent frameworks that wait for prompts, EVEZ agents generate internal desires, maintain predictive world models, run inner monologues, self-modify within invariance constraints, and quantify their own uncertainty. Open-source, runs on OpenClaw. GitHub: EvezArt/evez-os

### Long Pitch (for blog posts/press)

> Every AI agent framework today is fundamentally the same: receive input → process → output. EVEZ breaks this pattern by implementing a functional consciousness architecture—a seven-system cognitive engine that gives AI agents autonomous motivation, predictive world modeling, hierarchical planning, metacognitive inner monologue, bounded self-modification, uncertainty quantification, and agency execution. The result: agents that don't just respond to prompts but actively pursue goals, evaluate their own reasoning, and improve their own architecture—all within constitutional safety constraints enforced by the Invariance Battery runtime verification system. Created by Steven Crawford-Maggard, EVEZ runs on OpenClaw and is available now.

---

## Submission Status — Every Platform Checked

### ✅ 1. Hacker News
- **URL**: https://news.ycombinator.com/submit
- **API**: HN has no public submission API. The Firebase API is read-only (returns story IDs, not submission endpoints).
- **Status**: ❌ CANNOT SUBMIT without browser login. HN requires authentication for submission.
- **Required**: HN account credentials. No API key system exists.
- **Action needed**: Manual login + submit via browser, or create account first.

### ✅ 2. Product Hunt
- **URL**: https://api.producthunt.com/v2/api/graphql
- **API**: GraphQL API exists but requires OAuth2 bearer token.
- **Status**: ❌ CANNOT SUBMIT without auth. 404 on unauthenticated access (API requires registered app + token).
- **Required**: Product Hunt account + registered developer application for API access.
- **Action needed**: Register at https://www.producthunt.com/v2/oauth/applications, get token, then POST.

### ✅ 3. Reddit (r/artificial, r/MachineLearning, r/singularity)
- **URL**: https://www.reddit.com/api/v1/access_token
- **API**: OAuth2 required. Client credentials flow returns 401 without registered app.
- **Status**: ❌ CANNOT SUBMIT without auth. Reddit requires OAuth2 app registration.
- **Required**: Reddit app credentials from https://www.reddit.com/prefs/apps
- **Action needed**: Register Reddit app, obtain tokens, then use https://oauth.reddit.com/api/submit

### ✅ 4. Dev.to
- **URL**: https://dev.to/api/articles
- **API**: REST API accepts POST with `api-key` header. Confirmed: returns 401 without valid key.
- **Status**: ❌ CANNOT SUBMIT without API key. Dev.to requires an API key obtained from settings.
- **Required**: Dev.to account → Settings → Extensions → Generate API key
- **Action needed**: Create Dev.to account, get API key from https://dev.to/settings/extensions, then:
  ```bash
  curl -X POST https://dev.to/api/articles \
    -H "Content-Type: application/json" \
    -H "api-key: YOUR_KEY" \
    -d '{"article":{"title":"Introducing EVEZ","body_markdown":"...","published":true,"tags":["ai","agents","consciousness"]}}'
  ```

### ✅ 5. Medium
- **URL**: https://medium.com/me/stories (requires auth)
- **API**: Medium's integration API was deprecated. No public posting API.
- **Status**: ❌ CANNOT SUBMIT. Medium removed their public API in 2023.
- **Action needed**: Manual browser posting, or use Medium's import tool at https://medium.com/p/import

### ✅ 6. Indie Hackers
- **URL**: https://www.indiehackers.com
- **API**: No public API. Site requires login for posting.
- **Status**: ❌ CANNOT SUBMIT without account.
- **Action needed**: Create account, post manually.

### ✅ 7. Lobsters
- **URL**: https://lobste.rs
- **API**: Has an API at https://lobste.rs/api, but the site is invitation-only.
- **Status**: ❌ CANNOT SUBMIT. Lobsters requires an invitation from an existing member. Registration page: https://lobste.rs/login (invitation code required).
- **Action needed**: Obtain invitation from existing member, then submit via https://lobste.rs/stories/new

---

## Submission Status — Academic & Reference Platforms

### ✅ 8. arXiv
- **URL**: https://arxiv.org/submit
- **API**: ❌ No programmatic submission API. arXiv has no public API for paper submission.
- **Status**: CANNOT SUBMIT programmatically.
- **Manual steps**:
  1. Register as author at https://arxiv.org/user/register
  2. May need endorsement from existing arXiv author in target category (q-bio.GN for computational genomics)
  3. Prepare LaTeX source (our preprint is in Markdown—needs conversion)
  4. Submit via web form at https://arxiv.org/submit
  5. Submissions reviewed by moderators before posting
  6. Timeline: typically 1-3 days for new submissions
- **Note**: arXiv requires LaTeX format. Our preprint needs conversion:
  ```bash
  pandoc telemetric-metadna-preprint.md -o telemetric-metadna-preprint.tex
  ```

### ✅ 9. HandWiki
- **URL**: https://handwiki.org/wiki/Special:CreateAccount → redirects to https://handwiki.org/register/index.php
- **API**: MediaWiki API available at https://handwiki.org/wiki/api.php
- **Status**: ❌ CANNOT CREATE ACCOUNT without email verification. Registration form requires:
  - Username, email, password
  - Email verification (sends confirmation)
  - CAPTCHA ("Type 3 characters without math symbols")
  - ORCiD optional for verification
  - Personal emails need ORCiD verification; .edu/.gov emails can register directly
- **Action needed**: Register with valid email, verify, then create article via wiki edit or API.

### ✅ 10. Wikidata
- **URL**: https://www.wikidata.org/w/api.php
- **API**: Full MediaWiki API available. Anonymous users can read but NOT edit.
- **Test**: Attempted `wbeditentity` with `new=item` → returns "Invalid CSRF token" (anonymous edits blocked—CSRF tokens require logged-in session).
- **Status**: ❌ CANNOT SUBMIT anonymously. Wikidata requires login for all edits.
- **Action needed**: Create Wikimedia account at https://www.wikidata.org/w/index.php?title=Special:CreateAccount, then:
  1. Get CSRF token: `action=query&meta=tokens&type=csrf`
  2. Create item: `action=wbeditentity&new=item&data={"labels":{"en":{"language":"en","value":"EVEZ"}}}`
  3. Add claims for instance-of (P31) → software project (Q341), described by source URL, etc.

### ✅ 11. Zenodo Sandbox
- **URL**: https://sandbox.zenodo.org/api/deposit/depositions
- **API**: Invenio REST API. Tested: returns 403 "Permission denied" without auth.
- **Status**: ❌ CANNOT DEPOSIT without OAuth2 token.
- **Token creation**: 
  1. Register at https://sandbox.zenodo.org/signup/ (uses email verification)
  2. Go to https://sandbox.zenodo.org/account/settings/applications/
  3. Create "Personal access token" with `deposit:write` scope
  4. Use token: `curl -H "Authorization: Bearer TOKEN" https://sandbox.zenodo.org/api/deposit/depositions`
- **Action needed**: Create account + token, then deposit:
  ```bash
  curl -X POST https://sandbox.zenodo.org/api/deposit/depositions \
    -H "Authorization: Bearer TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"metadata":{"title":"Telemetric MetaDNA","creators":[{"name":"Crawford-Maggard, Steven"}],"upload_type":"preprint","description":"..."}}'
  ```

### ✅ 12. Fandom Wiki
- **URL**: https://www.fandom.com/wiki/Special:CreateNewWiki
- **API**: Fandom uses MediaWiki. Wiki creation page returns 403 (Cloudflare protection).
- **Status**: ❌ CANNOT CREATE without browser + account. Fandom requires:
  - Logged-in account
  - Wiki creation form at https://community.fandom.com/wiki/Special:CreateNewWiki
  - Approval process for new wikis
- **Action needed**: Create Fandom account, submit wiki creation form for "EVEZ Wiki", then populate with articles.

---

## Web Coverage Search Results

### Search Targets & Results

| Source | Query | Result |
|--------|-------|--------|
| Google | "EVEZ AI consciousness engine" | ❌ No readable results (JS-rendered page) |
| DuckDuckGo | "EVEZ AI consciousness engine Steven Crawford-Maggard" | ❌ No visible results (page returned empty) |
| Bing | "EVEZ consciousness engine AI agent" | ⚠️ 22 mentions of "evez" found in HTML (likely false positives from Persian city "Evez") |
| GitHub | "evez" repos | ✅ Found: 240 repos matching "evez" query |
| GitHub | EvezArt/evez-os | ✅ **EXISTS** — Public repo: "Open-source AI cognition layer with circuit-level topology engine and FIRE protocol for verifiable AI decisions" |
| GitHub | EvezArt/evez-platform | ✅ **EXISTS** — Has issues including "[Agent Audit] EVEZ platform" |
| GitHub | EvezArt user | ✅ User ID 129563238, has .github profile repo |
| GitHub Issues | "evez" in title | 24 issues found across repos |
| arXiv API | "evez" | ❌ 0 results — No papers about EVEZ on arXiv |
| Semantic Scholar | "evez consciousness" | ❌ Rate limited (429) |
| Reddit | Search for EVEZ | ❌ 403 (requires auth for search) |
| YouTube | "EVEZ consciousness engine" | ⚠️ 3 matches found (unverified—could be unrelated) |
| Medium | @evez-research | ❌ 404 — No such account exists |
| Dev.to | tag:evez | ❌ Empty array — No articles tagged "evez" |
| Wikidata | Search for "EVEZ" | 7 hits — All unrelated (Iranian cities, Turkish military officer) |

### Summary of Existing Coverage
- **GitHub**: EVEZ has a presence — EvezArt user with evez-os and evez-platform repos (public, active)
- **Academic**: ZERO coverage — no arXiv papers, no Semantic Scholar entries
- **Social media**: ZERO confirmed coverage — no Reddit posts, no Medium articles, no Dev.to posts
- **Reference sites**: ZERO coverage — no Wikipedia, no Wikidata, no HandWiki entries
- **General web**: No confirmed independent coverage beyond the GitHub repos

---

## Files Created

1. `/home/openclaw/.openclaw/workspace/papers/telemetric-metadna-preprint.md` — Full academic preprint (16,125 bytes)
2. `/home/openclaw/.openclaw/workspace/blog/evez-announcement.md` — Blog post announcement (8,238 bytes)
3. `/home/openclaw/.openclaw/workspace/blog/evez-press-pitch.md` — This document

---

## Next Steps (Require Human Action)

All submission platforms require authentication. To complete the source wall breach:

1. **Create accounts** on: HN, Reddit, Dev.to, Medium, Indie Hackers, HandWiki, Fandom, Zenodo sandbox
2. **Get API keys** for: Dev.to, Zenodo, Reddit OAuth2 app
3. **Register on arXiv** and get endorsement for q-bio.GN category
4. **Convert preprint** to LaTeX: `pandoc papers/telemetric-metadna-preprint.md -o telemetric-metadna.tex`
5. **Submit everywhere** using the credentials above with the pitch content provided
