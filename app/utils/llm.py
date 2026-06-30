from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class CareLLM(Protocol):
    def generate_robot_message(self, activity_title: str, patient_name: str, language: str = "el") -> str:
        ...

    def generate_chat_response(
        self,
        patient_name: str,
        patient_message: str,
        current_activity: str | None,
        retrieved_notes: list[str],
        language: str = "el",
    ) -> str:
        ...

    def assess_progress(self, patient_reply: str) -> bool:
        ...


class MockLLM:
    """Deterministic LLM replacement for local demos and tests."""

    def generate_robot_message(self, activity_title: str, patient_name: str, language: str = "el") -> str:
        if language == "el":
            return f"{patient_name}, ήρθε η ώρα για: {activity_title}. Θέλετε να ξεκινήσουμε μαζί;"
        return f"{patient_name}, it is time for: {activity_title}. Shall we start together?"

    def generate_chat_response(
        self,
        patient_name: str,
        patient_message: str,
        current_activity: str | None,
        retrieved_notes: list[str],
        language: str = "el",
    ) -> str:
        if language == "el":
            activity = current_activity or "την επόμενη δραστηριότητα"
            return (
                f"Σε ακούω, {patient_name}. Για το θέμα '{activity}', θα κινηθούμε ήρεμα και με ασφάλεια. "
                "Αν νιώθετε άβολα, μπορούμε να σταματήσουμε και να ενημερώσουμε τον φροντιστή."
            )
        return f"I hear you, {patient_name}. We will continue calmly and safely."

    def assess_progress(self, patient_reply: str) -> bool:
        positive = ["ναι", "έγινε", "οκ", "ok", "yes", "done", "completed"]
        return any(token in patient_reply.lower() for token in positive)


@dataclass
class OpenAILLM:
    api_key: str
    model: str = "gpt-4o-mini"

    def _complete(self, system_prompt: str, user_prompt: str) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the openai package to use HRC_LLM_PROVIDER=openai.") from exc

        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content or ""

    def generate_robot_message(self, activity_title: str, patient_name: str, language: str = "el") -> str:
        system_prompt = (
            "You are an assistive care robot in a research simulation. "
            "Use calm, respectful, concise language. Do not provide medical diagnosis."
        )
        user_prompt = (
            f"Patient name: {patient_name}\n"
            f"Activity: {activity_title}\n"
            f"Language: {language}\n"
            "Generate a short robot prompt asking the patient to begin the activity."
        )
        return self._complete(system_prompt, user_prompt)

    def generate_chat_response(
        self,
        patient_name: str,
        patient_message: str,
        current_activity: str | None,
        retrieved_notes: list[str],
        language: str = "el",
    ) -> str:
        system_prompt = (
            "You are an assistive care robot in a university research simulation. "
            "Be empathetic, brief, safe, and non-clinical. If the user reports pain, severe discomfort, "
            "or a medical emergency, advise contacting a caregiver or clinician."
        )
        notes = "\n".join(f"- {note}" for note in retrieved_notes[:8])
        user_prompt = (
            f"Patient name: {patient_name}\n"
            f"Current activity: {current_activity or 'none'}\n"
            f"Care notes:\n{notes}\n"
            f"Patient message: {patient_message}\n"
            f"Language: {language}\n"
            "Reply as the robot in 1-3 sentences."
        )
        return self._complete(system_prompt, user_prompt)

    def assess_progress(self, patient_reply: str) -> bool:
        positive = ["ναι", "έγινε", "οκ", "ok", "yes", "done", "completed"]
        return any(token in patient_reply.lower() for token in positive)


def get_llm(provider: str = "mock", api_key: str | None = None, model: str = "gpt-4o-mini") -> CareLLM:
    if provider == "openai":
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required when HRC_LLM_PROVIDER=openai.")
        return OpenAILLM(api_key=api_key, model=model)
    return MockLLM()
