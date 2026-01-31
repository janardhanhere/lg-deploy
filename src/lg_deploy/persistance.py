from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict


def utc_now() -> datetime:
    """Return current UTC time with timezone info."""
    return datetime.now(timezone.utc)


class ExecutionStatus(Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Execution:
    execution_id: str
    status: ExecutionStatus
    created_at: datetime = field(default_factory=utc_now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[dict] = None
    error: Optional[str] = None


class InMemoryPersistence:
    def __init__(self):
        self._executions: Dict[str, Execution] = {}
    
    def create(self, execution_id: str) -> Execution:
        execution = Execution(
            execution_id=execution_id,
            status=ExecutionStatus.QUEUED
        )
        self._executions[execution_id] = execution
        return execution
    
    def get(self, execution_id: str) -> Optional[Execution]:
        return self._executions.get(execution_id)
    
    def update_status(self, execution_id: str, status: ExecutionStatus):
        execution = self._executions.get(execution_id)
        if execution:
            execution.status = status
            if status == ExecutionStatus.RUNNING:
                execution.started_at = utc_now()
            elif status in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED):
                execution.completed_at = utc_now()
    
    def set_result(self, execution_id: str, result: dict):
        execution = self._executions.get(execution_id)
        if execution:
            execution.result = result
    
    def set_error(self, execution_id: str, error: str):
        execution = self._executions.get(execution_id)
        if execution:
            execution.error = error
