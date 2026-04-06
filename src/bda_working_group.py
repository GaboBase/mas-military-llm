"""bda_working_group.py
BDA Working Group - Debate Multi-Agente para Battle Damage Assessment
Analogia: Grupo de Analisis Post-Mision (G2/S2 nivel batallon)
Compatible con LangGraph y CrewAI
MAS-Military v1.0.0
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class Verdict(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILURE = "FAILURE"
    INCONCLUSIVE = "INCONCLUSIVE"


class AgentRole(str, Enum):
    ANALYST = "analyst"       # Oficial G2 - recopila evidencia
    CRITIC = "critic"         # Abogado del diablo - cuestiona
    SYNTHESIZER = "synthesizer" # S3 Ops - consolida
    COMMANDER = "commander"   # Meta-Agente - decision final


@dataclass
class AgentVote:
    agent_id: str
    role: AgentRole
    vote: Verdict
    confidence: float          # 0.0 - 1.0
    rationale: str
    pir_refs: List[str] = field(default_factory=list)
    sir_refs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "vote": self.vote.value,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "pir_refs": self.pir_refs,
            "sir_refs": self.sir_refs,
        }


@dataclass
class BDAConsensus:
    achieved: bool
    verdict: Verdict
    confidence: float
    rounds: int
    dissent_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "achieved": self.achieved,
            "verdict": self.verdict.value,
            "confidence": self.confidence,
            "rounds": self.rounds,
            "dissent_count": self.dissent_count,
        }


class BDAWorkingGroup:
    """Grupo de trabajo BDA - implementa debate multi-ronda hasta consenso.

    Analogia Militar:
      - Analyst   = S2 Intelligence Officer (recopila BDA raw)
      - Critic    = Devil's Advocate / Red Team
      - Synthesizer = S3 Operations (consolida hallazgos)
      - Commander = CO / Meta-Agente (decision binding)

    Analogia LLM:
      - Cada AgentVote es un LLM call con prompt especializado
      - El debate simula el Collaborative Filtering de OODA
      - El consenso es el Shared Situational Awareness digital
    """

    CONSENSUS_THRESHOLD = 0.66   # 2/3 mayoria
    MAX_ROUNDS = 3

    def __init__(self, session_id: str, task_id: str):
        self.session_id = session_id
        self.task_id = task_id
        self.votes: List[AgentVote] = []
        self.rounds_completed = 0
        self.lessons_learned: List[Dict[str, Any]] = []

    def cast_vote(self, vote: AgentVote) -> None:
        """Registrar voto de un agente (equivale a radio report en campo)."""
        self.votes.append(vote)

    def _tally(self) -> Dict[Verdict, float]:
        """Conteo ponderado por confidence (equivale a credibilidad de fuente)."""
        tally: Dict[Verdict, float] = {v: 0.0 for v in Verdict}
        total_weight = sum(v.confidence for v in self.votes)
        if total_weight == 0:
            return tally
        for vote in self.votes:
            tally[vote.vote] += vote.confidence / total_weight
        return tally

    def evaluate_consensus(self) -> BDAConsensus:
        """Evaluar si se alcanzo consenso. Devuelve BDAConsensus."""
        self.rounds_completed += 1
        tally = self._tally()
        winning_verdict = max(tally, key=lambda k: tally[k])
        winning_pct = tally[winning_verdict]
        achieved = winning_pct >= self.CONSENSUS_THRESHOLD
        dissent = sum(1 for v in self.votes if v.vote != winning_verdict)
        return BDAConsensus(
            achieved=achieved,
            verdict=winning_verdict,
            confidence=round(winning_pct, 4),
            rounds=self.rounds_completed,
            dissent_count=dissent,
        )

    def add_lesson(self, category: str, observation: str,
                   action_item: Optional[str] = None) -> None:
        """Registrar leccion aprendida post-mision."""
        self.lessons_learned.append({
            "category": category,
            "observation": observation,
            "action_item": action_item,
        })

    def export(self, consensus: BDAConsensus,
               escalate: bool = False,
               next_trigger: Optional[str] = None) -> Dict[str, Any]:
        """Exportar resultado final en formato schemas/bda_output.json."""
        return {
            "session_id": self.session_id,
            "task_id": self.task_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "consensus": consensus.to_dict(),
            "agents_votes": [v.to_dict() for v in self.votes],
            "damage_assessment": {
                "objectives_met": None,
                "objectives_total": None,
                "completion_pct": consensus.confidence if consensus.achieved else None,
                "collateral_issues": [],
                "follow_up_required": not consensus.achieved,
            },
            "lessons_learned": self.lessons_learned,
            "escalate_to_meta_agent": escalate,
            "next_mission_trigger": next_trigger,
        }


# ---------------------------------------------------------------------------
# Factory helpers para CrewAI / LangGraph
# ---------------------------------------------------------------------------

def create_bda_group(task_id: Optional[str] = None,
                     session_id: Optional[str] = None) -> BDAWorkingGroup:
    """Instanciar BDAWorkingGroup con IDs autogenerados si no se proveen."""
    return BDAWorkingGroup(
        session_id=session_id or str(uuid.uuid4()),
        task_id=task_id or str(uuid.uuid4()),
    )


def quick_bda(votes_data: List[Dict[str, Any]],
              task_id: Optional[str] = None) -> Dict[str, Any]:
    """Helper: crear grupo, inyectar votos, evaluar y exportar en una llamada."""
    group = create_bda_group(task_id=task_id)
    for v in votes_data:
        group.cast_vote(AgentVote(
            agent_id=v["agent_id"],
            role=AgentRole(v["role"]),
            vote=Verdict(v["vote"]),
            confidence=float(v["confidence"]),
            rationale=v["rationale"],
            pir_refs=v.get("pir_refs", []),
            sir_refs=v.get("sir_refs", []),
        ))
    consensus = group.evaluate_consensus()
    escalate = not consensus.achieved
    return group.export(consensus, escalate=escalate)
