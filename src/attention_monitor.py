# src/attention_monitor.py
# MAS-Military: Monitor de Atencion - Guardia de Escuadra del sistema
# Implementa la logica PIR/SIR/ANCLA para prevenir Agent Drift.
# Equivale al guardia de escuadra: su unica mision es vigilar la atencion.

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum


class AttentionStatus(str, Enum):
    ON_MISSION     = "ON_MISSION"
    DRIFT_WARNING  = "DRIFT_WARNING"
    DRIFT_CRITICAL = "DRIFT_CRITICAL"


@dataclass
class PIR:
    """Priority Intelligence Requirement - aprobado por el Meta-Agente."""
    pir_id:           str
    question:         str
    decision_enabled: str
    priority:         int
    status:           str = "open"


@dataclass
class SIR:
    """Specific Information Requirement - subtarea que alimenta un PIR."""
    sir_id:           str
    parent_pir_id:    str
    parent_sir_id:    Optional[str] = None
    description:      str = ""
    decision_enabled: str = ""
    agent_assigned:   Optional[str] = None
    status:           str = "pending"
    depth:            int = 0


@dataclass
class AttentionEvaluation:
    action_id:          str
    action_description: str
    pir_alignment:      float
    anchor_alignment:   float
    attention_score:    float
    status:             AttentionStatus
    recommendation:     str
    matched_pir:        Optional[str]
    token_pct:          float = 0.0


class AttentionMonitor:
    """
    Guardia de escuadra del sistema MAS-Military.
    Evalua cada accion contra PIRs activos y el ancla fija.
    Previene Agent Drift (Task Saturation en terminos militares).

    Thresholds:
      >= 0.40  : ON_MISSION
      >= 0.20  : DRIFT_WARNING  - re-justificar subtarea
      <  0.20  : DRIFT_CRITICAL - FRAGO cognitivo; reinyectar ancla
    """

    DRIFT_WARNING_THRESHOLD  = 0.40
    DRIFT_CRITICAL_THRESHOLD = 0.20
    CONTEXT_REINJECTION_PCT  = 0.40
    MAX_SUBTASK_CONTEXT_PCT  = 0.20  # Regla del 20%

    def __init__(self, anchor: str, pirs: List[PIR], context_window: int = 200_000):
        self.anchor         = anchor
        self.pirs           = {p.pir_id: p for p in pirs}
        self.context_window = context_window
        self.active_pir_id  = pirs[0].pir_id if pirs else None
        self.sir_tree:      Dict[str, SIR]            = {}
        self.eval_history:  List[AttentionEvaluation] = []
        self._token_count:  int                        = 0

    def register_sir(self, sir: SIR) -> str:
        """Rechaza nodos huerfanos. Equivale al sistema de ordenes militares."""
        if sir.parent_pir_id not in self.pirs:
            raise ValueError(
                f"SIR '{sir.sir_id}' huerfano: PIR '{sir.parent_pir_id}' no existe. "
                f"[DRIFT PREVENTED]"
            )
        if not sir.decision_enabled.strip():
            raise ValueError(
                f"SIR '{sir.sir_id}' no declara decision_enabled. "
                f"Completa el campo antes de registrar."
            )
        self.sir_tree[sir.sir_id] = sir
        return f"SIR '{sir.sir_id}' registrado -> PIR '{sir.parent_pir_id}'"

    def set_active_pir(self, pir_id: str) -> None:
        if pir_id not in self.pirs:
            raise ValueError(f"PIR '{pir_id}' no registrado.")
        self.active_pir_id = pir_id

    def evaluate_action(
        self,
        action_id: str,
        action_description: str,
        token_cost: int = 0,
    ) -> AttentionEvaluation:
        """Evalua si una accion esta dentro del arbol de atencion."""
        active_pir = self.pirs.get(self.active_pir_id)
        pir_text   = active_pir.question if active_pir else ""
        pir_rel    = self._semantic_similarity(action_description, pir_text)
        anchor_rel = self._semantic_similarity(action_description, self.anchor)
        score      = 0.7 * pir_rel + 0.3 * anchor_rel
        token_pct  = token_cost / self.context_window if self.context_window else 0.0
        if token_pct > self.MAX_SUBTASK_CONTEXT_PCT:
            score *= 0.7
        if score >= self.DRIFT_WARNING_THRESHOLD:
            status = AttentionStatus.ON_MISSION
            rec    = f"CONTINUE - alineado con PIR '{self.active_pir_id}'. Score: {score:.2f}"
        elif score >= self.DRIFT_CRITICAL_THRESHOLD:
            status = AttentionStatus.DRIFT_WARNING
            rec    = f"REDIRECT - score={score:.2f}. Declara a que PIR contribuye."
        else:
            status = AttentionStatus.DRIFT_CRITICAL
            rec    = f"HALT - drift critico score={score:.2f}. Reinyectando ancla."
        evaluation = AttentionEvaluation(
            action_id=action_id, action_description=action_description,
            pir_alignment=pir_rel, anchor_alignment=anchor_rel,
            attention_score=score, status=status, recommendation=rec,
            matched_pir=self.active_pir_id, token_pct=token_pct,
        )
        self.eval_history.append(evaluation)
        self._token_count += token_cost
        return evaluation

    def inject_anchor_if_needed(self, current_context: str) -> str:
        """Reinyecta el ancla cuando el contexto supera el 40%."""
        used_pct = self._token_count / self.context_window
        if used_pct >= self.CONTEXT_REINJECTION_PCT:
            pir_q = self.pirs[self.active_pir_id].question if self.active_pir_id else ""
            return (
                f"=== ANCLA DEL SISTEMA (REINYECCION) ===\n{self.anchor}\n"
                f"=== PIR ACTIVO: {self.active_pir_id} ===\n{pir_q}\n"
                f"=== CONTEXTO COMPRIMIDO ===\n"
                + "\n".join(current_context.split("\n")[-20:])
            )
        return current_context

    def get_drift_report(self) -> dict:
        """Reporte para el BDA Working Group."""
        total    = len(self.eval_history)
        warnings = sum(1 for e in self.eval_history if e.status == AttentionStatus.DRIFT_WARNING)
        crits    = sum(1 for e in self.eval_history if e.status == AttentionStatus.DRIFT_CRITICAL)
        avg      = sum(e.attention_score for e in self.eval_history) / total if total else 0
        return {
            "total_evaluated": total, "on_mission": total - warnings - crits,
            "drift_warnings": warnings, "drift_criticals": crits,
            "avg_attention_score": round(avg, 3),
            "health": "OTTIMO" if avg >= 0.7 else "BUONA" if avg >= 0.4 else "DEFICIENTE",
            "active_pir": self.active_pir_id, "sir_tree_size": len(self.sir_tree),
            "context_used_pct": round(self._token_count / self.context_window, 3),
        }

    @staticmethod
    def _semantic_similarity(text_a: str, text_b: str) -> float:
        """Similitud por tokens compartidos. En prod: usar embeddings."""
        if not text_a or not text_b:
            return 0.0
        stop = {"el","la","de","en","que","a","y","un","una","con","para","por"}
        sa = {w.lower() for w in text_a.split() if w.lower() not in stop}
        sb = {w.lower() for w in text_b.split() if w.lower() not in stop}
        if not sa or not sb:
            return 0.0
        return len(sa & sb) / len(sa | sb)
