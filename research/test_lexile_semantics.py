from research.lexile_semantics import map_atom, map_text

atom = map_atom("interoopticological inferenciology")
assert atom.coined is True
assert atom.kind == "COINED_TERM"
assert atom.token_count == 2
assert atom.confidence > 0

role = map_atom("classifier")
assert role.role == "CLASSIFIER"

plural = map_atom("recognizers")
assert plural.role == "RECOGNIZER"

phenomenon = map_atom("phenomenon")
assert phenomenon.kind == "PHENOMENON"

coined_role = map_atom("truth taxonimists")
assert coined_role.coined is True
assert coined_role.role == "TAXONOMIST"

packet = map_text(
    "The truth taxonimists classify contradiction indicators and recognize "
    "temporal lineage breaks."
)
assert packet["measure_type"] == "INTERNAL_PROXY_NOT_CERTIFIED_LEXILE"
assert packet["complexity"]["word_count"] > 0
assert len(packet["mapping_sha256"]) == 64
assert "truth taxonimists" in packet["coined_terms_present"] or packet["coined_terms_present"]

print("lexile semantic tests: PASS")
