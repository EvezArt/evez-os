"""Tests for openplanter.dag — Job DAG with budgets and state tracking."""
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openplanter.dag import Job, DAG, STATES


# ---------------------------------------------------------------------------
# Job dataclass
# ---------------------------------------------------------------------------

def test_job_default_state():
    """A new Job starts in the 'pending' state."""
    job = Job(id="j1", task="build")
    assert job.state == "pending"


def test_job_default_depends_on():
    """A new Job with no dependencies has an empty depends_on list."""
    job = Job(id="j1", task="build")
    assert job.depends_on == []


def test_job_default_budget():
    """A new Job has a non-empty default budget."""
    job = Job(id="j1", task="build")
    assert "max_seconds" in job.budget
    assert job.budget["max_seconds"] > 0


def test_job_custom_fields():
    """Job stores id, task, and depends_on correctly."""
    job = Job(id="j42", task="test", depends_on=["j1", "j2"])
    assert job.id == "j42"
    assert job.task == "test"
    assert job.depends_on == ["j1", "j2"]


def test_states_constant():
    """STATES contains the expected set of state names."""
    assert "pending" in STATES
    assert "running" in STATES
    assert "done" in STATES
    assert "failed" in STATES
    assert "skipped" in STATES


# ---------------------------------------------------------------------------
# DAG.add_job
# ---------------------------------------------------------------------------

def test_dag_add_job_stores_job():
    """add_job stores the job in the DAG and it can be retrieved."""
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        job = Job(id="j1", task="compile")
        dag.add_job(job)
        assert "j1" in dag.jobs
        assert dag.jobs["j1"] is job


def test_dag_add_job_records_spine_event():
    """add_job appends a 'job_added' event to the spine."""
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        dag.add_job(Job(id="j1", task="build"))
        events = dag.spine.read_all()
        assert any(e["type"] == "job_added" and e["data"]["id"] == "j1" for e in events)


def test_dag_add_multiple_jobs():
    """Multiple jobs can be added and each is retrievable."""
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        for i in range(5):
            dag.add_job(Job(id=f"j{i}", task=f"task_{i}"))
        assert len(dag.jobs) == 5


# ---------------------------------------------------------------------------
# DAG.ready_jobs
# ---------------------------------------------------------------------------

def test_ready_jobs_no_deps():
    """A job with no dependencies is immediately ready."""
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        j = Job(id="j1", task="independent")
        dag.add_job(j)
        ready = dag.ready_jobs()
        assert j in ready


def test_ready_jobs_with_unfinished_dep():
    """A job whose dependency is still pending is not ready."""
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        j1 = Job(id="j1", task="first")
        j2 = Job(id="j2", task="second", depends_on=["j1"])
        dag.add_job(j1)
        dag.add_job(j2)
        ready = dag.ready_jobs()
        assert j2 not in ready
        assert j1 in ready


def test_ready_jobs_with_done_dep():
    """A job whose dependency is 'done' becomes ready."""
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        j1 = Job(id="j1", task="first")
        j2 = Job(id="j2", task="second", depends_on=["j1"])
        dag.add_job(j1)
        dag.add_job(j2)
        dag.mark("j1", "done")
        ready = dag.ready_jobs()
        assert j2 in ready


def test_ready_jobs_excludes_running():
    """A running job is not in ready_jobs (state != 'pending')."""
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        j = Job(id="j1", task="work")
        dag.add_job(j)
        dag.mark("j1", "running")
        assert j not in dag.ready_jobs()


def test_ready_jobs_excludes_done():
    """A completed job is not re-listed as ready."""
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        j = Job(id="j1", task="work")
        dag.add_job(j)
        dag.mark("j1", "done")
        assert j not in dag.ready_jobs()


def test_ready_jobs_unknown_dep_skipped_by_implementation():
    """The DAG skips unknown dependency IDs (vacuously true), so the job IS ready.

    This matches the current implementation: `if d in self.jobs` causes
    deps not present in the DAG to be ignored rather than blocking the job.
    """
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        j = Job(id="j1", task="work", depends_on=["unknown_dep"])
        dag.add_job(j)
        # unknown dep is skipped → all(...) is vacuously True → job IS ready
        assert j in dag.ready_jobs()


# ---------------------------------------------------------------------------
# DAG.mark
# ---------------------------------------------------------------------------

def test_mark_updates_state():
    """mark changes the job's state field."""
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        dag.add_job(Job(id="j1", task="t"))
        dag.mark("j1", "running")
        assert dag.jobs["j1"].state == "running"


def test_mark_sets_started_at_for_running():
    """mark sets started_at when transitioning to 'running'."""
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        dag.add_job(Job(id="j1", task="t"))
        assert dag.jobs["j1"].started_at == 0.0
        dag.mark("j1", "running")
        assert dag.jobs["j1"].started_at > 0.0


def test_mark_sets_finished_at_for_done():
    """mark sets finished_at when transitioning to 'done'."""
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        dag.add_job(Job(id="j1", task="t"))
        dag.mark("j1", "done")
        assert dag.jobs["j1"].finished_at > 0.0


def test_mark_sets_finished_at_for_failed():
    """mark sets finished_at when transitioning to 'failed'."""
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        dag.add_job(Job(id="j1", task="t"))
        dag.mark("j1", "failed")
        assert dag.jobs["j1"].finished_at > 0.0


def test_mark_stores_result():
    """mark stores the result dict on the job."""
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        dag.add_job(Job(id="j1", task="t"))
        dag.mark("j1", "done", result={"output": "42"})
        assert dag.jobs["j1"].result == {"output": "42"}


def test_mark_records_spine_event():
    """mark appends a 'job_state' event to the spine."""
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        dag.add_job(Job(id="j1", task="t"))
        dag.mark("j1", "done")
        events = dag.spine.read_all()
        state_events = [e for e in events if e["type"] == "job_state"]
        assert any(e["data"]["id"] == "j1" and e["data"]["state"] == "done" for e in state_events)


def test_mark_unknown_job_is_noop():
    """mark on a non-existent job ID does not raise."""
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        # Should not raise
        dag.mark("nonexistent", "done")


# ---------------------------------------------------------------------------
# DAG chained workflow
# ---------------------------------------------------------------------------

def test_linear_dag_workflow():
    """Full linear DAG: j1 → j2 → j3 each becomes ready only after predecessor done."""
    with tempfile.TemporaryDirectory() as td:
        dag = DAG(Path(td) / "dag.jsonl")
        dag.add_job(Job(id="j1", task="a"))
        dag.add_job(Job(id="j2", task="b", depends_on=["j1"]))
        dag.add_job(Job(id="j3", task="c", depends_on=["j2"]))

        assert [j.id for j in dag.ready_jobs()] == ["j1"]
        dag.mark("j1", "done")
        assert [j.id for j in dag.ready_jobs()] == ["j2"]
        dag.mark("j2", "done")
        assert [j.id for j in dag.ready_jobs()] == ["j3"]
        dag.mark("j3", "done")
        assert dag.ready_jobs() == []
