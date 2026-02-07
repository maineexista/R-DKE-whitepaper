#!/usr/bin/env python3
"""
Experiment 2: Living Question Explorer

A toy model of R-DKE's "autonomous curiosity loop":

- We have a tiny map of topics (nodes) with an uncertainty score.
- At each step, the engine:
    1. Picks the most uncertain topic (uncertainty as nutrient).
    2. "Asks" a question there (printed to the terminal).
    3. Simulates learning something and reduces uncertainty.
- Over time, the map stabilises: some areas become well understood; others remain fuzzy.

Run:
    python experiments/living_question_explorer.py
"""

import random
from typing import Dict, List


class Topic:
    def __init__(self, name: str, questions: List[str], initial_uncertainty: float):
        self.name = name
        self.questions = questions
        self.uncertainty = initial_uncertainty  # 0 = fully known, 1 = very unknown
        self.knowledge = 1.0 - initial_uncertainty  # inverse

    def reinforce(self):
        """Simulate learning: uncertainty drops, knowledge rises."""
        delta = random.uniform(0.05, 0.15)
        self.uncertainty = max(0.0, self.uncertainty - delta)
        self.knowledge = min(1.0, 1.0 - self.uncertainty)

    def pick_question(self) -> str:
        return random.choice(self.questions)


def init_topics() -> Dict[str, Topic]:
    return {
        "AI Alignment": Topic(
            "AI Alignment",
            [
                "How do we align powerful AI systems with human values?",
                "What happens if objectives are slightly misspecified?",
                "How can we detect when an AI is gaming its reward?",
            ],
            initial_uncertainty=0.75,
        ),
        "Climate Models": Topic(
            "Climate Models",
            [
                "How do short-term predictions differ from long-term ones?",
                "Where are the largest sources of uncertainty in forecasts?",
                "How does new data tighten or relax our predictions?",
            ],
            initial_uncertainty=0.6,
        ),
        "Nutrition Science": Topic(
            "Nutrition Science",
            [
                "Why do different studies say different things about the same food?",
                "How do we separate correlation from causation in diet studies?",
                "What counts as strong evidence in nutrition?",
            ],
            initial_uncertainty=0.7,
        ),
        "History of Ideas": Topic(
            "History of Ideas",
            [
                "Which old philosophical debates are still unresolved?",
                "How do ideas mutate as they move through cultures?",
                "Which 'settled' ideas later turned out to be wrong?",
            ],
            initial_uncertainty=0.5,
        ),
    }


def ascii_bar(value: float, width: int = 20) -> str:
    value = max(0.0, min(1.0, value))
    filled = int(round(value * width))
    return "#" * filled + "-" * (width - filled)


def print_map(step_idx: int, topics: Dict[str, Topic]):
    print(f"\n=== STEP {step_idx} — Current Knowledge Map ===")
    print("Topic".ljust(25), "Knowledge", "Uncertainty", "Vein")
    print("-" * 70)
    for name, topic in topics.items():
        print(
            name.ljust(25),
            f"{topic.knowledge:8.2f}",
            f"{topic.uncertainty:10.2f}",
            ascii_bar(topic.knowledge),
        )


def pick_most_uncertain(topics: Dict[str, Topic]) -> Topic:
    # Choose the topic with max uncertainty; break ties randomly.
    max_unc = max(t.uncertainty for t in topics.values())
    candidates = [t for t in topics.values() if abs(t.uncertainty - max_unc) < 1e-6]
    return random.choice(candidates)


def main():
    print(
        """
Experiment 2: Living Question Explorer
--------------------------------------

This experiment shows a toy version of an R-DKE curiosity loop.

- The engine holds a tiny map of topics (AI, climate, nutrition, etc.).
- Each topic has an UNCERTAINTY score and a KNOWLEDGE score.
- At each step:
    1) The engine finds the most uncertain topic.
    2) It prints a "next question" it would pursue there.
    3) It simulates learning something, reducing that uncertainty.

Key idea:
    The system isn't waiting for your question.
    It is *actively seeking* the most uncertain region to explore next.

Press Enter to let the system take the next curiosity step, or 'q' to quit.
"""
    )

    topics = init_topics()

    for step_idx in range(1, 31):
        print_map(step_idx, topics)
        # Pick target
        target = pick_most_uncertain(topics)
        q = target.pick_question()

        print("\nMost uncertain region:", target.name)
        print("Engine's next question:")
        print(f'  → "{q}"')

        # Simulate learning
        target.reinforce()

        user = input("\nContinue? [Enter = next, q = quit] ")
        if user.strip().lower() == "q":
            break


if __name__ == "__main__":
    main()
