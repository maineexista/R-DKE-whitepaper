"""
R-DKE Interactive Demo
========================

A simple interactive demo of the R-DKE system.
Run with: python demo.py
"""

from rdke import SemanticAtomizer, PhysarumTruthGraph, RecursiveEngine


def main():
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " R-DKE Physarum Edition - Interactive Demo ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # Initialize the system
    atomizer = SemanticAtomizer()
    graph = PhysarumTruthGraph(
        decay_factor=0.95,
        decay_threshold=0.01,
        reinforcement_amount=0.2,
        nutrient_spike=5.0
    )
    engine = RecursiveEngine(graph, atomizer)
    
    # Add some initial knowledge
    print("Loading initial knowledge base...")
    print()
    
    knowledge = [
        # Tech companies
        ("Apple", "makes", "iPhone", 0.9),
        ("Apple", "makes", "MacBook", 0.9),
        ("Apple", "founded_by", "Steve_Jobs", 0.95),
        ("Google", "owns", "YouTube", 0.95),
        ("Google", "created", "Android", 0.9),
        ("Microsoft", "created", "Windows", 0.95),
        ("Microsoft", "owns", "LinkedIn", 0.9),
        ("Tesla", "founded_by", "Elon_Musk", 0.9),
        ("SpaceX", "founded_by", "Elon_Musk", 0.95),
        
        # Programming
        ("Python", "is_a", "Programming_Language", 0.99),
        ("Python", "created_by", "Guido_van_Rossum", 0.95),
        ("JavaScript", "is_a", "Programming_Language", 0.99),
        ("JavaScript", "runs_in", "Browser", 0.9),
        
        # AI
        ("GPT", "is_a", "Language_Model", 0.95),
        ("GPT", "created_by", "OpenAI", 0.95),
        ("Machine_Learning", "is_part_of", "AI", 0.9),
        ("Neural_Network", "is_used_in", "Deep_Learning", 0.9),
        ("Deep_Learning", "is_part_of", "Machine_Learning", 0.9),
    ]
    
    for subject, predicate, obj, reliability in knowledge:
        atom = atomizer.parse_triple(
            subject=subject,
            predicate=predicate,
            obj=obj,
            source_reliability=reliability
        )
        graph.add_atom(atom)
    
    print(f"  Loaded {len(knowledge)} facts into the Truth Graph")
    print(f"  Graph has {len(graph.nodes)} nodes and {len(graph.edges)} edges")
    print()
    
    # Interactive loop
    print("-" * 60)
    print("Commands:")
    print("  query <node>          - Query knowledge about a node")
    print("  add <s> <p> <o>       - Add a new fact (subject predicate object)")
    print("  verify <s> <p> <o>    - Verify/strengthen a fact")
    print("  decay                 - Run decay cycle")
    print("  stats                 - Show graph statistics")
    print("  nodes                 - List all nodes")
    print("  quit                  - Exit")
    print("-" * 60)
    print()
    
    while True:
        try:
            user_input = input("r-dke> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        parts = user_input.split()
        command = parts[0].lower()
        
        if command == "quit" or command == "exit":
            print("Goodbye!")
            break
        
        elif command == "query" and len(parts) >= 2:
            node = parts[1]
            result = engine.query(node)
            
            print(f"\n  Query: {node}")
            print(f"  Flow distribution:")
            
            percentages = result.get_flow_percentages()
            for dest, pct in sorted(percentages.items(), key=lambda x: -x[1])[:10]:
                bar = "█" * int(pct / 5)
                print(f"    {dest:25} : {pct:6.2f}% {bar}")
            
            print(f"\n  Latency: {result.query_latency_ms:.4f} ms")
            print()
        
        elif command == "add" and len(parts) >= 4:
            subject, predicate, obj = parts[1], parts[2], parts[3]
            atom = atomizer.parse_triple(subject, predicate, obj, source_reliability=0.7)
            edge = graph.add_atom(atom)
            print(f"\n  Added: {subject} --[{predicate}]--> {obj}")
            print(f"  Edge conductivity: {edge.conductivity:.4f}")
            print()
        
        elif command == "verify" and len(parts) >= 4:
            subject, predicate, obj = parts[1], parts[2], parts[3]
            success = graph.verify_edge(subject, predicate, obj)
            if success:
                edge = graph._find_edge(subject, predicate, obj)
                print(f"\n  Verified: {subject} --[{predicate}]--> {obj}")
                print(f"  New conductivity: {edge.conductivity:.4f}")
            else:
                print(f"\n  Edge not found: {subject} --[{predicate}]--> {obj}")
            print()
        
        elif command == "decay":
            pruned = graph.run_decay_cycle()
            print(f"\n  Decay cycle {graph.cycle_count} complete")
            print(f"  Edges pruned: {pruned}")
            print(f"  Alive edges: {len(graph.get_alive_edges())}")
            print()
        
        elif command == "stats":
            stats = graph.get_statistics()
            print(f"\n  Graph Statistics:")
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"    {key}: {value:.4f}")
                else:
                    print(f"    {key}: {value}")
            print()
        
        elif command == "nodes":
            print(f"\n  Nodes ({len(graph.nodes)}):")
            for i, node in enumerate(sorted(graph.nodes.keys())):
                print(f"    {node}", end="")
                if (i + 1) % 4 == 0:
                    print()
            print("\n")
        
        else:
            print(f"  Unknown command: {command}")
            print("  Type 'quit' to exit")
            print()


if __name__ == "__main__":
    main()
