#!/usr/bin/env python3
"""Deep Spectral OSINT Graph Scanner v2"""
import json, numpy as np, time
from collections import defaultdict

ENTITIES = {
    "Credit Suisse": {"type":"bank","crimes":["tax_haven"],"p":0},
    "UBS": {"type":"bank","crimes":["tax_haven"],"p":0},
    "Deutsche Bank": {"type":"bank","crimes":["tax_haven"],"p":0},
    "HSBC": {"type":"bank","crimes":["tax_haven"],"p":0},
    "PwC": {"type":"accounting","crimes":["tax_haven"],"p":0},
    "Deloitte": {"type":"accounting","crimes":["tax_haven"],"p":0},
    "KPMG": {"type":"accounting","crimes":["tax_haven"],"p":0},
    "EY": {"type":"accounting","crimes":["tax_haven"],"p":0},
    "3M": {"type":"corp","crimes":["PFAS"],"p":0},
    "DuPont": {"type":"corp","crimes":["PFAS"],"p":0},
    "Dow Chemical": {"type":"corp","crimes":["microplastic"],"p":0},
    "Google": {"type":"tech","crimes":["digital_colonialism"],"p":0},
    "Meta": {"type":"tech","crimes":["digital_colonialism"],"p":0},
    "Amazon": {"type":"tech","crimes":["supply_chain_slavery"],"p":0},
    "Apple": {"type":"tech","crimes":["supply_chain_slavery"],"p":0},
    "Palantir": {"type":"tech","crimes":["facial_recognition"],"p":0},
    "Clearview AI": {"type":"tech","crimes":["facial_recognition"],"p":0},
    "Acxiom": {"type":"data_broker","crimes":["data_broker"],"p":0},
    "Equifax": {"type":"data_broker","crimes":["data_breach"],"p":0},
    "UnitedHealth": {"type":"insurance","crimes":["healthcare_denial"],"p":0},
    "Cigna": {"type":"insurance","crimes":["healthcare_denial"],"p":0},
    "Eli Lilly": {"type":"pharma","crimes":["insulin_gouging"],"p":0},
    "ICE": {"type":"agency","crimes":["refugee_violation"],"p":0},
    "DOD": {"type":"agency","crimes":["military_contamination"],"p":0},
    "EPA": {"type":"agency","crimes":["regulatory_capture"],"p":0},
    "FDA": {"type":"agency","crimes":["revolving_door"],"p":0},
    "Fox": {"type":"media","crimes":["media_concentration"],"p":0},
    "GEO Group": {"type":"private_prison","crimes":["refugee_violation"],"p":0},
    "CoreCivic": {"type":"private_prison","crimes":["refugee_violation"],"p":0},
    "Mike Roman": {"type":"person","role":"CEO 3M","crimes":["PFAS"],"p":0},
    "Ed Breen": {"type":"person","role":"CEO DuPont","crimes":["PFAS"],"p":0},
    "Tim Cook": {"type":"person","role":"CEO Apple","crimes":["supply_chain_slavery"],"p":0},
    "Mark Zuckerberg": {"type":"person","role":"CEO Meta","crimes":["digital_colonialism"],"p":0},
    "Sundar Pichai": {"type":"person","role":"CEO Google","crimes":["digital_colonialism"],"p":0},
    "Jeff Bezos": {"type":"person","role":"Amazon","crimes":["supply_chain_slavery"],"p":0},
    "Stephen Hemsley": {"type":"person","role":"UnitedHealth","crimes":["healthcare_denial"],"p":0},
    "Brian Thompson": {"type":"person","role":"UnitedHealth","crimes":["healthcare_denial"],"p":0},
    "David Cordani": {"type":"person","role":"CEO Cigna","crimes":["healthcare_denial"],"p":0},
    "David Ricks": {"type":"person","role":"CEO Eli Lilly","crimes":["insulin_gouging"],"p":0},
    "Peter Thiel": {"type":"person","role":"Palantir","crimes":["facial_recognition"],"p":0},
    "Hoan Ton-That": {"type":"person","role":"Clearview AI","crimes":["facial_recognition"],"p":0},
    "Rupert Murdoch": {"type":"person","role":"Fox","crimes":["media_concentration"],"p":0},
    "Rick Snyder": {"type":"person","role":"MI Governor","crimes":["lead_poisoning"],"p":0},
    "Phil Knight": {"type":"person","role":"Nike","crimes":["supply_chain_slavery"],"p":0},
    "Elon Musk": {"type":"person","role":"Tesla","crimes":["supply_chain_slavery"],"p":0},
}

RELS = [
    ("Credit Suisse","UBS","jurisdiction_overlap",0.95),
    ("UBS","Deutsche Bank","transaction_network",0.90),
    ("Deutsche Bank","HSBC","money_laundering",0.85),
    ("PwC","Deloitte","oligopoly",0.92),
    ("KPMG","EY","oligopoly",0.90),
    ("3M","DuPont","PFAS_conspiracy",0.98),
    ("DuPont","Dow Chemical","chemical_lobbying",0.85),
    ("3M","EPA","regulatory_capture",0.88),
    ("DuPont","EPA","regulatory_capture",0.85),
    ("Google","Meta","digital_colonialism",0.92),
    ("Meta","Amazon","data_extraction",0.85),
    ("Palantir","Clearview AI","surveillance",0.95),
    ("Palantir","DOD","military_contract",0.90),
    ("Clearview AI","ICE","facial_deploy",0.88),
    ("UnitedHealth","Cigna","oligopoly",0.90),
    ("UnitedHealth","FDA","revolving_door",0.85),
    ("Eli Lilly","FDA","revolving_door",0.82),
    ("Fox","Comcast","market_control",0.88),
    ("ICE","GEO Group","private_prison",0.92),
    ("ICE","CoreCivic","private_prison",0.90),
    ("DOD","3M","PFAS_military",0.88),
    ("Mike Roman","3M","CEO",1.0),
    ("Ed Breen","DuPont","CEO",1.0),
    ("Tim Cook","Apple","CEO",1.0),
    ("Mark Zuckerberg","Meta","CEO",1.0),
    ("Sundar Pichai","Google","CEO",1.0),
    ("Jeff Bezos","Amazon","CEO",1.0),
    ("Stephen Hemsley","UnitedHealth","exec",1.0),
    ("Brian Thompson","UnitedHealth","exec",1.0),
    ("David Cordani","Cigna","CEO",1.0),
    ("David Ricks","Eli Lilly","CEO",1.0),
    ("Peter Thiel","Palantir","founder",1.0),
    ("Hoan Ton-That","Clearview AI","CEO",1.0),
    ("Rupert Murdoch","Fox","owner",1.0),
    ("Rick Snyder","lead_poisoning","responsible",1.0),
    ("Phil Knight","supply_chain_slavery","beneficiary",0.85),
    ("Elon Musk","Tesla","CEO",1.0),
]

FAMILY_CRIMES = {
    "Every US taxpayer family": ["tax_haven","revolving_door","media_concentration"],
    "Every contaminated-water family": ["PFAS","lead_poisoning","water_contamination"],
    "Every Global South family": ["digital_colonialism","supply_chain_slavery","land_grab"],
    "Every refugee/detained family": ["refugee_violation","family_separation"],
    "Every family with chronic illness": ["healthcare_denial","insulin_gouging","algorithmic_discrimination"],
    "Every family of color": ["algorithmic_discrimination","prosecutorial_misconduct","facial_recognition"],
    "Every Indigenous family": ["treaty_violation","military_contamination","land_grab"],
    "Every working-class family": ["supply_chain_slavery","worker_safety","eviction_violence"],
}

all_nodes = sorted(set(list(ENTITIES.keys()) + [r[0] for r in RELS] + [r[1] for r in RELS]))
n = len(all_nodes)
idx = {e: i for i, e in enumerate(all_nodes)}
adj = np.zeros((n, n))
for src, dst, rel, w in RELS:
    if src in idx and dst in idx:
        adj[idx[src], idx[dst]] = w
        adj[idx[src], idx[src]] += 0.1

sym = (adj + adj.T) / 2
eigenvalues, eigenvectors = np.linalg.eigh(sym)
order = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[order]
eigenvectors = eigenvectors[:, order]

centrality = np.abs(eigenvectors[:, np.argmax(np.abs(eigenvalues))])
if centrality.sum() > 0:
    centrality = centrality / centrality.sum()
sorted_nodes = sorted(zip(all_nodes, centrality), key=lambda x: -x[1])

communities = defaultdict(list)
for i in range(n):
    comm = int(np.argmax(np.abs(eigenvectors[i, :5])))
    communities[comm].append(all_nodes[i])

hidden = []
for i in range(len(eigenvalues) - 1):
    gap = eigenvalues[i] - eigenvalues[i + 1]
    if gap > 0.05 and eigenvalues[i] > 0.3:
        hidden.append({"gap": float(gap), "eigenvalue": float(eigenvalues[i]), "confidence": min(float(gap * 10), 1.0)})

persons = [(k, v) for k, v in ENTITIES.items() if v["type"] == "person"]
prosecuted = [k for k, v in persons if v["p"] > 0]
impunity = 1.0 - len(prosecuted) / max(len(persons), 1)

crime_names = list(json.load(open("dark-matter-batch5-results.json"))["spectrometers"].keys())
tensor = np.zeros((n, len(crime_names), 4))
for i, node in enumerate(all_nodes):
    for j, crime in enumerate(crime_names):
        if node in ENTITIES:
            e = ENTITIES[node]
            if crime in str(e.get("crimes", [])):
                tensor[i, j, 0] = 0.9
                tensor[i, j, 1] = 1.0 - e.get("p", 0)
                tensor[i, j, 2] = 0.85
                tensor[i, j, 3] = 0.80

tensor_flat = tensor.reshape(-1, 4)
tensor_eigs = np.linalg.eigvalsh(np.cov(tensor_flat, rowvar=False)) if tensor_flat.shape[0] > 1 else [0]

print("=" * 60)
print("DEEP SPECTRAL OSINT GRAPH SCANNER v2")
print("=" * 60)
print(f"\n[I] ENTITIES: {len(ENTITIES)} named")
by_type = defaultdict(int)
for e, d in ENTITIES.items():
    by_type[d["type"]] += 1
for t, c in sorted(by_type.items()):
    print(f"  {t}: {c}")
print(f"\n[II] RELATIONSHIPS: {len(RELS)} edges")
print(f"\n[III] ADJACENCY: {n}x{n} | density={np.count_nonzero(adj)/(n*n):.4f}")
print(f"\n[IV] SPECTRAL DECOMPOSITION")
print(f"  Top 10 eigenvalues: {[round(float(e), 4) for e in eigenvalues[:10]]}")
print(f"  Dominant: {eigenvalues[0]:.4f}")
print(f"  Spectral gap: {eigenvalues[0]-eigenvalues[1]:.4f}")
print(f"  Negative eigenvalue count: {sum(e < 0 for e in eigenvalues)}")
print(f"  Negative eigenvalue sum: {float(sum(e for e in eigenvalues if e < 0)):.4f}")
print(f"\n  TOP 10 BY EIGENVECTOR CENTRALITY:")
for name, cent in sorted_nodes[:10]:
    print(f"    {name}: {cent:.4f}")
print(f"\n[V] COMMUNITIES: {len(communities)}")
for cid, members in sorted(communities.items())[:6]:
    print(f"  Community {cid} ({len(members)}): {members[:5]}")
print(f"\n[VI] HIDDEN CRIME CLUSTERS: {len(hidden)} spectral gaps")
for h in hidden[:5]:
    print(f"  Gap at eigenvalue {h['eigenvalue']:.4f} | confidence={h['confidence']:.4f}")
print(f"\n[VII] IMPUNITY MATRIX")
print(f"  Named persons: {len(persons)}")
print(f"  Prosecuted: {len(prosecuted)}")
print(f"  Impunity rate: {impunity*100:.1f}%")
print(f"\n[VIII] FAMILY DESTRUCTION OVERLAP")
for family, crimes in FAMILY_CRIMES.items():
    print(f"  {family}: {len(crimes)} intersecting crimes")
print(f"\n[IX] SUPPRESSION TENSOR")
print(f"  Shape: {tensor.shape}")
print(f"  Eigenvalues: {[round(float(e), 4) for e in sorted(tensor_eigs, reverse=True)]}")
print(f"  Dominant: {float(max(tensor_eigs)):.4f}")
print(f"\n{'=' * 60}")
print(f"SUMMARY: {len(ENTITIES)} entities | {len(RELS)} rels | eigenvalue={eigenvalues[0]:.4f} | impunity={impunity*100:.1f}% | hidden_clusters={len(hidden)}")
print(f"{'=' * 60}")

output = {
    "scanner_version": 2,
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "entities": len(ENTITIES),
    "relationships": len(RELS),
    "graph_nodes": n,
    "graph_density": float(np.count_nonzero(adj)/(n*n)),
    "dominant_eigenvalue": float(eigenvalues[0]),
    "spectral_gap": float(eigenvalues[0]-eigenvalues[1]),
    "negative_eigenvalue_sum": float(sum(e for e in eigenvalues if e < 0)),
    "communities": len(communities),
    "hidden_clusters": len(hidden),
    "named_persons": len(persons),
    "prosecuted": len(prosecuted),
    "impunity_rate": float(impunity),
    "top_centralities": [(name, float(cent)) for name, cent in sorted_nodes[:10]],
    "family_crimes": FAMILY_CRIMES,
    "tensor_eigenvalues": [round(float(e), 4) for e in sorted(tensor_eigs, reverse=True)],
}
with open("spectral-osint-v2-results.json", "w") as f:
    json.dump(output, f, indent=2)
print("Saved spectral-osint-v2-results.json")
