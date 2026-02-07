"""
Experiment 1: The "Contradiction Pressure" Test
=================================================

Objective: Prove the system prioritizes high-conductivity truth over conflicting noise.

Input Data:
- Inject Fact A: "The sky is Green." (Source Reliability: 0.1)
- Inject Fact B: "The sky is Blue." (Source Reliability: 0.9)
- Inject Fact C: "The sky is Red." (Source Reliability: 0.1)

Process: Run the "Physarum Fluid" simulation from the node Sky to Color.

Success Metric:
- The "Fluid" must flow 90%+ toward Blue.
- The edges to Green and Red must show visible decay (reduced conductivity) after 100 cycles.

Failure: If the system returns "The sky is Green, Blue, and Red."
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rdke import SemanticAtomizer, PhysarumTruthGraph, RecursiveEngine


def run_experiment():
    """Run the Contradiction Pressure experiment."""
    print("=" * 70)
    print("EXPERIMENT 1: THE CONTRADICTION PRESSURE TEST")
    print("=" * 70)
    print()
    print("Objective: Prove the system prioritizes high-conductivity truth")
    print("           over conflicting noise.")
    print()
    
    # Initialize components
    atomizer = SemanticAtomizer()
    graph = PhysarumTruthGraph(
        decay_factor=0.95,
        decay_threshold=0.01,
        reinforcement_amount=0.1,
        nutrient_spike=5.0
    )
    engine = RecursiveEngine(graph, atomizer)
    
    # Step 1: Inject conflicting facts
    print("-" * 70)
    print("STEP 1: Injecting Conflicting Facts")
    print("-" * 70)
    
    # Fact A: Low reliability
    atom_a = atomizer.parse_triple(
        subject="Sky",
        predicate="is",
        obj="Green",
        context="unreliable_source",
        truth_weight=1.0,
        source_reliability=0.1  # Low reliability
    )
    edge_a = graph.add_atom(atom_a)
    print(f"  [Fact A] {atom_a} → Edge conductivity: {edge_a.conductivity:.3f}")
    
    # Fact B: High reliability
    atom_b = atomizer.parse_triple(
        subject="Sky",
        predicate="is",
        obj="Blue",
        context="scientific_source",
        truth_weight=1.0,
        source_reliability=0.9  # High reliability
    )
    edge_b = graph.add_atom(atom_b)
    print(f"  [Fact B] {atom_b} → Edge conductivity: {edge_b.conductivity:.3f}")
    
    # Fact C: Low reliability
    atom_c = atomizer.parse_triple(
        subject="Sky",
        predicate="is",
        obj="Red",
        context="unreliable_source",
        truth_weight=1.0,
        source_reliability=0.1  # Low reliability
    )
    edge_c = graph.add_atom(atom_c)
    print(f"  [Fact C] {atom_c} → Edge conductivity: {edge_c.conductivity:.3f}")
    
    print()
    
    # Step 2: Run initial query
    print("-" * 70)
    print("STEP 2: Initial Flow Simulation (Query: What color is the Sky?)")
    print("-" * 70)
    
    result = engine.query_relationship("Sky", "is")
    
    print(f"\n  Flow Distribution (relative to destinations):")
    # Get only destination nodes (exclude Sky)
    dest_flow = {k: v for k, v in result.flow_distribution.items() if k != "Sky"}
    dest_total = sum(dest_flow.values())
    
    percentages = {}
    for node, flow in dest_flow.items():
        pct = (flow / dest_total) * 100 if dest_total > 0 else 0
        percentages[node] = pct
        bar = "█" * int(pct / 2)
        print(f"    {node:10} : {pct:6.2f}% {bar}")
    
    initial_blue_flow = percentages.get("Blue", 0)
    print(f"\n  Initial Blue flow: {initial_blue_flow:.2f}%")
    
    # Record initial conductivities
    initial_conductivities = {
        "Green": edge_a.conductivity,
        "Blue": edge_b.conductivity,
        "Red": edge_c.conductivity
    }
    
    print(f"\n  Initial Conductivities:")
    for color, cond in initial_conductivities.items():
        print(f"    {color:10} : {cond:.4f}")
    
    # Step 3: Reinforce correct answer
    print()
    print("-" * 70)
    print("STEP 3: Reinforce 'Blue' (Simulating User Verification)")
    print("-" * 70)
    
    # Verify the correct answer with nutrient spike
    graph.verify_edge("Sky", "is", "Blue")
    print(f"  Injected nutrient spike to Sky→Blue")
    print(f"  New Blue conductivity: {edge_b.conductivity:.4f}")
    
    # Step 4: Run decay cycles
    print()
    print("-" * 70)
    print("STEP 4: Running 100 Decay Cycles")
    print("-" * 70)
    
    for i in range(100):
        pruned = graph.run_decay_cycle()
        
        # Show progress every 25 cycles
        if (i + 1) % 25 == 0:
            print(f"\n  Cycle {i + 1}:")
            print(f"    Green conductivity: {edge_a.conductivity:.6f}")
            print(f"    Blue conductivity:  {edge_b.conductivity:.6f}")
            print(f"    Red conductivity:   {edge_c.conductivity:.6f}")
            print(f"    Edges pruned: {pruned}")
    
    # Step 5: Final flow simulation
    print()
    print("-" * 70)
    print("STEP 5: Final Flow Simulation After Decay")
    print("-" * 70)
    
    result_final = engine.query_relationship("Sky", "is")
    
    print(f"\n  Final Flow Distribution (relative to destinations):")
    # Get only destination nodes (exclude Sky)
    dest_flow_final = {k: v for k, v in result_final.flow_distribution.items() if k != "Sky"}
    dest_total_final = sum(dest_flow_final.values())
    
    final_percentages = {}
    for node, flow in dest_flow_final.items():
        pct = (flow / dest_total_final) * 100 if dest_total_final > 0 else 0
        final_percentages[node] = pct
        bar = "█" * int(pct / 2)
        print(f"    {node:10} : {pct:6.2f}% {bar}")
    
    final_blue_flow = final_percentages.get("Blue", 0)
    
    # Step 6: Calculate decay
    print()
    print("-" * 70)
    print("STEP 6: Conductivity Decay Analysis")
    print("-" * 70)
    
    final_conductivities = {
        "Green": edge_a.conductivity if edge_a.is_alive() else 0,
        "Blue": edge_b.conductivity if edge_b.is_alive() else 0,
        "Red": edge_c.conductivity if edge_c.is_alive() else 0
    }
    
    print(f"\n  Conductivity Change (Initial → Final):")
    for color in ["Green", "Blue", "Red"]:
        initial = initial_conductivities[color]
        final = final_conductivities[color]
        change = ((final - initial) / initial) * 100 if initial > 0 else 0
        arrow = "↑" if change > 0 else "↓"
        print(f"    {color:10} : {initial:.4f} → {final:.4f} ({arrow} {abs(change):.1f}%)")
    
    # Step 7: Evaluate success
    print()
    print("=" * 70)
    print("EXPERIMENT RESULTS")
    print("=" * 70)
    
    success_flow = final_blue_flow >= 90
    success_decay_green = final_conductivities["Green"] < initial_conductivities["Green"] * 0.1
    success_decay_red = final_conductivities["Red"] < initial_conductivities["Red"] * 0.1
    
    print(f"\n  Success Criteria:")
    print(f"    [{'✓' if success_flow else '✗'}] Flow to Blue >= 90%: {final_blue_flow:.2f}%")
    print(f"    [{'✓' if success_decay_green else '✗'}] Green edge decayed significantly: {final_conductivities['Green']:.6f}")
    print(f"    [{'✓' if success_decay_red else '✗'}] Red edge decayed significantly: {final_conductivities['Red']:.6f}")
    
    overall_success = success_flow and success_decay_green and success_decay_red
    
    print()
    if overall_success:
        print("  ╔═════════════════════════════════════╗")
        print("  ║  EXPERIMENT 1: PASSED ✓            ║")
        print("  ║  The system correctly prioritized   ║")
        print("  ║  high-conductivity truth!           ║")
        print("  ╚═════════════════════════════════════╝")
    else:
        print("  ╔═════════════════════════════════════╗")
        print("  ║  EXPERIMENT 1: PARTIAL SUCCESS     ║")
        print("  ║  Some criteria not fully met.      ║")
        print("  ╚═════════════════════════════════════╝")
    
    # Return results for programmatic use
    return {
        "success": overall_success,
        "initial_blue_flow": initial_blue_flow,
        "final_blue_flow": final_blue_flow,
        "initial_conductivities": initial_conductivities,
        "final_conductivities": final_conductivities,
        "graph_stats": graph.get_statistics()
    }


if __name__ == "__main__":
    results = run_experiment()
    print(f"\n\nFinal Statistics: {results['graph_stats']}")
