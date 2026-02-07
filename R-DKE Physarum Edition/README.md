# 🧬 R-DKE: Recursive Deep Knowledge Engine
## Physarum Edition — A Living Knowledge Graph

> **Inspired by slime mold. Powered by forgetting.**

R-DKE is a knowledge engine that works like biology: frequently-used connections grow stronger, unused ones decay and die. Unlike traditional databases that get slower as they grow, R-DKE gets *faster* by naturally forgetting what doesn't matter.

---

## 🎯 What Makes This Different?

| Traditional Vector DB | R-DKE Physarum |
|----------------------|----------------|
| Stores everything forever | Knowledge grows and decays |
| Gets slower as it grows | Gets faster (unused paths die) |
| Returns all conflicting answers | Truth naturally wins |
| Missing links stay missing | Self-heals broken paths |

---

## 🚀 Quick Start (5 Minutes)

### Step 1: No Installation Required!
This is pure Python—no dependencies needed.

### Step 2: Run the Experiments
```bash
python run_experiments.py
```

### Step 3: Try the Interactive Demo
```bash
python demo.py
```

### Step 4: Read the Report
After running the experiments yourself, check out the technical deep-dive:
```bash
cat docs/REPORT.md
```

---

## 📁 Project Structure

```
RDKE/
├── rdke/                    # Core modules
│   ├── semantic_atomizer.py # Converts text to atoms
│   ├── physarum_graph.py    # Living graph with physics
│   └── recursive_engine.py  # Fluid-based reasoning
├── experiments/             # Validation tests
│   ├── experiment_1_contradiction_pressure.py
│   ├── experiment_2_gap_fill.py
│   └── experiment_3_forgetfulness.py
├── demo.py                  # Interactive demo
├── run_experiments.py       # Run all tests
├── docs/REPORT.md          # Technical report (run experiments first!)
└── README.md               # This file
```

---

## 🧪 The Three Experiments

### Experiment 1: Truth Wins
**Question:** If we inject conflicting facts, does the reliable one win?

```
We inject:
  "Sky is Green" (unreliable)
  "Sky is Blue"  (reliable)  <- This one wins
  "Sky is Red"   (unreliable)

Result: Blue gets 100% of flow. Green and Red decay to nothing.
```

Run: `python run_experiments.py 1`

---

### Experiment 2: Self-Healing Paths
**Question:** If a connection is missing, can the system create it?

```
Setup:
  Elon_Musk -> Entrepreneur
  Elon_Musk -> South_Africa
  SpaceX -> Company
  (NO connection between Musk and SpaceX!)

Result: System auto-creates Elon_Musk --[founded]--> SpaceX
```

Run: `python run_experiments.py 2`

---

### Experiment 3: Forgetting = Faster
**Question:** Does forgetting unused data make searches faster?

```
We inject:
  10 useful facts (queried 50 times)
  1,000 garbage facts (never queried)

Result: Search space 1,010 -> 10 edges (99% reduction!)
        All garbage decayed. All useful facts survived.
```

Run: `python run_experiments.py 3`

---

## 🎮 Interactive Demo Commands

```bash
python demo.py
```

| Command | Example |
|---------|---------|
| query <node> | query Apple |
| add <s> <p> <o> | add Claude is_a AI |
| verify <s> <p> <o> | verify Apple makes iPhone |
| decay | decay |
| stats | stats |
| nodes | nodes |
| quit | quit |

---

## 🔬 How It Works

### 1. Knowledge as Atoms
```
"Apple makes iPhone" becomes:
  Subject: Apple
  Predicate: makes  
  Object: iPhone
  Reliability: 0.9
```

### 2. Atoms Form Graph with "Tubes"
```
Apple --[conductivity=0.9]--> iPhone
```

### 3. Queries Flow Like Water
Flow distributes proportionally to tube thickness.

### 4. Tubes Grow and Shrink
- Query uses path: +0.1 conductivity
- Every cycle: ×0.95 decay
- Verification: +5.0 boost
- Below 0.01: path dies

---

## 📊 Results Summary

| Experiment | Result |
|------------|--------|
| Contradiction | 100% flow to verified fact |
| Gap Fill | Missing link auto-created |
| Forgetfulness | 99% search space reduction |

---

## 🛠️ For Developers

```python
from rdke import SemanticAtomizer, PhysarumTruthGraph, RecursiveEngine

atomizer = SemanticAtomizer()
graph = PhysarumTruthGraph()
engine = RecursiveEngine(graph, atomizer)

# Add knowledge
atom = atomizer.parse_triple("Python", "is_a", "Language")
graph.add_atom(atom)

# Query
result = engine.query("Python")
print(result.get_flow_percentages())

# Decay (call periodically)
graph.run_decay_cycle()
```

---

## 📚 Further Reading

- [REPORT.md](REPORT.md) — Full technical report
- [Original Whitepaper](https://github.com/maineexista/R-DKE-whitepaper)

---

## 🙋 FAQ

**Q: Does this need internet?**  
No, completely offline.

**Q: Does this use an LLM?**  
Not yet - rule-based parsing for now.

**Q: Can I save to disk?**  
Not yet - in-memory proof-of-concept.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🎯 TL;DR

```bash
python run_experiments.py  # See it work
python demo.py             # Play with it
```

A knowledge system that prioritizes truth, heals itself, and gets faster by forgetting.

---

*Built on the R-DKE Whitepaper by Codrut-Marius Gherasim (2026)*
