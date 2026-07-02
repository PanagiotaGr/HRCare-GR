# HRCare-GR

**Hybrid LLM Architecture for Assistive Human-Robot Collaboration in Greek Elderly Care**

HRCare-GR is a research-oriented Python MVP inspired by hybrid LLM architectures for human-robot collaboration, but implemented as an original project with a Greek elderly-care scenario, modular graph workflow, deterministic care rules, Streamlit interface, and optional LLM support.

## What it does

The system simulates an assistive robot that supports an older adult during a daily care routine. It combines:

- patient profile retrieval,
- task generation,
- deterministic scheduling rules,
- situation assessment,
- robot response generation,
- progress checking,
- structured session logging,
- optional OpenAI-powered dialogue.

The application can run without an API key by using the deterministic mock LLM. For more realistic dialogue, set `HRC_LLM_PROVIDER=openai` and provide `OPENAI_API_KEY` in `.env`.

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
Robot response / chat response
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
│   ├── streamlit_app.py
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
├── docs/
│   └── evaluation.md
├── experiments/
│   └── evaluate_scenarios.py
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
```

Run the CLI simulation:

```bash
python -m app.main
```

Run the Streamlit application:

```bash
streamlit run app/streamlit_app.py
```

## Evaluation

Run the synthetic scenario evaluation:

```bash
python experiments/evaluate_scenarios.py
```

The evaluation script writes JSON and CSV outputs to:

```text
experiments/results/
```

See `docs/evaluation.md` for the protocol, metrics, and suggested thesis use.

## OpenAI mode

Edit `.env`:

```bash
HRC_LLM_PROVIDER=openai
HRC_LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_api_key_here
```

Then run:

```bash
streamlit run app/streamlit_app.py
```

If the provider is `mock`, no API key is required.

## Example patient IDs

- `P001`: Μαρία Παπαδοπούλου
- `P002`: Νίκος Αντωνίου

## Current MVP features

- Streamlit web interface
- patient profile panel
- daily care-plan generation
- deterministic conflict resolution
- safety warnings
- robot interaction panel
- task completion metrics
- session logging
- mock/OpenAI LLM provider abstraction
- synthetic scenario evaluation

## Research angle

Possible university title:

> A Hybrid LLM and Rule-Based Architecture for Personalized Human-Robot Collaboration in Elderly Care Environments

Possible evaluation metrics:

- task completion rate,
- schedule conflict rate,
- response appropriateness,
- patient-state consistency,
- number of safety rule violations,
- average interaction turns per activity.

## Safety note

This is a simulation and research prototype. It must not be used for real medical decision-making.
