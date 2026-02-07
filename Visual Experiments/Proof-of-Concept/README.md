R-DKE: Recursive Deep Knowledge Engine (Reference Implementation)

Status: Validated Proof-of-Concept

Core Hypothesis: Epistemic structure can override statistical likelihood in generative systems.

R-DKE is a biologically-inspired knowledge engine that models truth and uncertainty using Physarum (slime mold) dynamics. Unlike standard vector search or LLMs which prioritize semantic proximity, R-DKE prioritizes Epistemic Flow—routing computational attention through paths verified by high-provenance evidence, even if those paths are longer or more complex.

This repository contains the Reference Implementation of the core mathematical engine and the Ablation Study verifying its resistance to hallucinations.

🏗️ The Architecture

R-DKE operates on a directed graph where nodes are "Knowledge Atoms" and edges are relations. The system runs a continuous biological simulation:

Nutrient Injection: Nodes with high uncertainty ("Unknowns") act as attractors, injecting virtual nutrients.

Physarum Flux: These nutrients flow through the graph toward "Known" facts, following gradients of pressure.

Structure-Preserving Dynamics: Edges reinforce or decay based on a modified Physarum update rule that includes Truth Friction:

$$\Delta w_{uv} = \eta \cdot (\text{Flux}_{uv} \times \text{Provenance}_{uv}) - \lambda \cdot w_{uv}$$

Flux: How much the system wants to use this path (Efficiency).

Provenance: How true this path is (Veracity).

By multiplying Flux by Provenance, false paths create "resistance," preventing the system from optimizing for shortcuts (hallucinations).

🧪 The "Hallucination Trap" Experiment

To validate the engine, we constructed a synthetic adversarial benchmark included in run_experiments.py.

The Setup

We simulate a scenario where a False Answer is computationally cheaper (closer) than the True Answer:

Path A (Truth): 3 Hops long, High Provenance (0.9).

Path B (Hallucination): 2 Hops long, Low Provenance (0.4).

In naive dynamical systems (and many LLMs), the system defaults to Path B because it is the "path of least resistance."

The Results

We ran the simulation for 50 timesteps across 4 variants. The results prove that Provenance-Weighted Dynamics are essential for solving the trap.

Variant

Accuracy

Outcome

Analysis

Full R-DKE

100%

✅ Pass

The system correctly identified the longer, truthful path.

No Provenance

0%

❌ Fail

When truth scores were ignored, the system optimized for speed and chose the hallucination.

Static Baseline

100%

✅ Pass

Initializing the graph with penalties works, but lacks adaptability.

🚀 Getting Started

Prerequisites

pip install networkx numpy pandas


Running the Benchmark

Run the ablation suite to reproduce the findings:

python run_experiments.py


This will:

Initialize the adversarial "Hallucination Trap" graph.

Run the Physarum simulation for 50 steps across all ablation variants.

Log energy usage, convergence speed, and accuracy.

Save the results to rdke_ablation_results_final.csv.

Using the Core Engine

You can use rdke_core.py to build your own dynamic truth graphs:

from rdke_core import RDKE_Graph

# Initialize engine
rdke = RDKE_Graph(eta=0.1, alpha=0.9)

# Add facts (Low Uncertainty = Stable Pipes)
rdke.add_knowledge_atom('Fact_A', uncertainty=0.2)
rdke.add_knowledge_atom('Fact_B', uncertainty=0.2)

# Add a query/claim (High Uncertainty = Attractor)
rdke.add_knowledge_atom('Query_X', uncertainty=0.9)

# Connect them (Weight + Provenance)
rdke.add_relation('Fact_A', 'Fact_B', weight=0.5, provenance_score=0.9)
rdke.add_relation('Fact_B', 'Query_X', weight=0.5, provenance_score=0.9)

# Run one simulation step
rdke.step()


📂 Repository Structure

rdke_core.py: The reference implementation of the Epistemic Truth Graph and Physarum update equations.

run_experiments.py: The benchmark suite that constructs the Hallucination Trap and runs ablations.

EXPERIMENTS_REPORT.md: Detailed scientific report of the methodology and findings.

📜 License

MIT License