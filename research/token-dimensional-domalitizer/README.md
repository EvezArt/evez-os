# Token-Dimensional Domalitizer (TDD)

A deterministic, provenance-first lexical research prototype for EVEZ-OS.

**Domalitization** is a coined operational term: mapping each token into multiple *domains* (orthography, phonology, morphology, etymology, semantics, pragmatics, time, and evidence) while retaining the original token and the provenance of every assertion.

This is a computational instrument, not an etymology oracle. It never promotes sound resemblance to historical descent. Missing evidence stays `UNKNOWN`; generated interpretations stay `PROPOSED`.

## What it does

- Preserves the original input and token offsets.
- Builds a token-dimensional record with eight independently populated dimensions.
- Separates attested facts, user-supplied assertions, hypotheses, and unknowns.
- Supports explicit cross-semantic edges between tokens/concepts.
- Computes deterministic lexical fingerprints and a reversible round-trip check.
- Emits JSON suitable for an append-only EVEZ Spine or downstream graph database.
- Uses only the Python standard library; suitable for Termux and offline operation.

## Run

```bash
python3 domalitizer.py analyze "tokendimensional domalitizing domain"
python3 domalitizer.py analyze "permaloot metamemetic metametalinguistic" --pretty
python3 domalitizer.py validate lexicon.seed.json
python3 -m unittest -v
```

## Token dimensions

| Dimension | Stored fields |
|---|---|
| Orthographic | surface form, normalized form, character span |
| Phonological | IPA, syllables, notes; only supplied/attested values |
| Morphological | proposed segments, root, affixes, derivation |
| Etymological | language, ancestor, cognates, source, status |
| Semantic | glosses, concepts, sense IDs |
| Pragmatic | context, register, intended use |
| Temporal | first-known date, period, change history |
| Evidence | source, method, confidence, epistemic status |

## Evidence contract

Allowed statuses: `ATTESTED`, `USER_SUPPLIED`, `PROPOSED`, `INFERRED`, `UNKNOWN`, `REJECTED`.

- `ATTESTED` requires a source reference.
- `USER_SUPPLIED` records authorship, not external verification.
- `PROPOSED` is a generated candidate, never a historical fact.
- `INFERRED` must name its method and uncertainty.
- `UNKNOWN` is a valid result, not a failure.
- `REJECTED` preserves a falsified candidate and its reason.

## Token-dimensional domain vector

Each token receives a sparse domain vector. A dimension is marked present only when the record contains a value; unknown dimensions are not silently imputed. The vector is descriptive, not a measure of intelligence, consciousness, or semantic truth.

## Cross-semantic edges

Edges require an explicit relation label such as `translation_candidate`, `same_concept_candidate`, `sound_association`, `cognate_candidate`, or `contrast`. Every edge carries provenance and status. Similarity is not ancestry.

## Round-trip

The engine's first round-trip guarantee is exact preservation of the original string and token spans through serialization. Semantic round-trip equivalence requires a separately supplied reconstruction and is not claimed by this prototype.

## Extension points

1. Add PanPhon/IPA features as an optional plugin.
2. Import CLDF/Lexibank/DBnary records with source-level provenance.
3. Add graph storage and persistent homology over token-concept networks.
4. Add human-rated semantic equivalence and calibrated uncertainty.
5. Connect emitted events to the EVEZ append-only Spine.

## Example

```json
{
  "surface": "domalitizing",
  "dimensions": {
    "orthographic": {"normalized": "domalitizing"},
    "phonological": {"ipa": null, "status": "UNKNOWN"},
    "morphological": {"segments": [], "status": "PROPOSED"},
    "etymological": {"origin": null, "status": "UNKNOWN"},
    "semantic": {"glosses": ["mapping tokens across multiple domains"], "status": "USER_SUPPLIED"},
    "pragmatic": {"register": "coined technical vocabulary"},
    "temporal": {"first_recorded_in_project": "2026-11-08"},
    "evidence": {"status": "USER_SUPPLIED"}
  }
}
```

The sample gloss is an operational interpretation for this project, not a claim about an established word history.
