# Truth Veins vs Noise

A tiny, self-contained experiment that demonstrates one of the core ideas behind **R-DKE**:

> **Uncertainty acts like nutrient.**  
> Claims that are ambiguous attract more “attention” and therefore gather more evidence.  
> Stable truths naturally strengthen over time, while noisy or contradictory paths fade.

This toy model simulates a miniature *truth graph* of several claims.  
Each claim collects **support** and **conflict** evidence as a simple update rule reinforces (or dissolves) its “truth vein.”

---

## 🔍 What You’ll See

Every time you press **Enter**, the system:

1. Identifies which claims are **most uncertain** (where support ≈ conflict).  
2. Sends **more evidence events** their way (uncertainty → nutrient).  
3. Updates each claim’s **confidence** value.  
4. Applies a small **decay**, causing inactive or unstable paths to fade.  

You’ll watch some claims grow strong, stable “truth veins,”  
while others collapse under conflicting evidence.

It’s a simple, visual way to understand:  
**truth reinforcement**, **self-stabilising knowledge**,  
and **physarum-inspired reasoning.**

---

## ▶️ Run It

```bash
python truth_veins_vs_noise.py
Keep pressing Enter to advance steps.
Press q to quit.