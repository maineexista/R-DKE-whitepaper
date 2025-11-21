# Living Question Explorer

A tiny, self-contained experiment that demonstrates another core idea behind **R-DKE**:

> **The system does not wait for your question.**  
> It actively seeks uncertainty and chooses the next question that will grow its understanding.  
> Knowledge expands like a living organism exploring nutrient-rich space.

This toy model simulates a miniature *knowledge map* of several topics.  
Each topic has an **uncertainty** score and a **knowledge** score that evolve as the engine “learns.”

---

## 🔍 What You’ll See

Every time you press **Enter**, the system:

1. Scans all topics and finds the **most uncertain region**  
   (uncertainty → nutrient).  
2. Selects an internal question it wants to explore next.  
3. Simulates learning, reducing uncertainty in that region.  
4. Updates the full **knowledge map**, showing how understanding spreads.  

You’ll watch the map gradually stabilise —  
uncertain regions being explored first, then reinforced over time.

It’s a simple, visual way to understand:  
**autonomous curiosity**, **uncertainty-driven exploration**,  
and **self-organising learning inspired by Physarum.**

---

## ▶️ Run It

```bash
python living_question_explorer.py
Keep pressing Enter to advance steps.
Press q to quit.
