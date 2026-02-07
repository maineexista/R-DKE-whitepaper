"""
R-DKE Validation Suite
========================

Run all three validation experiments to prove the R-DKE architecture works.

Usage:
    python run_experiments.py          # Run all experiments
    python run_experiments.py 1        # Run experiment 1 only
    python run_experiments.py 2        # Run experiment 2 only
    python run_experiments.py 3        # Run experiment 3 only
"""

import sys
import json
from datetime import datetime

def run_all():
    """Run all experiments and generate a report."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + "R-DKE (Physarum Edition) - Validation Suite".center(68) + "║")
    print("║" + "Version 2.0 | Biological Logic Implementation".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    results = {}
    
    # Experiment 1: Contradiction Pressure
    print("\n" + "▓" * 70)
    print("RUNNING EXPERIMENT 1: CONTRADICTION PRESSURE")
    print("▓" * 70 + "\n")
    
    from experiments.experiment_1_contradiction_pressure import run_experiment as exp1
    results["experiment_1"] = exp1()
    
    # Experiment 2: Gap Fill
    print("\n" + "▓" * 70)
    print("RUNNING EXPERIMENT 2: NUTRIENT GAP FILL")
    print("▓" * 70 + "\n")
    
    from experiments.experiment_2_gap_fill import run_experiment as exp2
    results["experiment_2"] = exp2()
    
    # Experiment 3: Forgetfulness
    print("\n" + "▓" * 70)
    print("RUNNING EXPERIMENT 3: EFFICIENCY OF FORGETFULNESS")
    print("▓" * 70 + "\n")
    
    from experiments.experiment_3_forgetfulness import run_experiment as exp3
    results["experiment_3"] = exp3()
    
    # Summary Report
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + "VALIDATION SUITE SUMMARY".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    exp1_status = "✓ PASSED" if results["experiment_1"]["success"] else "✗ FAILED"
    exp2_status = "✓ PASSED" if results["experiment_2"]["success"] else "✗ FAILED"
    exp3_status = "✓ PASSED" if results["experiment_3"]["success"] else "✗ FAILED"
    
    print(f"  Experiment 1 (Contradiction Pressure):    {exp1_status}")
    print(f"  Experiment 2 (Nutrient Gap Fill):         {exp2_status}")
    print(f"  Experiment 3 (Efficiency of Forgetfulness): {exp3_status}")
    
    total_passed = sum(1 for r in results.values() if r["success"])
    
    print()
    print(f"  Total: {total_passed}/3 experiments passed")
    print()
    
    if total_passed == 3:
        print("  ╔═══════════════════════════════════════════════════════════════╗")
        print("  ║  ALL EXPERIMENTS PASSED! ✓                                   ║")
        print("  ║                                                               ║")
        print("  ║  The R-DKE Physarum Architecture has been validated:          ║")
        print("  ║    • Truth prioritization works correctly                      ║")
        print("  ║    • Recursive gap-filling heals broken paths                  ║")
        print("  ║    • Forgetfulness improves query performance                  ║")
        print("  ╚═══════════════════════════════════════════════════════════════╝")
    else:
        print("  ╔═══════════════════════════════════════════════════════════════╗")
        print("  ║  PARTIAL SUCCESS                                             ║")
        print(f"  ║  {total_passed}/3 experiments passed. Review failed tests.              ║")
        print("  ╚═══════════════════════════════════════════════════════════════╝")
    
    # Save results to JSON
    results["timestamp"] = datetime.now().isoformat()
    results["total_passed"] = total_passed
    
    with open("validation_results.json", "w") as f:
        # Convert non-serializable items
        def clean_results(obj):
            if isinstance(obj, dict):
                return {k: clean_results(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [clean_results(i) for i in obj]
            elif isinstance(obj, float):
                return round(obj, 6)
            return obj
        
        json.dump(clean_results(results), f, indent=2)
    
    print(f"\n  Results saved to: validation_results.json")
    print()
    
    return results


def run_single(experiment_num):
    """Run a single experiment."""
    if experiment_num == 1:
        from experiments.experiment_1_contradiction_pressure import run_experiment
    elif experiment_num == 2:
        from experiments.experiment_2_gap_fill import run_experiment
    elif experiment_num == 3:
        from experiments.experiment_3_forgetfulness import run_experiment
    else:
        print(f"Unknown experiment: {experiment_num}")
        print("Valid experiments: 1, 2, 3")
        return
    
    run_experiment()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            exp_num = int(sys.argv[1])
            run_single(exp_num)
        except ValueError:
            print(f"Invalid argument: {sys.argv[1]}")
            print("Usage: python run_experiments.py [1|2|3]")
    else:
        run_all()
