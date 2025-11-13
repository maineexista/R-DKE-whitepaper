🧬 Physarum Knowledge Atoms — R-DKE v2.0 Mini Engine  
*A tiny biologically-inspired reasoning loop — where knowledge doesn’t compute… it grows.*

This experiment is a minimal, runnable demonstration of the **Physarum-Inspired Reasoning Loop** from **R-DKE v2.0**.  
It simulates how *uncertainty* can act as nutrient, how reasoning flows through a conceptual graph, and how truth stabilizes through reinforcement and decay — mirroring the behaviour of *Physarum polycephalum* (slime mold).

Rather than searching or retrieving, the system **grows its internal representation** of knowledge.

---

## 🌱 Concept Overview

This micro-engine demonstrates:

### 🔹 Knowledge Atoms  
Short conceptual sentences with deterministic embeddings.

### 🔹 Uncertainty → Nutrient  
Nodes with weak or contradictory neighbors generate “nutrient,” attracting flow.

### 🔹 Semantic Flow  
Edges with high semantic agreement conduct more flow.

### 🔹 Reinforce / Decay  
High-flow edges thicken; low-flow paths fade.  
A **truth graph** emerges.

### 🔹 Instant Answer (Toy)  
Queries are embedded and flow through the strengthened graph to produce an answer.

> **Goal:** Demonstrate *reasoning as growth*, not retrieval.  
> A pedagogical scaffold for R-DKE v2.0 research.

---

## ⚡ Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py --steps 120 --gif out.gif --export truth_graph.json
This generates:
out.gif — a visualization of the “knowledge organism” growing
truth_graph.json — the stabilized conceptual structure
🔍 Ask the Engine a Question
python run.py --query "How can uncertainty guide reasoning?" --topk 4
Example output:
Instant answer:
  • (0.746) Uncertainty can guide exploration
  • (0.621) Reasoning can be distributed
  • (0.542) Graph edges can carry meaning
  • (0.532) Memories can decay without reinforcement
Trace: Uncertainty can guide exploration → Noise supports exploration
Answers come from the grown graph, not a model.
🧠 How It Works (Internal Logic)
1. Embeddings
Each atom receives a deterministic vector (no ML model required).
2. Graph Construction
Nodes connect to their semantically nearest neighbors.
3. Uncertainty Measurement
Nodes with:
low semantic coherence
high neighbor disagreement
produce higher nutrient.
4. Flow Propagation
Flow prefers:
nutrient gradients
semantically aligned edges
5. Reinforcement Cycle
conductance += reinforce * flow - decay
Edges self-organize into truth routes.
6. Instant Reasoning
A query embedding moves through stabilized high-conductance pathways.
This creates a tiny but interpretable analog of the R-DKE v2.0 loop.

🧩 Try Modifying the Experiment
You can tweak:
• Add new atoms
Edit atoms.json.
• Change reinforcement/decay
Inside step() in run.py.
• Adjust graph density
In build_graph() → k=6.
• Alter uncertainty sensitivity
Inside node_uncertainty().
• Switch layout algorithm
Change nx.spring_layout to any NetworkX layout.
This experiment invites exploration, experimentation, and conceptual extension.

📁 Repository Structure
/02_physarum_knowledge_atoms
  ├── atoms.json
  ├── run.py
  ├── requirements.txt
  ├── README.md
  └── LICENSE
Generated files like out.gif and truth_graph.json should not be committed.
🔗 Related Work
Full R-DKE v2.0 whitepaper:
https://github.com/maineexista/R-DKE-whitepaper
⚖️ License
This project is released under the MIT License, allowing others to freely use, modify, and build upon the work while protecting the author from liability.
See: LICENSE file.
