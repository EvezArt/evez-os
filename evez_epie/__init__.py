"""EPIE: Evidence and Inference Kernel, standard-library-only reference implementation."""
from .kernel import EventLedger, bayesian_update, entropy_bits, expected_information_gain, rank_tests, retention_score, rank_retention, canonical_hash
from .retention import select_hot_index
from .research import expected_value_of_sample_information, rank_decision_tests, choose_next_test, prequential_log_score, realized_research_reward, negative_brier_score, aggregate_research_reward
from .spine_adapter import append_to_spine, verify_spine, sync_ledger_to_spine

__all__ = ["EventLedger", "bayesian_update", "entropy_bits", "expected_information_gain", "rank_tests", "retention_score", "rank_retention", "canonical_hash", "select_hot_index", "expected_value_of_sample_information", "rank_decision_tests", "choose_next_test", "prequential_log_score", "realized_research_reward", "negative_brier_score", "aggregate_research_reward", "append_to_spine", "verify_spine", "sync_ledger_to_spine"]
