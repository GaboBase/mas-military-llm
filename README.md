# mas-military-llm

> **Analogia Sistema Multi-Agente LLM x Doctrina Militar C2**
> Ecosistema Gabriel: PrompTitecture + Backlog Builder + ERP on Demand

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://github.com/langchain-ai/langgraph)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.80+-purple.svg)](https://crewai.com)

---

## Concepto Central

```
CC-DC-DE: Centralized Command - Distributed Control - Decentralized Execution
          Meta-Agente        - Supervisores          - Workers Especializados
          PrompTitecture     - Backlog Builder        - ERP on Demand
```

Este repositorio implementa la analogia completa entre la doctrina militar de
Command & Control (C2) y los sistemas Multi-Agente LLM (MAS), desarrollada
como arquitectura del ecosistema Gabriel.

---

## Jerarquia Militar x Agentes LLM

| Unidad Militar | Liderazgo | Equivalente LLM | Funcion |
|---|---|---|---|
| Army Group | General 4 estrellas | Meta-Agente / God-Agent | Define objetivo; nunca ejecuta |
| Corps | Teniente General | Orchestrator Principal | Descompone misiones |
| Division | Mayor General | Supervisor Estrategico | Coordina dominios en paralelo |
| Brigade | Coronel | Supervisor de Dominio | Gestiona agentes especializados |
| Battalion | Teniente Coronel | Coordinator Agent | Traduce ordenes en tacticas |
| Company | Capitan | Module Supervisor | Supervisa grupos de workers |
| Platoon | Teniente | Task Supervisor | Asigna sub-tareas |
| Squad | Staff Sergeant | Agente Especializado | Ejecuta con herramientas |
| Team | Sergeant | Agente Atomico / Worker | Unidad minima de accion |

---

## Modulos del Repositorio

```
mas-military-llm/
README.md
docs/
  01_fundamento_doctrinal.md
  02_jerarquia_escalones.md
  03_canales_comunicacion.md
  04_documentos_mando_prompts.md
  05_ooda_ciclo_cognitivo.md
  06_bda_working_group.md
  07_sistema_atencion_pir_sir.md
  08_mapa_espacios_gabriel.md
  09_plan_pace_resiliencia.md
  10_sitrep_schema.md
src/
  langgraph_ecosystem.py
  bda_working_group.py
  attention_monitor.py
  sitrep_schema.py
  crewai_agents.py
schemas/
  sitrep.json
  bda_output.json
  pir_sir_tree.json
.github/workflows/
  ci_validate_schemas.yml
```

---

## Conceptos Clave (Analogia)

| Concepto Militar | Equivalente LLM |
|---|---|
| OODA Loop | Ciclo cognitivo del agente |
| Commander's Intent | Ancla fija de contexto |
| PIR / SIR | Arbol de atencion cerrado |
| AAR | Multi-Agent Reflexion (MAR) |
| BDA Working Group | Debate multi-agente evaluador |
| PDA / FDA / TSA | Evaluacion tripartita de outputs |
| Plan PACE | Resiliencia de 4 niveles |
| SITREP | Structured output estandarizado |
| Auftragstaktik | Anti-drift: QUE lograr, nunca COMO |
| Task Saturation | Agent Drift en LLM |

---

## Instalacion

```bash
git clone https://github.com/GaboBase/mas-military-llm
cd mas-military-llm
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Uso Rapido

```python
from src.langgraph_ecosystem import build_ecosystem_graph

graph = build_ecosystem_graph()
result = graph.invoke({
    "commander_intent": "Construir el ecosistema Gabriel autosuficiente",
    "active_doctrine": {"framework": "PrompTitecture", "version": "8.0"},
    "roe": ["Nunca ejecutar sin SITREP", "Escalar severity>=3 al humano"],
    "current_backlog": [],
    "artifacts": {},
    "sitreps": [],
    "bda_assessments": [],
    "debate_log": [],
    "escalations": []
})
```

---

## Espacios Conectados

- [PrompTitecture](https://www.perplexity.ai/spaces/promptitecture-WS0PmhJCS6GHiG_MKodetg) - Meta-Agente / Doctrina
- [Backlog Builder](https://www.perplexity.ai/spaces/backlog-builder-exWRv_0NQGimIoNES00iCw) - Supervisor Estrategico
- [ERP on Demand](https://www.perplexity.ai/spaces/erp-on-demand-6.tKS4z3Sy6.wb7BA3A6ZQ) - Division de Ejecucion
- [Notion DOCWEB](https://www.notion.so) - Cuadro Operativo Comun (COP)

---

## Regla del 20% (Anti-Drift)

> Ninguna subtarea puede consumir mas del 20% del contexto total.
> Cada SIR debe declarar a que PIR alimenta y que decision habilita.
> Si no puede hacer esa traza = DRIFT. Se interrumpe y se reinyecta el ancla.

---

## Estado del Sistema

- Version: 1.0.0
- Estado: OTTIMO
- Fecha: 2026-04-06
- Autor: Gabriel Joel (GaboBase)
- Proxima revision: BDA Working Group Sesion 2

---

*Generado: 2026-04-06 05:00 -04 | Coquimbo, CL | DOCWEB Workspace*
