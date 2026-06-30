from __future__ import annotations


class MockLLM:
    """Deterministic LLM replacement for local demos and tests."""

    def generate_robot_message(self, activity_title: str, patient_name: str, language: str = "el") -> str:
        if language == "el":
            return f"{patient_name}, ήρθε η ώρα για: {activity_title}. Θέλετε να ξεκινήσουμε μαζί;"
        return f"{patient_name}, it is time for: {activity_title}. Shall we start together?"

    def assess_progress(self, patient_reply: str) -> bool:
        positive = ["ναι", "έγινε", "οκ", "ok", "yes", "done", "completed"]
        return any(token in patient_reply.lower() for token in positive)


def get_llm(provider: str = "mock") -> MockLLM:
    if provider != "mock":
        raise NotImplementedError("Only the mock provider is implemented in the MVP.")
    return MockLLM()
