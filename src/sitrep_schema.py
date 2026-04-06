# src/sitrep_schema.py
# MAS-Military: Schema canónico del SITREP
# Equivale al formato SITREP estandarizado de la doctrina militar.
# Todo agente worker produce un SitrepMessage al terminar su tarea.

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
import uuid, json


class OperationalState(str, Enum):
    FULLY_OPERATIONAL = "FULLY_OPERATIONAL"
    DEGRADED          = "DEGRADED"
    NON_OPERATIONAL   = "NON_OPERATIONAL"
    ESCALATE          = "ESCALATE"


class Phase(str, Enum):
    PLANNING    = "planning"
    EXECUTING   = "executing"
    ASSESSING   = "assessing"
    ESCALATING  = "escalating"


class AgentRole(str, Enum):
    META_AGENT = "meta_agent"
    SUPERVISOR = "supervisor"
    WORKER     = "worker"


class EscalationSeverity(int, Enum):
    INFO     = 1
    WARNING  = 2
    CRITICAL = 3
    ABORT    = 4


@dataclass
class ActionRecord:
    action:       str
    result:       str
    artifact_ref: Optional[str] = None


@dataclass
class IntelligenceReport:
    discoveries: List[str] = field(default_factory=list)
    confirmed:   List[str] = field(default_factory=list)
    unresolved:  List[str] = field(default_factory=list)


@dataclass
class ObstacleReport:
    blocking:       List[str]      = field(default_factory=list)
    non_blocking:   List[str]      = field(default_factory=list)
    pace_activated: Optional[str]  = None


@dataclass
class NextSteps:
    immediate:              str
    pending_decision:       Optional[str] = None
    awaiting_from_superior: Optional[str] = None


@dataclass
class EscalationRequest:
    required: bool               = False
    level:    Optional[str]      = None
    reason:   Optional[str]      = None
    severity: EscalationSeverity = EscalationSeverity.INFO


@dataclass
class BDARequest:
    trigger_bda: bool          = False
    reason:      Optional[str] = None


@dataclass
class SitrepMessage:
    """Unidad atomica de comunicacion del sistema MAS-Military."""
    agent_id:       str
    role:           AgentRole
    parent_task_id: str
    session_id:     str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp:      str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    operational_state: OperationalState = OperationalState.FULLY_OPERATIONAL
    completion_pct:    float             = 0.0
    current_phase:     Phase             = Phase.EXECUTING
    actions_taken:  List[ActionRecord]  = field(default_factory=list)
    intelligence:   IntelligenceReport  = field(default_factory=IntelligenceReport)
    obstacles:      ObstacleReport      = field(default_factory=ObstacleReport)
    next_steps:     Optional[NextSteps] = None
    escalation:     EscalationRequest   = field(default_factory=EscalationRequest)
    bda_request:    BDARequest          = field(default_factory=BDARequest)
    pir_id:         Optional[str]       = None
    sir_id:         Optional[str]       = None
    attention_score: Optional[float]    = None

    def to_json(self) -> str:
        def _s(obj):
            if hasattr(obj, '__dict__'):
                return {k: _s(v) for k, v in obj.__dict__.items()}
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, list):
                return [_s(i) for i in obj]
            return obj
        return json.dumps(_s(self), indent=2, ensure_ascii=False)

    @property
    def is_critical(self) -> bool:
        return self.escalation.severity >= EscalationSeverity.CRITICAL

    @property
    def needs_bda(self) -> bool:
        return self.bda_request.trigger_bda

    def summary(self) -> str:
        return (
            f"[{self.agent_id}|{self.current_phase.value}|"
            f"{self.completion_pct:.0%}|SEV={self.escalation.severity.value}] "
            f"{self.next_steps.immediate if self.next_steps else 'No next steps'}"
        )
