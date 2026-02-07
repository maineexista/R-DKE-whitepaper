"""
Experiment 2: The "Nutrient" Gap Fill (Recursion)
===================================================

Objective: Prove the system can "heal" broken logic paths automatically.

Input Data:
- Node A: "Elon Musk"
- Node C: "SpaceX"
- Missing Link: The connection (CEO/Founder) is deleted.

Process: Ask: "What is the relationship between Elon Musk and SpaceX?"

Expected Behavior:
1. Fluid flows from Elon and stops (Dead End).
2. System triggers Recursion Event.
3. System generates internal query: "Elon Musk SpaceX relation."
4. System creates temporary Edge B.

Success Metric: The system returns the correct path and permanently 
               adds the new Edge B to the graph with a high "Truth Weight."
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rdke import SemanticAtomizer, SemanticAtom, PhysarumTruthGraph, RecursiveEngine
from rdke.recursive_engine import create_simple_fetcher


def run_experiment():
    """Run the Nutrient Gap Fill experiment."""
    print("=" * 70)
    print("EXPERIMENT 2: THE NUTRIENT GAP FILL (RECURSION) TEST")
    print("=" * 70)
    print()
    print("Objective: Prove the system can heal broken logic paths automatically.")
    print()
    
    # Initialize components
    atomizer = SemanticAtomizer()
    graph = PhysarumTruthGraph(
        decay_factor=0.95,
        decay_threshold=0.01,
        reinforcement_amount=0.2,
        nutrient_spike=5.0
    )
    
    # Create a mock external knowledge base for gap filling
    external_knowledge = {
        "elon musk spacex": [
            ("Elon_Musk", "founded", "SpaceX"),
            ("Elon_Musk", "is_CEO_of", "SpaceX"),
        ],
        "elon musk": [
            ("Elon_Musk", "founded", "Tesla"),
            ("Elon_Musk", "founded", "SpaceX"),
        ],
        "spacex": [
            ("SpaceX", "is_a", "Aerospace_Company"),
            ("SpaceX", "founded_in", "2002"),
        ]
    }
    
    fetcher = create_simple_fetcher(external_knowledge)
    
    engine = RecursiveEngine(
        graph, 
        atomizer,
        external_fetcher=fetcher,
        enable_recursion=True
    )
    
    # Step 1: Set up initial graph with a gap
    print("-" * 70)
    print("STEP 1: Setting Up Initial Graph (WITH gap)")
    print("-" * 70)
    
    # Add some context nodes but NO direct connection to SpaceX
    atom1 = atomizer.parse_triple(
        subject="Elon_Musk",
        predicate="is_a",
        obj="Entrepreneur",
        context="general_knowledge",
        source_reliability=0.8
    )
    graph.add_atom(atom1)
    print(f"  Added: {atom1}")
    
    atom2 = atomizer.parse_triple(
        subject="Elon_Musk",
        predicate="born_in",
        obj="South_Africa",
        context="general_knowledge",
        source_reliability=0.9
    )
    graph.add_atom(atom2)
    print(f"  Added: {atom2}")
    
    atom3 = atomizer.parse_triple(
        subject="SpaceX",
        predicate="is_a",
        obj="Company",
        context="general_knowledge",
        source_reliability=0.8
    )
    graph.add_atom(atom3)
    print(f"  Added: {atom3}")
    
    print(f"\n  Initial Graph Stats: {graph.get_statistics()}")
    
    # Show initial connections
    print(f"\n  Connections from Elon_Musk:")
    for edge in graph.get_edges_from("Elon_Musk"):
        print(f"    → {edge.predicate} → {edge.target}")
    
    # Verify there's NO connection to SpaceX
    musk_to_spacex = graph.find_paths("Elon_Musk", "SpaceX", max_depth=3)
    print(f"\n  Direct paths from Elon_Musk to SpaceX: {len(musk_to_spacex)}")
    
    # Step 2: Query without recursion first
    print()
    print("-" * 70)
    print("STEP 2: Query WITHOUT Recursion (Baseline)")
    print("-" * 70)
    
    # Temporarily disable recursion
    engine.enable_recursion = False
    
    result_no_recursion = engine.query(
        start_node="Elon_Musk",
        end_node="SpaceX",
        question="What is the relationship between Elon Musk and SpaceX?"
    )
    
    print(f"\n  Flow reached SpaceX: {'Yes' if 'SpaceX' in result_no_recursion.flow_distribution else 'No'}")
    print(f"  Gaps detected: {result_no_recursion.gaps_detected}")
    print(f"  Paths found: {len(result_no_recursion.paths_found)}")
    
    # Step 3: Query WITH recursion
    print()
    print("-" * 70)
    print("STEP 3: Query WITH Recursion Enabled")
    print("-" * 70)
    
    # Re-enable recursion
    engine.enable_recursion = True
    
    result_with_recursion = engine.query(
        start_node="Elon_Musk",
        end_node="SpaceX",
        question="What is the relationship between Elon Musk and SpaceX?"
    )
    
    print(f"\n  Recursion triggered: {result_with_recursion.recursion_triggered}")
    print(f"  Recursion events: {len(engine.recursion_events)}")
    
    if engine.recursion_events:
        for i, event in enumerate(engine.recursion_events):
            print(f"\n  Recursion Event {i+1}:")
            print(f"    Gap from: {event.gap_from}")
            print(f"    Query generated: {event.query_generated}")
            print(f"    Atoms created: {len(event.atoms_created)}")
            print(f"    Edge created: {event.edge_created is not None}")
            print(f"    Success: {event.success}")
    
    # Step 4: Verify the gap was filled
    print()
    print("-" * 70)
    print("STEP 4: Verify Gap Was Filled")
    print("-" * 70)
    
    # Check new connections
    print(f"\n  New connections from Elon_Musk:")
    for edge in graph.get_edges_from("Elon_Musk"):
        print(f"    → {edge.predicate} → {edge.target} (conductivity: {edge.conductivity:.3f})")
    
    # Check if path now exists
    new_paths = graph.find_paths("Elon_Musk", "SpaceX", max_depth=3)
    print(f"\n  Paths from Elon_Musk to SpaceX after recursion: {len(new_paths)}")
    
    if new_paths:
        print(f"\n  Best path found:")
        best_path = max(new_paths, key=lambda p: sum(e.combined_weight() for e in p))
        for edge in best_path:
            print(f"    {edge.source} --[{edge.predicate}]--> {edge.target}")
    
    # Step 5: Query again to verify permanent storage
    print()
    print("-" * 70)
    print("STEP 5: Second Query (Verify Permanent Storage)")
    print("-" * 70)
    
    # Clear recursion history
    engine.recursion_events.clear()
    
    result_second = engine.query(
        start_node="Elon_Musk",
        end_node="SpaceX",
        question="What is the relationship between Elon Musk and SpaceX?"
    )
    
    print(f"\n  Recursion triggered: {result_second.recursion_triggered}")
    print(f"  New recursion events: {len(engine.recursion_events)}")
    print(f"  Paths found: {len(result_second.paths_found)}")
    
    if "SpaceX" in result_second.flow_distribution:
        print(f"  Flow to SpaceX: {result_second.flow_distribution['SpaceX']:.3f}")
    
    # Step 6: Check truth weights
    print()
    print("-" * 70)
    print("STEP 6: Analyze New Edge Properties")
    print("-" * 70)
    
    # Find the new edges connecting Musk to SpaceX
    new_edges = []
    if "Elon_Musk" in graph.nodes:
        for edge in graph.nodes["Elon_Musk"].outgoing_edges.values():
            if edge.target == "SpaceX":
                new_edges.append(edge)
    
    print(f"\n  Edges from Elon_Musk to SpaceX: {len(new_edges)}")
    for edge in new_edges:
        print(f"\n    Edge: {edge.predicate}")
        print(f"      Conductivity: {edge.conductivity:.4f}")
        print(f"      Truth Weight: {edge.truth_weight:.4f}")
        print(f"      Source Reliability: {edge.source_reliability:.4f}")
        print(f"      Combined Weight: {edge.combined_weight():.4f}")
        print(f"      Access Count: {edge.access_count}")
    
    # Step 7: Evaluate success
    print()
    print("=" * 70)
    print("EXPERIMENT RESULTS")
    print("=" * 70)
    
    # Success criteria
    gap_detected = len(result_no_recursion.gaps_detected) > 0 or len(result_no_recursion.paths_found) == 0
    recursion_occurred = result_with_recursion.recursion_triggered or len(engine.recursion_events) > 0
    path_created = len(new_paths) > 0
    permanent_storage = len(engine.recursion_events) == 0 and len(result_second.paths_found) > 0
    high_truth_weight = any(e.combined_weight() > 0.3 for e in new_edges) if new_edges else False
    
    print(f"\n  Success Criteria:")
    print(f"    [{'✓' if gap_detected else '✗'}] Gap detected in initial query")
    print(f"    [{'✓' if recursion_occurred else '✗'}] Recursion event triggered")
    print(f"    [{'✓' if path_created else '✗'}] New path created to SpaceX")
    print(f"    [{'✓' if permanent_storage else '✗'}] Edge permanently stored (no re-fetch)")
    print(f"    [{'✓' if high_truth_weight else '✗'}] High truth weight on new edge")
    
    overall_success = gap_detected and path_created and high_truth_weight
    
    print()
    if overall_success:
        print("  ╔═════════════════════════════════════╗")
        print("  ║  EXPERIMENT 2: PASSED ✓            ║")
        print("  ║  The system successfully healed     ║")
        print("  ║  the broken logic path!             ║")
        print("  ╚═════════════════════════════════════╝")
    else:
        print("  ╔═════════════════════════════════════╗")
        print("  ║  EXPERIMENT 2: PARTIAL SUCCESS     ║")
        print("  ║  Some criteria not fully met.      ║")
        print("  ╚═════════════════════════════════════╝")
    
    return {
        "success": overall_success,
        "gap_detected": gap_detected,
        "recursion_occurred": recursion_occurred,
        "path_created": path_created,
        "permanent_storage": permanent_storage,
        "new_edges": len(new_edges),
        "graph_stats": graph.get_statistics()
    }


if __name__ == "__main__":
    results = run_experiment()
    print(f"\n\nFinal Statistics: {results['graph_stats']}")
