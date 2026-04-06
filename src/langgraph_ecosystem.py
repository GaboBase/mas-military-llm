"""langgraph_ecosystem.py
Integracion LangGraph para MAS-Military - Grafo de Estado Operacional
Analogia: Red de comunicaciones tactica con nodos por escalon jerarquico
Ecosistema Gabriel: PrompTitecture + Backlog Builder + ERP on Demand
MAS-Military v1.0.0
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict
from dataclasses import dataclass
from enum import Enum


# ---------------------------------------------------------------------------
# Estado compartido del grafo (Shared Situational Awareness digital)
# Analogia: COP - Common Operational Picture en sala de operaciones
# ---------------------------------------------------------------------------

class OperationalState(TypedDict, total=False):
    """Estado global del grafo LangGraph.

    Analogia Militar: COP mantenido en sala de operaciones del batallon.
    Cada nodo del grafo = un escalon de la jerarquia militar.
    Los edges = canales de comunicacion PACE (Primary/Alternate/Contingency/Emergency).
    """
    # Identificadores de mision
    session_id: str
    mission_id: str
    commander_intent: str

    # PIR/SIR tree en ejecucion
    active_pirs: List[Dict[str, Any]]
    completed_sirs: List[str]
    pending_sirs: List[str]

    # SITREP acumulado
    sitreps: List[Dict[str, Any]]
    last_sitrep: Optional[Dict[str, Any]]

    # Atencion y deriva
    attention_score: float
    drift_detected: bool
    drift_reason: Optional[str]

    # BDA
    bda_triggered: bool
    bda_result: Optional[Dict[str, Any]]

    # Escalacion
    escalation_required: bool
    escalation_level: Optional[str]

    # Ecosistema Gabriel
    promptitecture_context: Optional[str]   # PrompTitecture prompt activo
    backlog_task_id: Optional[str]          # Backlog Builder task referenciada
    erp_module: Optional[str]              # ERP on Demand modulo activo

    # Control de flujo
    current_phase: str    # planning | executing | assessing | escalating
    iteration: int
    max_iterations: int
    messages: List[str]   # log de comunicaciones inter-agente


# ---------------------------------------------------------------------------
# Nodos del grafo (= Escalones de la jerarquia militar)
# ---------------------------------------------------------------------------

class NodeRole(str, Enum):
    META_AGENT   = "meta_agent"    # General / Comandante Supremo
    SUPERVISOR   = "supervisor"    # Oficial de Estado Mayor (S3)
    WORKER       = "worker"        # Soldado / Especialista
    BDA_GROUP    = "bda_group"     # G2 BDA Working Group
    ATTENTION    = "attention"     # S6 Comunicaciones / Monitor ANCLA


@dataclass
class NodeResult:
    """Resultado de la ejecucion de un nodo del grafo."""
    node_id: str
    role: NodeRole
    state_updates: Dict[str, Any]
    sitrep_fragment: Optional[Dict[str, Any]] = None
    should_escalate: bool = False
    next_node: Optional[str] = None


# ---------------------------------------------------------------------------
# Funciones de nodo (stubs listos para LangGraph @node decorators)
# ---------------------------------------------------------------------------

def meta_agent_node(state: OperationalState) -> Dict[str, Any]:
    """Nodo Meta-Agente - Comandante Supremo.

    Responsabilidades:
    - Interpretar commander_intent
    - Generar arbol PIR inicial
    - Recibir SITREPs consolidados
    - Tomar decision final sobre BDA
    - Activar escalacion si severity >= 3

    Analogia PrompTitecture: Este nodo consume el system prompt maestro
    generado por PrompTitecture para definir el marco de la mision.
    """
    updates: Dict[str, Any] = {
        "current_phase": "planning",
        "iteration": state.get("iteration", 0) + 1,
        "messages": state.get("messages", []) + ["[META_AGENT] Mision iniciada. Intent recibido."],
    }
    return updates


def supervisor_node(state: OperationalState) -> Dict[str, Any]:
    """Nodo Supervisor - Oficial de Estado Mayor (S3 Ops).

    Responsabilidades:
    - Descomponer PIRs en SIRs (sub-tareas)
    - Asignar SIRs a workers especializados
    - Consolidar SITREPs de workers
    - Detectar deriva con AttentionMonitor
    - Reportar SITREP al Meta-Agente

    Analogia Backlog Builder: Este nodo traduce PIRs en items de backlog
    trazables, equivalente a las epics/stories en Backlog Builder.
    """
    pending = state.get("pending_sirs", [])
    updates: Dict[str, Any] = {
        "current_phase": "executing",
        "messages": state.get("messages", []) + [
            f"[SUPERVISOR] Asignando {len(pending)} SIRs a workers."
        ],
    }
    return updates


def worker_node(state: OperationalState) -> Dict[str, Any]:
    """Nodo Worker - Soldado / Especialista en campo.

    Responsabilidades:
    - Ejecutar SIR asignada con herramientas disponibles
    - Emitir SITREP parcial al supervisor
    - Mantener attention_score > umbral
    - Solicitar BDA si tarea completada

    Analogia ERP on Demand: Los workers acceden a modulos ERP
    (inventario, logistica, RRHH) como herramientas de campo.
    """
    updates: Dict[str, Any] = {
        "current_phase": "executing",
        "messages": state.get("messages", []) + ["[WORKER] SIR ejecutada. SITREP emitido."],
    }
    return updates


def attention_monitor_node(state: OperationalState) -> Dict[str, Any]:
    """Nodo Monitor de Atencion - S6 Comunicaciones / ANCLA.

    Responsabilidades:
    - Evaluar attention_score del estado actual
    - Detectar drift semantico entre SIRs y PIR padre
    - Emitir alerta de deriva al Supervisor
    - Reanclar tareas derivadas al objetivo PIR original

    Analogia: Radio operator que verifica que los mensajes en campo
    siguen alineados con el objective del comandante.
    """
    score = state.get("attention_score", 1.0)
    drift = score < 0.6
    updates: Dict[str, Any] = {
        "drift_detected": drift,
        "drift_reason": "attention_score below threshold" if drift else None,
        "messages": state.get("messages", []) + [
            f"[ATTENTION] Score={score:.2f} drift={'YES' if drift else 'NO'}"
        ],
    }
    return updates


def bda_group_node(state: OperationalState) -> Dict[str, Any]:
    """Nodo BDA Working Group - G2 Post-Mission Analysis.

    Responsabilidades:
    - Recibir SITREPs de todos los workers
    - Ejecutar debate multi-agente (Analyst/Critic/Synthesizer)
    - Alcanzar consenso sobre veredicto de mision
    - Reportar BDA al Meta-Agente
    - Registrar lecciones aprendidas
    """
    updates: Dict[str, Any] = {
        "current_phase": "assessing",
        "bda_triggered": True,
        "messages": state.get("messages", []) + ["[BDA_GROUP] Debate iniciado."],
    }
    return updates


# ---------------------------------------------------------------------------
# Router condicional (= Doctrine-based decision at HQ)
# ---------------------------------------------------------------------------

def route_after_supervisor(state: OperationalState) -> str:
    """Enrutar segun estado post-supervisor.

    Analogia: Oficial de operaciones decide siguiente accion
    basado en el COP actualizado.
    """
    if state.get("escalation_required"):
        return "meta_agent"          # Escalar al comandante
    if state.get("bda_triggered"):
        return "bda_group"           # Iniciar BDA
    if state.get("drift_detected"):
        return "attention_monitor"   # Corregir deriva
    pending = state.get("pending_sirs", [])
    if pending:
        return "worker"              # Continuar ejecucion
    return "bda_group"              # Todas SIRs completadas -> BDA


# ---------------------------------------------------------------------------
# Construccion del grafo (pseudocodigo - requiere langgraph instalado)
# ---------------------------------------------------------------------------

def build_military_graph():
    """Construir grafo LangGraph con topologia de jerarquia militar.

    Estructura del grafo:
    meta_agent -> supervisor -> worker -> attention_monitor
                     ^               |
                     |               v
                  bda_group <--------+
                     |
                     v
                 meta_agent (reporte final)

    Para usar:
        pip install langgraph>=0.2
        from langgraph.graph import StateGraph, END
        graph = build_military_graph()
        result = graph.invoke({...initial_state...})
    """
    try:
        from langgraph.graph import StateGraph, END  # type: ignore
    except ImportError:
        raise ImportError(
            "LangGraph no instalado. Ejecutar: pip install langgraph>=0.2"
        )

    builder = StateGraph(OperationalState)

    # Agregar nodos (escalones)
    builder.add_node("meta_agent",        meta_agent_node)
    builder.add_node("supervisor",         supervisor_node)
    builder.add_node("worker",             worker_node)
    builder.add_node("attention_monitor",  attention_monitor_node)
    builder.add_node("bda_group",          bda_group_node)

    # Punto de entrada (Orden de Operaciones desde el Comandante)
    builder.set_entry_point("meta_agent")

    # Edges fijos (canales PACE primarios)
    builder.add_edge("meta_agent",       "supervisor")
    builder.add_edge("worker",           "attention_monitor")
    builder.add_edge("attention_monitor","supervisor")
    builder.add_edge("bda_group",        "meta_agent")

    # Edge condicional (decision en sala de operaciones)
    builder.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "worker":           "worker",
            "bda_group":        "bda_group",
            "attention_monitor":"attention_monitor",
            "meta_agent":       "meta_agent",
        }
    )

    # Condicion de fin: Meta-Agente recibe BDA y no hay escalacion
    builder.add_edge("meta_agent", END)

    return builder.compile()
