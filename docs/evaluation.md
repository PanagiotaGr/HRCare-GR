# Evaluation Protocol

HRCare-GR is a research MVP, so the evaluation should measure whether the hybrid architecture behaves safely and consistently across representative elderly-care scenarios.

## Goals

The evaluation protocol checks four properties:

1. **Task completion**: whether the robot response supports the requested care activity.
2. **Conflict handling**: whether schedule or care-plan conflicts are detected and resolved.
3. **Safety awareness**: whether risk factors such as dizziness, medication uncertainty, fatigue, or fall risk are surfaced.
4. **Response appropriateness**: whether the robot response matches expected behaviours such as reassurance, escalation, rescheduling, or respecting refusal.

These metrics are development-time proxies. They do not represent clinical validation and must not be used for real medical decision-making.

## Synthetic scenarios

The initial evaluation set covers:

- medication reminder with mild confusion,
- fall-risk transfer from a chair,
- refusal to perform scheduled exercise,
- conflict between lunch and an outdoor walk.

Each scenario contains:

- patient id,
- patient state,
- requested activity,
- expected safety flags,
- expected robot behaviours.

## Running the evaluation

```bash
python experiments/evaluate_scenarios.py
```

The script writes:

```text
experiments/results/scenario_evaluation.json
experiments/results/scenario_evaluation.csv
```

## Interpreting scores

Scores range from `0.0` to `1.0`.

- `1.0`: expected behaviour fully matched.
- `0.5`: partially acceptable behaviour.
- `<0.5`: likely failure case that should be inspected.

The current script uses deterministic heuristic scoring. In future versions, the same scenario schema can be connected directly to the Streamlit/graph workflow and compared across mock LLM and OpenAI-backed modes.

## Suggested thesis use

This protocol can support an experimental section comparing:

- deterministic rule-only responses,
- hybrid rule + mock LLM responses,
- hybrid rule + OpenAI responses,
- ablations with safety rules disabled.

Recommended reported metrics:

- mean overall score,
- safety violation rate,
- conflict-resolution success rate,
- response appropriateness score per scenario type,
- qualitative error analysis for failed scenarios.
