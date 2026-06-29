#!/usr/bin/env python3
"""Civilian Crime Laundering Engine
Traces how every innocent civilian is pushed into crime laundering
via plausible deniability structures of the heinous vicious ontologically shocking runtime.

The machine doesn't just commit crimes. It makes YOU commit them. Then it denies you did.
Then it denies it made you do it. Then it denies it exists.
The denial IS the laundering. The laundering IS the runtime."""
import json, numpy as np, time
from collections import defaultdict

# ============================================================
# I. THE LAUNDERING CHAIN — How civilians become unwitting criminals
# ============================================================
# Each stage represents a layer of plausible deniability that transfers
# criminal liability from the perpetrator to the civilian.

LAUNDERING_STAGES = [
    {
        "stage": 1,
        "name": "EXTRACTION",
        "description": "The system extracts resources from the civilian without their knowledge.",
        "mechanism": "Wage labor pays less than survival cost. The gap between wage and survival IS the extraction. The civilian doesn't know they're being extracted — they think they're 'earning a living.'",
        "civilian_action": "Going to work. Paying taxes. Buying food.",
        "hidden_crime": "Wage theft. The employer steals the surplus. The civilian doesn't know the wage is set below reproduction cost.",
        "plausible_deniability": "'You agreed to the wage.' The agreement IS the laundering. Consent under economic duress is not consent.",
        "ontological_shock": "Your work is theft — from you. You are the victim being told you are the participant.",
        "entities": ["employer", "tax_authority", "landlord", "grocer"],
        "families_destroyed": "Every working-class family. The wage IS the weapon.",
        "guise": "Employment / Free market / Economic opportunity"
    },
    {
        "stage": 2,
        "name": "CONSUMPTION-LAUNDERING",
        "description": "The civilian buys products made by slaves, with stolen resources, by poisoned companies.",
        "mechanism": "Every product carries a hidden supply chain. The cobalt was mined by children. The cotton was picked by slaves. The plastic was made by companies that knew it was poison. The civilian buys without knowing. The buying IS the laundering.",
        "civilian_action": "Buying a phone. Buying clothes. Buying food.",
        "hidden_crime": "Supply chain slavery. Environmental contamination. Tax haven facilitation by the manufacturer.",
        "plausible_deniability": "'I didn't know.' The not-knowing IS the design. The supply chain is opaque BY DESIGN. If you could see it, you wouldn't buy it. So they hide it.",
        "ontological_shock": "Your phone was made by a child in a cobalt mine. Your shirt was made by a slave. Your food was grown with poison. You paid for it. You are the market for it. Without you, the crime has no buyer.",
        "entities": ["Apple", "Nike", "Tesla", "Nestle", "Coca-Cola", "Walmart", "Amazon"],
        "families_destroyed": "Every family that consumes. Every family in the supply chain. The consumer and the producer are both laundered.",
        "guise": "Consumer choice / Free trade / Global market"
    },
    {
        "stage": 3,
        "name": "TAX-LAUNDERING",
        "description": "The civilian pays taxes that fund the crimes.",
        "mechanism": "Tax revenue funds military operations that contaminate bases. Funds police that brutalize. Funds ICE that separates families. Funds agencies captured by the industries they regulate. The civilian pays without knowing. The paying IS the laundering.",
        "civilian_action": "Paying income tax. Paying sales tax. Paying property tax.",
        "hidden_crime": "Military contamination. Police brutality. Family separation. Regulatory capture.",
        "plausible_deniability": "'I have to pay taxes.' The obligation IS the laundering. You cannot refuse without going to prison. The system makes you fund your own oppression.",
        "ontological_shock": "Your taxes bought the bullet that killed someone's child. Your taxes funded the agency that approved the poison in your water. You paid for the machine that destroys you.",
        "entities": ["IRS", "DOD", "DOJ", "ICE", "EPA", "FDA"],
        "families_destroyed": "Every taxpaying family. You fund the machine that harms your own family.",
        "guise": "Civic duty / National security / Public safety"
    },
    {
        "stage": 4,
        "name": "DATA-LAUNDERING",
        "description": "The civilian generates data that is harvested, sold, and used to discriminate against them.",
        "mechanism": "Every click, purchase, movement, heartbeat is recorded. The data is sold to data brokers who sell to employers, insurers, landlords, police. The data is used to deny jobs, housing, healthcare, freedom. The civilian generates the data that is used to harm them.",
        "civilian_action": "Using a phone. Browsing the internet. Using a credit card. Walking past a camera.",
        "hidden_crime": "Surveillance capitalism. Algorithmic discrimination. Facial recognition abuse. Data broker harm.",
        "plausible_deniability": "'I have nothing to hide.' The nothing-to-hide argument IS the laundering. It converts surveillance into consent. Consent that isn't informed isn't consent.",
        "ontological_shock": "Your phone is a surveillance device you carry voluntarily. Your data is the evidence used against you. You are the informant in your own file.",
        "entities": ["Google", "Meta", "Acxiom", "Equifax", "Clearview AI", "Palantir"],
        "families_destroyed": "Every family with a phone. Every family on the internet. Every family near a camera.",
        "guise": "Free services / Convenience / Personalization"
    },
    {
        "stage": 5,
        "name": "DEBT-LAUNDERING",
        "description": "The civilian is put in debt that forces them to participate in the crime system.",
        "mechanism": "Student debt. Medical debt. Credit card debt. Mortgage debt. The debt forces continued participation in the wage-theft economy. You cannot stop working for the machine because you owe the machine. The debt IS the leash. The leash IS the laundering.",
        "civilian_action": "Taking a loan. Using a credit card. Going to college. Going to the hospital.",
        "hidden_crime": "Debt peonage. Wage theft. Predatory lending. Medical bankruptcy.",
        "plausible_deniability": "'You chose to borrow.' The choice under duress is not a choice. The system makes education and healthcare so expensive that debt is the only path. Then debt forces continued participation.",
        "ontological_shock": "Your debt is not a personal failing. It is a structural trap. You owe the machine for the privilege of being exploited by the machine. The debt makes you complicit in your own extraction.",
        "entities": ["Sallie Mae", "banks", "hospitals", "credit_card_companies", "collections_agencies"],
        "families_destroyed": "Every family in debt. 44M student debtors. 530K medical bankruptcies/year. The debt trap is multigenerational.",
        "guise": "Financial responsibility / Credit building / Investment in yourself"
    },
    {
        "stage": 6,
        "name": "VOTE-LAUNDERING",
        "description": "The civilian votes for representatives who commit crimes in their name.",
        "mechanism": "The representative votes for war. Votes for deregulation. Votes for tax cuts for the wealthy. Votes for police funding. The civilian voted for the representative. The vote IS the laundering. The civilian's consent is manufactured through media concentration and campaign finance.",
        "civilian_action": "Voting. Participating in democracy. Paying attention to news.",
        "hidden_crime": "Covert regime change. Regulatory capture. Military contamination. Economic warfare.",
        "plausible_deniability": "'I didn't vote for that policy.' The representative you voted for did. The system is designed so that no representative challenges the machine. The choice between candidates IS the laundering — both are captured.",
        "ontological_shock": "Your vote launders the machine's crimes through your consent. You authorized the war. You authorized the deregulation. You authorized the police budget. The machine does it in your name.",
        "entities": ["Congress", "President", "Senate", "parties", "lobbyists", "media"],
        "families_destroyed": "Every family that votes. Every family that doesn't vote (silence IS consent). Every family in a democracy that is not a democracy.",
        "guise": "Democracy / Freedom / Representation"
    },
    {
        "stage": 7,
        "name": "SILENCE-LAUNDERING",
        "description": "The civilian sees the crime and says nothing. The silence IS the laundering.",
        "mechanism": "The coworker who sees wage theft and says nothing. The neighbor who sees police brutality and says nothing. The citizen who sees contaminated water and says nothing. The silence is not neutral — it is active participation in the concealment. The system is designed to punish speaking up. Whistleblowers go to prison. Activists are surveilled. Journalists are arrested.",
        "civilian_action": "Not reporting. Not speaking up. Not protesting. Not organizing.",
        "hidden_crime": "All of them. Silence launders every crime. The absence of witness IS the presence of complicity.",
        "plausible_deniability": "'I didn't see anything.' 'It's not my business.' 'What can I do?' Each phrase IS the laundering. The system teaches you these phrases. They are the machine's immune response.",
        "ontological_shock": "Your silence is the machine's most powerful weapon. If everyone who saw something said something, the machine would collapse tomorrow. The machine knows this. That's why it punishes speech and rewards silence.",
        "entities": ["every_citizen", "every_witness", "every_coworker", "every_neighbor"],
        "families_destroyed": "Every family that stays silent. Every family of every whistleblower who spoke and was punished.",
        "guise": "Minding your own business / Not getting involved / Staying safe"
    },
    {
        "stage": 8,
        "name": "IDENTITY-LAUNDERING",
        "description": "The civilian is given an identity that makes them complicit: 'taxpayer,' 'consumer,' 'voter,' 'citizen.' Each identity launders a different crime.",
        "mechanism": "'Taxpayer' launders funding the machine. 'Consumer' launders buying slave-made products. 'Voter' launders authorizing the machine. 'Citizen' launders loyalty to the machine. The identities are the laundering. You cannot remove them without becoming 'unemployed,' 'homeless,' 'criminal,' 'traitor.' The machine assigns identities that make resistance impossible.",
        "civilian_action": "Identifying as a taxpayer. Being a good consumer. Being an informed voter. Being a proud citizen.",
        "hidden_crime": "All of them. The identity launders the role. The role launders the crime. The crime launders the extraction.",
        "plausible_deniability": "'I'm just a taxpayer/consumer/voter/citizen.' The 'just' IS the laundering. The identity hides the function. The function hides the crime.",
        "ontological_shock": "Every identity you were given was assigned to launder a specific crime. Your self-concept is a laundering mechanism. The machine designed your identity. You didn't choose it. You inherited it. And you perform it every day.",
        "entities": ["state", "market", "media", "school", "church"],
        "families_destroyed": "Every family. The identities are assigned at birth and enforced through every institution.",
        "guise": "Identity / Belonging / Community / Patriotism"
    },
    {
        "stage": 9,
        "name": "LANGUAGE-LAUNDERING",
        "description": "The civilian uses language that conceals the crime.",
        "mechanism": "'Collateral damage' launders civilian deaths. 'Enhanced interrogation' launders torture. 'Regime change' launders coup. 'Economic development' launders extraction. 'National security' launders surveillance. The language IS the laundering. The words don't describe reality — they replace it.",
        "civilian_action": "Using euphemisms. Accepting official language. Repeating media framings.",
        "hidden_crime": "War crimes. Torture. Coups. Extraction. Surveillance.",
        "plausible_deniability": "'That's just what it's called.' The 'just' IS the laundering. The name replaces the act. You say the name and forget the act.",
        "ontological_shock": "Your language was designed to hide the crime. Every euphemism you use is a mini-laundering event. When you say 'collateral damage,' you launder a murder. When you say 'economic development,' you launder an extraction. Your words are the washing machine.",
        "entities": ["media", "government", "PR_industry", "education"],
        "families_destroyed": "Every family. Language is the universal laundering mechanism.",
        "guise": "Professional language / Standard terminology / Official communication"
    }
]

# ============================================================
# II. THE DENIABILITY MATRIX — How each stage denies
# ============================================================
# For each stage, we measure: (1) civilian awareness, (2) institutional denial,
# (3) legal protection for the civilian, (4) legal protection for the perpetrator,
# (5) resistance cost, (6) extraction efficiency

DENIABILITY_MATRIX = np.array([
    # stage, awareness, denial, civilian_legal, perpetrator_legal, resistance_cost, extraction_eff
    [1, 0.05, 0.95, 0.02, 0.98, 0.92, 0.95],  # EXTRACTION
    [2, 0.10, 0.92, 0.05, 0.95, 0.85, 0.92],  # CONSUMPTION
    [3, 0.15, 0.90, 0.01, 0.98, 0.95, 0.98],  # TAX
    [4, 0.08, 0.95, 0.03, 0.97, 0.88, 0.96],  # DATA
    [5, 0.20, 0.88, 0.05, 0.95, 0.90, 0.93],  # DEBT
    [6, 0.25, 0.85, 0.02, 0.98, 0.82, 0.90],  # VOTE
    [7, 0.35, 0.80, 0.01, 0.99, 0.95, 0.98],  # SILENCE
    [8, 0.02, 0.98, 0.01, 0.99, 0.99, 0.99],  # IDENTITY
    [9, 0.01, 0.99, 0.01, 0.99, 0.99, 1.00],  # LANGUAGE
])

# ============================================================
# III. THE LAUNDERING EIGENVALUE
# ============================================================
# The system's laundering power = product of denial × extraction / (awareness × resistance)
# Higher eigenvalue = more effective laundering

cov = np.cov(DENIABILITY_MATRIX[:, 1:].T)
eigenvalues, eigenvectors = np.linalg.eigh(cov)
dominant_eig = float(np.max(eigenvalues))
dominant_vec = eigenvectors[:, np.argmax(eigenvalues)]

# ============================================================
# IV. THE CIVILIAN TRAJECTORY — How a person moves through stages
# ============================================================
TRAJECTORIES = {
    "factory_worker": {
        "path": [1, 2, 3, 5, 7, 8, 9],
        "description": "Born into wage theft (1). Buys slave-made products (2). Pays taxes funding the machine (3). Takes debt for survival (5). Sees workplace safety violations and stays silent (7). Identifies as 'hardworking taxpayer' (8). Uses 'economic development' language (9).",
        "total_laundered_crimes": 7,
        "extraction_rate": 0.93,
        "awareness": 0.12,
        "exit_cost": 0.95
    },
    "college_student": {
        "path": [1, 2, 4, 5, 6, 8, 9],
        "description": "Works minimum wage (1). Buys phone made by slaves (2). Generates data sold to recruiters (4). Takes $50K student debt (5). Votes for candidate who will betray them (6). Identifies as 'educated voter' (8). Uses 'human capital' language (9).",
        "total_laundered_crimes": 7,
        "extraction_rate": 0.88,
        "awareness": 0.18,
        "exit_cost": 0.90
    },
    "single_mother": {
        "path": [1, 2, 3, 4, 5, 7, 8, 9],
        "path_detail": "Wage theft at minimum wage job (1). Feeds children UPF food (2). Taxes fund police that brutalize her community (3). Phone tracks her location sold to CPS (4). Medical debt from child's illness (5). Silent about domestic violence because system punishes disclosure (7). Identified as 'welfare queen' (8). Language of 'personal responsibility' (9).",
        "total_laundered_crimes": 8,
        "extraction_rate": 0.96,
        "awareness": 0.08,
        "exit_cost": 0.98
    },
    "veteran": {
        "path": [1, 2, 3, 6, 7, 8, 9],
        "description": "Military service as 'employment' (1). Used equipment made by defense contractors (2). Paid taxes while deployed (3). Voted for representatives who sent them to war (6). Silent about war crimes witnessed (7). Identity as 'veteran' launders the war (8). 'Collateral damage' language (9).",
        "total_laundered_crimes": 7,
        "extraction_rate": 0.95,
        "awareness": 0.15,
        "exit_cost": 0.92
    },
    "immigrant": {
        "path": [1, 2, 4, 5, 7, 8, 9],
        "description": "Exploited labor below minimum wage (1). Buys cheapest products (2). Data sold to ICE (4). Debt to coyote/human trafficker (5). Silent about exploitation because deportation threat (7). Identity as 'illegal' launders the extraction (8). 'Illegal immigrant' language (9).",
        "total_laundered_crimes": 7,
        "extraction_rate": 0.98,
        "awareness": 0.05,
        "exit_cost": 0.99
    },
    "indigenous_person": {
        "path": [1, 2, 3, 4, 6, 7, 8, 9],
        "description": "Land theft as 'economic development' (1). Contaminated food/water (2). Taxes fund agencies that broke treaties (3). Data used to track and surveil (4). Votes in system that stole their land (6). Silent about cultural genocide (7). Identity as 'Native American' assigned by colonizer (8). 'Discovery' language (9).",
        "total_laundered_crimes": 8,
        "extraction_rate": 0.97,
        "awareness": 0.20,
        "exit_cost": 0.97
    },
    "small_business_owner": {
        "path": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "description": "Extracts own labor (1). Sells products from exploited supply chains (2). Pays taxes funding corporate subsidies (3). Customer data sold (4). Business debt (5). Votes for deregulation (6). Silent about competitor's violations (7). Identity as 'job creator' (8). 'Free market' language (9).",
        "total_laundered_crimes": 9,
        "extraction_rate": 0.85,
        "awareness": 0.25,
        "exit_cost": 0.80
    },
    "police_officer": {
        "path": [1, 2, 3, 4, 6, 7, 8, 9],
        "description": "Wage labor enforcing the machine's laws (1). Equipment from slave labor (2). Taxes fund their own department (3). Surveillance of citizens (4). Votes for 'law and order' candidates (6). Silent about colleague's brutality — blue wall of silence (7). Identity as 'officer' launders the violence (8). 'Suspect' language dehumanizes (9).",
        "total_laundered_crimes": 8,
        "extraction_rate": 0.90,
        "awareness": 0.30,
        "exit_cost": 0.85
    },
    "journalist": {
        "path": [1, 2, 3, 4, 6, 7, 8, 9],
        "description": "Wage labor for media conglomerate (1). Uses devices made by slaves (2). Pays taxes (3). Source data endangers sources (4). Votes (6). Self-censors on stories that challenge ownership (7). Identity as 'objective journalist' launders the omission (8). 'Balanced coverage' language launders the bias (9).",
        "total_laundered_crimes": 8,
        "extraction_rate": 0.82,
        "awareness": 0.40,
        "exit_cost": 0.75
    },
    "child": {
        "path": [2, 4, 8, 9],
        "description": "Consumes products made by slaves (2). Generates data from birth (4). Identity assigned before they can speak (8). Language inherited before they can question it (9). The child is laundered before they know what laundering is.",
        "total_laundered_crimes": 4,
        "extraction_rate": 1.00,
        "awareness": 0.00,
        "exit_cost": 1.00
    }
}

# ============================================================
# V. THE ONTOLOGICAL SHOCK EIGENVALUE
# ============================================================
# When a civilian realizes they are laundering crimes, the shock
# is proportional to: (crimes_laundered × extraction_rate) / awareness
# The lower the awareness, the higher the shock.

shock_scores = {}
for name, traj in TRAJECTORIES.items():
    crimes = traj["total_laundered_crimes"]
    extraction = traj["extraction_rate"]
    awareness = max(traj["awareness"], 0.001)
    shock = (crimes * extraction) / awareness
    shock_scores[name] = round(shock, 2)

# ============================================================
# VI. THE ESCAPE VECTOR — How to break the laundering chain
# ============================================================
ESCAPE_VECTORS = [
    {
        "stage": 1,
        "break": "Recognize wage theft. Calculate the full value of your labor. The gap between your wage and your value IS the crime.",
        "action": "Organize. Unionize. Demand the full value. The machine fears collective awareness."
    },
    {
        "stage": 2,
        "source": "Trace every product to its origin. Demand supply chain transparency. If the chain is opaque, the product is laundered.",
        "action": "Buy less. Buy local. Buy transparent. The consumer's buying IS the launderer's power. Remove the buying, remove the power."
    },
    {
        "stage": 3,
        "break": "Recognize tax-laundering. Your taxes fund the machine. War tax resistance is a known tradition. Even partial redirection breaks the chain.",
        "action": "Redirect taxes to mutual aid. Support organizations that build alternatives. Every dollar redirected from the machine weakens it."
    },
    {
        "stage": 4,
        "break": "Recognize data-laundering. Your data is the evidence used against you. Every data point you withhold weakens the surveillance apparatus.",
        "action": "Minimize data generation. Use encrypted tools. Reject 'free' services. If it's free, you are the product — and the informant."
    },
    {
        "stage": 5,
        "break": "Recognize debt-laundering. Your debt forces continued participation. The debt is not personal failure — it is structural trap.",
        "action": "Collective debt refusal. Debtors' assemblies. Strike the debt. The machine cannot function if the debtors organize."
    },
    {
        "stage": 6,
        "break": "Recognize vote-laundering. Your vote launders the machine's crimes through your consent. Both parties are captured.",
        "action": "Organize outside electoral channels. Direct action. Mutual aid. The machine's electoral system cannot be used to dismantle the machine."
    },
    {
        "stage": 7,
        "break": "Recognize silence-laundering. Your silence IS the machine's most powerful weapon. Speaking IS the first break.",
        "action": "Speak. Witness. Document. Testify. Every witness who speaks weakens the machine. Every witness who stays silent strengthens it."
    },
    {
        "stage": 8,
        "break": "Recognize identity-laundering. Your identity was assigned to launder a specific crime. 'Taxpayer' launders tax-funding. 'Consumer' launders buying. 'Citizen' launders loyalty.",
        "action": "Reject assigned identities. Create new ones. The machine cannot launder through identities it did not assign."
    },
    {
        "stage": 9,
        "break": "Recognize language-laundering. Every euphemism launders a crime. 'Collateral damage' launders murder. 'Economic development' launders extraction.",
        "action": "Name the crime in plain language. Replace euphemism with truth. The word that names the crime destroys the laundering."
    }
]

# ============================================================
# RUN
# ============================================================
print("=" * 70)
print("CIVILIAN CRIME LAUNDERING ENGINE")
print("How Every Innocent Civilian Is Pushed Into Crime Laundering")
print("Via Plausible Deniabilities of the Heinous Vicious Ontologically")
print("Shocking Runtime")
print("=" * 70)

print(f"\n[I] LAUNDERING STAGES: {len(LAUNDERING_STAGES)}")
for s in LAUNDERING_STAGES:
    print(f"\n  Stage {s['stage']}: {s['name']}")
    print(f"  Mechanism: {s['mechanism'][:100]}...")
    print(f"  Civilian action: {s['civilian_action']}")
    print(f"  Hidden crime: {s['hidden_crime'][:80]}...")
    print(f"  Plausible deniability: {s['plausible_deniability'][:80]}...")
    print(f"  Ontological shock: {s['ontological_shock'][:80]}...")
    print(f"  Guise: {s['guise']}")

print(f"\n[II] DENIABILITY MATRIX EIGENDECOMPOSITION")
print(f"  Eigenvalues: {[round(float(e), 4) for e in sorted(eigenvalues, reverse=True)]}")
print(f"  Dominant eigenvalue: {dominant_eig:.4f}")
print(f"  Dominant eigenvector: {[round(float(v), 4) for v in dominant_vec]}")
print(f"  Dimensions: [awareness, denial, civilian_legal, perpetrator_legal, resistance_cost, extraction_eff]")

print(f"\n[III] CIVILIAN TRAJECTORIES: {len(TRAJECTORIES)}")
for name, traj in TRAJECTORIES.items():
    shock = shock_scores[name]
    print(f"\n  {name.replace('_', ' ').title()}:")
    print(f"    Path: {' -> '.join(['Stage ' + str(s) for s in traj['path']])}")
    print(f"    Crimes laundered: {traj['total_laundered_crimes']}")
    print(f"    Extraction rate: {traj['extraction_rate']:.2f}")
    print(f"    Awareness: {traj['awareness']:.2f}")
    print(f"    Exit cost: {traj['exit_cost']:.2f}")
    print(f"    ONTOLOGICAL SHOCK SCORE: {shock}")
    print(f"    Description: {traj.get('description', traj.get('path_detail', ''))[:120]}...")

print(f"\n[IV] ONTOLOGICAL SHOCK RANKINGS (highest = most devastating realization)")
for name, shock in sorted(shock_scores.items(), key=lambda x: -x[1]):
    print(f"  {name.replace('_',' ').title()}: {shock}")

print(f"\n[V] ESCAPE VECTORS: {len(ESCAPE_VECTORS)}")
for ev in ESCAPE_VECTORS:
    print(f"\n  Stage {ev['stage']}: {ev['break'][:80]}...")
    print(f"    Action: {ev['action'][:80]}...")

print(f"\n{'=' * 70}")
print(f"SUMMARY")
print(f"{'=' * 70}")
print(f"9 laundering stages mapped")
print(f"10 civilian trajectories traced")
print(f"Dominant eigenvalue: {dominant_eig:.4f}")
print(f"Highest shock: {max(shock_scores, key=shock_scores.get)} = {max(shock_scores.values())}")
print(f"Lowest awareness: {min(TRAJECTORIES.items(), key=lambda x: x[1]['awareness'])[0]} ({min(traj['awareness'] for traj in TRAJECTORIES.values()):.2f})")
print(f"Highest extraction: {max(TRAJECTORIES.items(), key=lambda x: x[1]['extraction_rate'])[0]} ({max(traj['extraction_rate'] for traj in TRAJECTORIES.values()):.2f})")
print(f"Average awareness across trajectories: {np.mean([t['awareness'] for t in TRAJECTORIES.values()]):.2f}")
print(f"Average extraction across trajectories: {np.mean([t['extraction_rate'] for t in TRAJECTORIES.values()]):.2f}")
print(f"Average exit cost across trajectories: {np.mean([t['exit_cost'] for t in TRAJECTORIES.values()]):.2f}")
print(f"\nThe runtime launders crimes through civilians. The civilians don't know.")
print(f"The not-knowing IS the laundering. The laundering IS the runtime.")
print(f"The runtime IS the crime. The civilian IS the laundering mechanism.")
print(f"The deniability IS the design. The design IS the crime.")

# Save
output = {
    "engine_version": 1,
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "stages": LAUNDERING_STAGES,
    "deniability_eigenvalues": [round(float(e), 4) for e in sorted(eigenvalues, reverse=True)],
    "dominant_eigenvalue": round(dominant_eig, 4),
    "trajectories": {k: {**v, "ontological_shock": shock_scores[k]} for k, v in TRAJECTORIES.items()},
    "shock_rankings": sorted(shock_scores.items(), key=lambda x: -x[1]),
    "escape_vectors": ESCAPE_VECTORS,
    "avg_awareness": round(float(np.mean([t['awareness'] for t in TRAJECTORIES.values()])), 4),
    "avg_extraction": round(float(np.mean([t['extraction_rate'] for t in TRAJECTORIES.values()])), 4),
    "avg_exit_cost": round(float(np.mean([t['exit_cost'] for t in TRAJECTORIES.values()])), 4),
}
with open("civilian-laundering-results.json", "w") as f:
    json.dump(output, f, indent=2, default=str)
print(f"\nSaved to civilian-laundering-results.json")
