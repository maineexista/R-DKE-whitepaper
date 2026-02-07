#!/usr/bin/env python3
"""
Experiment 1: Truth Veins vs Noise

A tiny toy model of R-DKE's "truth graph" plus Physarum-style reinforcement.

- We track a handful of claims.
- Each claim has SUPPORT and CONFLICT "evidence" counters.
- At each timestep:
    - We identify high-uncertainty claims (where support ≈ conflict).
    - Those uncertain claims get MORE simulated evidence updates
      (uncertainty acts like nutrient / attention).
    - We update a "confidence" value for each claim.
    - We apply a small decay so unused / unstable paths fade over time.

Run:
    python experiments/truth_veins_vs_noise.py
"""

import random
import time
from typing import Dict, Tuple

ClaimState = Dict[str, Dict[str, float]]


def init_claims() -> ClaimState:
    """
    Initialise a small set of claims with neutral evidence.

    In a real R-DKE system these would be semantic atoms, here they are just labels.
    """
    return {
        "A: Exercise improves mood": {"support": 2.0, "conflict": 1.0, "confidence": 0.0},
        "B: Coffee is always unhealthy": {"support": 1.0, "conflict": 2.0, "confidence": 0.0},
        "C: AI will replace all jobs": {"support": 1.5, "conflict": 1.5, "confidence": 0.0},
        "D: Reading before bed helps sleep": {"support": 2.0, "conflict": 0.5, "confidence": 0.0},
        "E: Drinking water causes dehydration": {"support": 0.5, "conflict": 2.0, "confidence": 0.0},
    }


def uncertainty(support: float, conflict: float) -> float:
    """
    Very simple uncertainty measure:
        - High when support ≈ conflict.
        - Low when one side clearly dominates.
    """
    total = support + conflict + 1e-6
    balance = abs(support - conflict) / total  # 0 = perfectly balanced, 1 = totally one-sided
    return 1.0 - balance  # 1 = very uncertain, 0 = very certain


def update_confidence(support: float, conflict: float) -> float:
    """
    Confidence ~ (support - conflict), squashed into [0, 1].

    0   = strong conflict (probably false)
    0.5 = ambiguous
    1   = strong support (probably true)
    """
    score = support - conflict  # can be negative
    # squash into [0, 1] with a simple tanh-like mapping
    # but avoid importing math/tanh to keep things readable:
    # assume score in [-10, 10]
    norm = max(-10.0, min(10.0, score)) / 10.0
    return 0.5 + 0.5 * norm


def ascii_bar(value: float, width: int = 20) -> str:
    """Draw a simple bar from 0–1."""
    value = max(0.0, min(1.0, value))
    filled = int(round(value * width))
    return "#" * filled + "-" * (width - filled)


def print_state(step: int, claims: ClaimState) -> None:
    print(f"\n=== STEP {step} ===")
    print("Claim".ljust(40), "Conf.", "Uncert.", "Support", "Conflict", "Truth Vein")
    print("-" * 90)
    for claim, state in claims.items():
        s = state["support"]
        c = state["conflict"]
        conf = state["confidence"]
        unc = uncertainty(s, c)
        bar = ascii_bar(conf)
        print(
            claim.ljust(40),
            f"{conf:5.2f}",
            f"{unc:7.2f}",
            f"{s:7.2f}",
            f"{c:8.2f}",
            bar,
        )


def step(claims: ClaimState, base_updates: int = 2, extra_for_uncertainty: int = 3) -> None:
    """
    One simulation step:

    - Compute uncertainty for each claim.
    - Claims with higher uncertainty receive more "evidence events".
    - Evidence events randomly add to support or conflict.
    - Apply small decay to both support and conflict.
    - Recompute confidence.
    """
    # 1. Compute uncertainties and pick "nutrient hotspots"
    uncertainties: Dict[str, float] = {}
    for name, state in claims.items():
        uncertainties[name] = uncertainty(state["support"], state["conflict"])

    # Normalise uncertainties into weights for extra updates
    total_unc = sum(uncertainties.values()) + 1e-6
    weights = {k: v / total_unc for k, v in uncertainties.items()}

    # 2. Apply evidence events
    for name, state in claims.items():
        # base number of evidence events for everyone
        updates = base_updates

        # plus extra proportional to uncertainty
        updates += int(round(extra_for_uncertainty * weights[name]))

        for _ in range(updates):
            # Evidence can support or conflict; we bias mildly toward the "true" claims.
            if "always unhealthy" in name or "replace all jobs" in name or "dehydration" in name:
                # more likely to see conflicting evidence against these
                if random.random() < 0.7:
                    state["conflict"] += random.uniform(0.2, 0.6)
                else:
                    state["support"] += random.uniform(0.1, 0.3)
            else:
                # more likely to see supporting evidence for these
                if random.random() < 0.7:
                    state["support"] += random.uniform(0.2, 0.6)
                else:
                    state["conflict"] += random.uniform(0.1, 0.3)

    # 3. Apply decay (old evidence slowly fades)
    for state in claims.values():
        state["support"] *= 0.98
        state["conflict"] *= 0.98

    # 4. Recompute confidence
    for state in claims.values():
        state["confidence"] = update_confidence(state["support"], state["conflict"])


def main():
    print(
        """
Experiment 1: Truth Veins vs Noise
----------------------------------

This is a tiny toy model of an R-DKE "truth graph".

- Each row is a claim.
- SUPPORT and CONFLICT are like accumulated evidence.
- CONF. (confidence) is how strongly the system leans true vs false.
- UNCERT. is high when support ≈ conflict (ambiguous claims).

Key idea:
    Uncertainty acts like nutrient.
    Claims that are ambiguous attract MORE evidence updates.
    Over time, stable "veins of truth" emerge.

Press Enter to advance a step, or 'q' then Enter to quit.
"""
    )
    claims = init_claims()
    for step_idx in range(1, 31):
        step(claims)
        print_state(step_idx, claims)
        user = input("Continue? [Enter = next, q = quit] ")
        if user.strip().lower() == "q":
            break


if __name__ == "__main__":
    main()
