import networkx as nx
import numpy as np
from collections import defaultdict

class RDKE_Graph:
    def __init__(self, alpha=0.9, beta=0.1, eta=0.1, lam=0.05, gamma=1.0):
        """
        Implements the math from Section 2.2 of the Whitepaper.
        alpha: Propagation gain
        beta: Leakage/decay of node activation
        eta: Edge reinforcement rate (default 0.1 is stable)
        lam: Passive edge decay
        gamma: Nutrient injection magnitude
        """
        self.graph = nx.DiGraph()
        self.alpha = alpha
        self.beta = beta
        self.eta = eta
        self.lam = lam
        self.gamma = gamma
        
        # State vectors (dictionaries mapped to node IDs)
        self.x = defaultdict(float)  # Node activation (protoplasm)
        self.u = defaultdict(float)  # Node uncertainty
        
    def add_knowledge_atom(self, node_id, uncertainty=0.5):
        self.graph.add_node(node_id)
        self.u[node_id] = uncertainty
        self.x[node_id] = 0.0

    def add_relation(self, u, v, weight=0.5, provenance_score=1.0):
        # w_uv is combined structural weight * provenance
        self.graph.add_edge(u, v, weight=weight, provenance=provenance_score)

    def step(self, ablation_config=None):
        """
        Executes one iteration of the Physarum Loop.
        ablation_config: dict to toggle features off for Section 4.3 experiments.
        """
        if ablation_config is None:
            ablation_config = {}

        nodes = list(self.graph.nodes())
        new_x = self.x.copy()
        
        # 1. Calculate Nutrient Injection (s_v)
        s = defaultdict(float)
        for v in nodes:
            # --- NEW: Basal Metabolic Rate ---
            # Always add a tiny trickle. This prevents nodes from being "vacuums"
            # and ensures flow happens even between high-pressure nodes.
            s[v] = 0.01 
            
            if ablation_config.get('no_uncertainty_injection'):
                s[v] += self.gamma * 0.1 
            else:
                # Targeted Injection adds a BIG boost (1.0) on top of the trickle
                if self.u[v] > 0.6: 
                    s[v] += self.gamma

        # 2. Flow Dynamics (Node Activation Update)
        # x_v(t+1) = alpha * Sum(incoming flow) + s_v - beta * x_v
        for v in nodes:
            incoming_flow = 0.0
            for u in self.graph.predecessors(v):
                edge_data = self.graph[u][v]
                w_uv = edge_data['weight']
                
                # Ablation 'No Provenance': Treat all edges as equal reliability
                if not ablation_config.get('no_provenance'):
                    w_uv *= edge_data['provenance']

                # Normalize outgoing capacity (d_u)
                out_degree_weight = sum([self.graph[u][n]['weight'] for n in self.graph.successors(u)])
                if out_degree_weight > 0:
                    d_u = 1.0 / out_degree_weight
                    incoming_flow += w_uv * d_u * self.x[u]
            
            new_x[v] = (self.alpha * incoming_flow) + s[v] - (self.beta * self.x[v])
        
        self.x = new_x

        # 3. Edge Adaptation (Reinforcement/Decay)
        # Ablation 'No Physarum': Skip this block entirely (static graph)
        if not ablation_config.get('no_physarum_dynamics'):
            for u, v in self.graph.edges():
                w_uv = self.graph[u][v]['weight']
                
                # Flux proxy: absolute difference in activation
                flux = abs(self.x[u] - self.x[v])
                
                # --- NEW: Structure-Preserving Dynamics ---
                # Retrieve provenance (truth score), default to 1.0 if missing
                provenance = self.graph[u][v].get('provenance', 1.0)

                # If ablation 'no_provenance' is active, disable the friction logic
                if ablation_config.get('no_provenance'):
                    provenance = 1.0

                # MODIFIED UPDATE RULE: 
                # Friction factor: Truthful paths reinforce fully, untruthful ones resist.
                # d/dt w = eta * (flux * provenance) - lambda * w
                delta_w = (self.eta * flux * provenance) - (self.lam * w_uv)
                # ------------------------------------------
                
                new_w = w_uv + delta_w
                # Clip weights [0, 1]
                self.graph[u][v]['weight'] = max(0.0, min(1.0, new_w))

    def get_strongest_path(self, start_node, end_node):
        """Synthesis Engine: Find path with highest combined weight."""
        try:
            return nx.shortest_path(self.graph, start_node, end_node, weight=lambda u, v, d: 1/d['weight'])
        except nx.NetworkXNoPath:
            return None