# HRCare-GR

**Hybrid LLM Architecture for Assistive Human-Robot Collaboration in Greek Elderly Care**

HRCare-GR is a research-oriented Python MVP inspired by hybrid LLM architectures for human-robot collaboration, but implemented as an original project with a Greek elderly-care scenario, modular graph workflow, deterministic care rules, and simulation-first design.

## What it does

The system simulates an assistive robot that supports an older adult during a daily care routine. It combines:

- patient profile retrieval,
- task generation,
- deterministic scheduling rules,
- situation assessment,
- robot response generation,
- progress checking,
- structured session logging.

The first version runs fully from the command line and can work without an API key by using a deterministic mock LLM.

## Architecture

```text
Patient profile + care notes
        ↓
Knowledge retrieval
        ↓
Daily task generation
        ↓
Rule-based planner
        ↓
Situation assessment
        ↓
Robot response
        ↓
Progress checking
        ↓
Session logs / evaluation
```

## Project structure

```text
hrcare-gr/
├── app/
│   ├── main.py
│   ├── graph/
│   │   ├── state.py
│   │   └── workflow.py
│   ├── nodes/
│   │   ├── knowledge_retriever.py
│   │   ├── task_generator.py
│   │   ├── situation_assessor.py
│   │   ├── planner.py
│   │   ├── progress_checker.py
│   │   └── robot_response.py
│   ├── rules/
│   │   └── activity_rules.py
│   ├── data/
│   │   ├── patients/
│   │   └── care_guidelines/
│   └── utils/
│       ├── config.py
│       ├── llm.py
│       └── logging.py
├── experiments/
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main
```

## Example patient IDs

- `P001`: Maria Papadopoulou
- `P002`: Nikos Antoniou

## Research angle



Possible evaluation metrics:

- task completion rate,
- schedule conflict rate,
- response appropriateness,
- patient-state consistency,
- number of safety rule violations,
- average interaction turns per activity.

## Safety note

This is a simulation and research prototype. It must not be used for real medical decision-making.
