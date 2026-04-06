#!/usr/bin/env python3
"""
EVEZ Scheduler - Task scheduling, cron jobs, delayed execution
Time-based task management
"""

import json
import time
import random
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

class ScheduleType(Enum):
    ONCE = "once"
    RECURRING = "recurring"
    CRON = "cron"

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ScheduledJob:
    id: str
    name: str
    schedule_type: ScheduleType
    interval_seconds: Optional[int]  # For recurring
    cron_expression: Optional[str]   # For cron
    next_run: str
    task_data: Dict = field(default_factory=dict)
    last_run: Optional[str] = None
    status: JobStatus = JobStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None

class SchedulerEngine:
    """EVEZ Scheduler - Time-based task execution"""
    
    def __init__(self):
        self.model_name = "EVEZ-Scheduler-v1"
        self.jobs: Dict[str, ScheduledJob] = {}
        self.execution_history: List[Dict] = []
        
    def schedule_once(self, name: str, delay_seconds: int, task_data: Dict) -> str:
        """Schedule one-time task"""
        job_id = f"job_{len(self.jobs) + 1}"
        next_run = (datetime.utcnow() + timedelta(seconds=delay_seconds)).isoformat() + "Z"
        
        job = ScheduledJob(
            id=job_id,
            name=name,
            schedule_type=ScheduleType.ONCE,
            interval_seconds=None,
            cron_expression=None,
            next_run=next_run,
            task_data=task_data
        )
        
        self.jobs[job_id] = job
        return job_id
    
    def schedule_recurring(self, name: str, interval_seconds: int, task_data: Dict) -> str:
        """Schedule recurring task"""
        job_id = f"job_{len(self.jobs) + 1}"
        next_run = (datetime.utcnow() + timedelta(seconds=interval_seconds)).isoformat() + "Z"
        
        job = ScheduledJob(
            id=job_id,
            name=name,
            schedule_type=ScheduleType.RECURRING,
            interval_seconds=interval_seconds,
            cron_expression=None,
            next_run=next_run,
            task_data=task_data
        )
        
        self.jobs[job_id] = job
        return job_id
    
    def schedule_cron(self, name: str, cron_expr: str, task_data: Dict) -> str:
        """Schedule cron-based task"""
        job_id = f"job_{len(self.jobs) + 1}"
        next_run = (datetime.utcnow() + timedelta(minutes=random.randint(1, 60))).isoformat() + "Z"
        
        job = ScheduledJob(
            id=job_id,
            name=name,
            schedule_type=ScheduleType.CRON,
            interval_seconds=None,
            cron_expression=cron_expr,
            next_run=next_run,
            task_data=task_data
        )
        
        self.jobs[job_id] = job
        return job_id
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled job"""
        if job_id in self.jobs:
            del self.jobs[job_id]
            return True
        return False
    
    def run_job(self, job_id: str) -> Dict:
        """Execute a job immediately"""
        if job_id not in self.jobs:
            return {"error": "Job not found"}
        
        job = self.jobs[job_id]
        job.status = JobStatus.RUNNING
        
        # Simulate execution
        result = {
            "job_id": job_id,
            "name": job.name,
            "executed_at": datetime.utcnow().isoformat() + "Z",
            "task_data": job.task_data,
            "success": random.random() > 0.2,
            "output": f"Task {job.name} completed"
        }
        
        job.last_run = datetime.utcnow().isoformat() + "Z"
        
        if result["success"]:
            job.status = JobStatus.COMPLETED
            job.result = result
        else:
            job.status = JobStatus.FAILED
            job.error = "Execution failed"
        
        # Schedule next run for recurring
        if job.schedule_type == ScheduleType.RECURRING and job.interval_seconds:
            job.next_run = (datetime.utcnow() + timedelta(seconds=job.interval_seconds)).isoformat() + "Z"
        
        self.execution_history.append(result)
        return result
    
    def get_pending(self) -> List[Dict]:
        """Get jobs ready to run"""
        now = datetime.utcnow().isoformat() + "Z"
        pending = []
        
        for job_id, job in self.jobs.items():
            if job.next_run <= now and job.status in [JobStatus.PENDING, JobStatus.COMPLETED]:
                pending.append(vars(job))
        
        return pending
    
    def get_status(self) -> Dict:
        return {
            "model": self.model_name,
            "total_jobs": len(self.jobs),
            "pending": len(self.get_pending()),
            "executions": len(self.execution_history)
        }


# Demo
if __name__ == "__main__":
    scheduler = SchedulerEngine()
    print("=== EVEZ Scheduler ===")
    
    # Schedule jobs
    scheduler.schedule_once("one_time_task", 60, {"action": "notify"})
    scheduler.schedule_recurring("heartbeat", 30, {"action": "ping"})
    scheduler.schedule_cron("daily_report", "0 9 * * *", {"action": "report"})
    
    # Run pending
    pending = scheduler.get_pending()
    for p in pending:
        result = scheduler.run_job(p["id"])
        print(f"Ran: {result['name']} - {result['success']}")
    
    print(json.dumps(scheduler.get_status(), indent=2))