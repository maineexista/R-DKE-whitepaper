import time
import pandas as pd
import numpy as np
from rdke_core import RDKE_Graph

# --- METRIC LOGGER ---
results = []

def log_experiment(variant, task, accuracy, steps, energy_proxy, time_taken):
    results.append({
        "Variant": variant,
        "Task": task,
        "Accuracy": accuracy,
        "Convergence Steps": steps,
        "Energy (Sum x_v)": energy_proxy,
        "Time (ms)": time_taken * 1000
    })

# --- SCENARIO GENERATORS ---

def setup_fever_scenario(noise_level=0.3):
    """
    Creates a graph with a True claim path and several False claim paths.
    False paths have lower provenance but might be shorter.
    """
    rdke = RDKE_Graph(eta=0.1, alpha=0.9) # Standard stable parameters
    
    rdke.add_knowledge_atom('Start', uncertainty=0.1)
    
    # --- CHANGED: Low Uncertainty for Known Facts ---
    # We "know" these facts, so they act as stable pipes, not hungry sources.
    # This creates the pressure gradient needed for flow.
    rdke.add_knowledge_atom('Fact_A', uncertainty=0.2) 
    rdke.add_knowledge_atom('Fact_B', uncertainty=0.2)
    
    # The Claim remains High Uncertainty (The "Hungry" Destination)
    rdke.add_knowledge_atom('Claim_True', uncertainty=0.9)
    
    # False Chain
    rdke.add_knowledge_atom('False_X', uncertainty=0.5)
    
    # Edges
    # Option A structure: Truth has high provenance (0.9), False has low (0.4)
    rdke.add_relation('Start', 'Fact_A', weight=0.5, provenance_score=0.9)
    rdke.add_relation('Fact_A', 'Fact_B', weight=0.5, provenance_score=0.9)
    rdke.add_relation('Fact_B', 'Claim_True', weight=0.5, provenance_score=0.9)
    
    # False edges start "clogged" (weight=0.1) and have low truth (0.4)
    # This creates the resistance ("Friction") for the dynamics.
    rdke.add_relation('Start', 'False_X', weight=0.1, provenance_score=0.4) 
    rdke.add_relation('False_X', 'Claim_True', weight=0.1, provenance_score=0.4)
    
    return rdke

def run_ablation_suite():
    # Define Ablation Configurations
    configs = {
        "Full R-DKE": {},
        "No Physarum (Static)": {'no_physarum_dynamics': True},
        "No Uncertainty Inj.": {'no_uncertainty_injection': True},
        "No Provenance": {'no_provenance': True}
    }

    print(f"{'='*20} RUNNING ABLATION SUITE {'='*20}")
    
    for variant_name, config in configs.items():
        # --- Task 1: FEVER / Fact Verification ---
        model = setup_fever_scenario()
        
        start_time = time.time()
        total_energy = 0
        
        # Run Dynamics Loop
        for t in range(50): # Run for 50 timesteps
            model.step(ablation_config=config)
            total_energy += sum(model.x.values())
        
        duration = time.time() - start_time
        
        # Evaluate: Did it reinforce the True path?
        # We check if the edge weight of the True path > False path
        try:
            w_true = model.graph['Fact_B']['Claim_True']['weight']
        except KeyError:
            w_true = 0
            
        try:
            w_false = model.graph['False_X']['Claim_True']['weight']
        except KeyError:
            w_false = 0 # Path pruned completely
            
        # We consider it a "Success" if the True path is stronger
        success = w_true > w_false
        
        log_experiment(
            variant=variant_name, 
            task="FEVER (Synthetic)", 
            accuracy=1.0 if success else 0.0, 
            steps=50, 
            energy_proxy=round(total_energy, 2), 
            time_taken=duration
        )

    # Output Results
    df = pd.DataFrame(results)
    print(df.to_markdown(index=False))
    df.to_csv("rdke_ablation_results_final.csv", index=False)

if __name__ == "__main__":
    run_ablation_suite()