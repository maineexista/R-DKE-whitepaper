"""
Module B: The Physarum Truth-Graph (Memory Layer)
===================================================

Goal: A graph database where edges have "physics."

This is not just Node A -> Node B. The edge connecting them acts 
like a biological tube with conductivity, decay, and nutrient flow.

The Physics Engine Rules:
- Conductivity (C): Represents the thickness of the connection
- Decay (D): Every N cycles, reduce C by a decay factor
- Nutrient Flow: External verification injects nutrient spikes
"""

import uuid
import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict

from .semantic_atomizer import SemanticAtom


@dataclass
class Edge:
    """
    A physics-enabled edge in the Physarum Truth-Graph.
    
    Acts like a biological tube with conductivity that can grow or decay.
    """
    source: str
    target: str
    predicate: str
    conductivity: float = 1.0  # Thickness of the connection
    truth_weight: float = 1.0
    source_reliability: float = 0.5
    access_count: int = 0
    last_accessed: str = field(default_factory=lambda: datetime.now().isoformat())
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    edge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Context and metadata
    context: str = ""
    atom_ids: List[str] = field(default_factory=list)
    
    def combined_weight(self) -> float:
        """Calculate effective weight considering all factors."""
        return self.conductivity * self.truth_weight * self.source_reliability
    
    def reinforce(self, amount: float = 0.1) -> None:
        """
        Reinforce this edge (increase conductivity).
        Called when a query successfully traverses this edge.
        """
        self.conductivity = min(10.0, self.conductivity + amount)
        self.access_count += 1
        self.last_accessed = datetime.now().isoformat()
    
    def decay(self, factor: float = 0.95) -> None:
        """
        Apply decay to this edge.
        Rule: Every N cycles, reduce C by a decay factor (e.g., C=C×0.95).
        """
        self.conductivity *= factor
    
    def inject_nutrient(self, amount: float = 5.0) -> None:
        """
        Inject a massive nutrient spike.
        Rule: When external verification confirms A→B, inject nutrient spike.
        """
        self.conductivity = min(10.0, self.conductivity + amount)
        self.truth_weight = min(1.0, self.truth_weight + 0.1)
    
    def is_alive(self, threshold: float = 0.01) -> bool:
        """Check if the edge is still alive (above decay threshold)."""
        return self.conductivity >= threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary."""
        return {
            "edge_id": self.edge_id,
            "source": self.source,
            "target": self.target,
            "predicate": self.predicate,
            "conductivity": self.conductivity,
            "truth_weight": self.truth_weight,
            "source_reliability": self.source_reliability,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "created_at": self.created_at,
            "context": self.context,
            "atom_ids": self.atom_ids,
            "combined_weight": self.combined_weight()
        }


class Node:
    """A node in the Physarum Truth-Graph."""
    
    def __init__(self, name: str, node_type: str = "entity"):
        self.name = name
        self.node_type = node_type
        self.outgoing_edges: Dict[str, Edge] = {}  # edge_id -> Edge
        self.incoming_edges: Dict[str, Edge] = {}  # edge_id -> Edge
        self.metadata: Dict[str, Any] = {}
        self.access_count: int = 0
        self.created_at: str = datetime.now().isoformat()
    
    def add_outgoing(self, edge: Edge) -> None:
        """Add an outgoing edge."""
        self.outgoing_edges[edge.edge_id] = edge
    
    def add_incoming(self, edge: Edge) -> None:
        """Add an incoming edge."""
        self.incoming_edges[edge.edge_id] = edge
    
    def get_neighbors(self, min_conductivity: float = 0.0) -> List[Tuple[str, Edge]]:
        """Get neighbors with edges above minimum conductivity."""
        neighbors = []
        for edge in self.outgoing_edges.values():
            if edge.conductivity >= min_conductivity:
                neighbors.append((edge.target, edge))
        return neighbors
    
    def total_outgoing_conductivity(self) -> float:
        """Sum of all outgoing edge conductivities."""
        return sum(e.conductivity for e in self.outgoing_edges.values())


class PhysarumTruthGraph:
    """
    The Physarum Truth-Graph: A living knowledge graph with physics.
    
    Key features:
    - Edges have conductivity that grows with use
    - Edges decay over time (forgetting)
    - External verification injects "nutrients"
    - Dead edges (low conductivity) are pruned
    """
    
    def __init__(
        self,
        decay_factor: float = 0.95,
        decay_threshold: float = 0.01,
        reinforcement_amount: float = 0.1,
        nutrient_spike: float = 5.0
    ):
        """
        Initialize the Physarum Truth-Graph.
        
        Args:
            decay_factor: Multiplicative decay per cycle (default 0.95)
            decay_threshold: Below this, edges are considered dead
            reinforcement_amount: Amount to add on successful traversal
            nutrient_spike: Amount to add on external verification
        """
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        
        # Physics parameters
        self.decay_factor = decay_factor
        self.decay_threshold = decay_threshold
        self.reinforcement_amount = reinforcement_amount
        self.nutrient_spike = nutrient_spike
        
        # Cycle tracking
        self.cycle_count: int = 0
        
        # Statistics
        self.stats = {
            "atoms_ingested": 0,
            "edges_created": 0,
            "edges_pruned": 0,
            "queries_processed": 0,
            "reinforcements": 0,
            "nutrient_injections": 0
        }
    
    def add_atom(self, atom: SemanticAtom) -> Edge:
        """
        Add a Semantic Atom to the graph.
        
        Creates nodes for subject and object if they don't exist,
        and creates or reinforces the edge between them.
        
        Args:
            atom: The SemanticAtom to add
            
        Returns:
            The created or updated Edge
        """
        # Ensure nodes exist
        if atom.subject not in self.nodes:
            self.nodes[atom.subject] = Node(atom.subject)
        if atom.obj not in self.nodes:
            self.nodes[atom.obj] = Node(atom.obj)
        
        # Check for existing edge with same subject, predicate, object
        existing_edge = self._find_edge(atom.subject, atom.predicate, atom.obj)
        
        if existing_edge:
            # Reinforce existing edge
            existing_edge.reinforce(self.reinforcement_amount)
            existing_edge.atom_ids.append(atom.atom_id)
            # Update reliability if new source is more reliable
            if atom.source_reliability > existing_edge.source_reliability:
                existing_edge.source_reliability = atom.source_reliability
            self.stats["reinforcements"] += 1
            return existing_edge
        
        # Create new edge
        edge = Edge(
            source=atom.subject,
            target=atom.obj,
            predicate=atom.predicate,
            conductivity=atom.combined_weight(),
            truth_weight=atom.truth_weight,
            source_reliability=atom.source_reliability,
            context=atom.context,
            atom_ids=[atom.atom_id]
        )
        
        self.edges[edge.edge_id] = edge
        self.nodes[atom.subject].add_outgoing(edge)
        self.nodes[atom.obj].add_incoming(edge)
        
        self.stats["atoms_ingested"] += 1
        self.stats["edges_created"] += 1
        
        return edge
    
    def _find_edge(
        self, 
        source: str, 
        predicate: str, 
        target: str
    ) -> Optional[Edge]:
        """Find an existing edge matching the criteria."""
        if source not in self.nodes:
            return None
        
        for edge in self.nodes[source].outgoing_edges.values():
            if edge.target == target and edge.predicate == predicate:
                return edge
        return None
    
    def get_node(self, name: str) -> Optional[Node]:
        """Get a node by name."""
        return self.nodes.get(name)
    
    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """Get an edge by ID."""
        return self.edges.get(edge_id)
    
    def get_edges_from(
        self, 
        node_name: str, 
        min_conductivity: float = 0.0
    ) -> List[Edge]:
        """Get all edges from a node above minimum conductivity."""
        if node_name not in self.nodes:
            return []
        
        return [
            e for e in self.nodes[node_name].outgoing_edges.values()
            if e.conductivity >= min_conductivity
        ]
    
    def get_edges_to(
        self, 
        node_name: str, 
        min_conductivity: float = 0.0
    ) -> List[Edge]:
        """Get all edges to a node above minimum conductivity."""
        if node_name not in self.nodes:
            return []
        
        return [
            e for e in self.nodes[node_name].incoming_edges.values()
            if e.conductivity >= min_conductivity
        ]
    
    def find_paths(
        self,
        start: str,
        end: str,
        max_depth: int = 5,
        min_conductivity: float = 0.0
    ) -> List[List[Edge]]:
        """
        Find all paths between two nodes.
        
        Args:
            start: Starting node name
            end: Ending node name
            max_depth: Maximum path length
            min_conductivity: Minimum edge conductivity to consider
            
        Returns:
            List of paths (each path is a list of edges)
        """
        if start not in self.nodes or end not in self.nodes:
            return []
        
        paths = []
        visited = set()
        
        def dfs(current: str, path: List[Edge], depth: int):
            if depth > max_depth:
                return
            
            if current == end and path:
                paths.append(path.copy())
                return
            
            if current in visited:
                return
            
            visited.add(current)
            
            for edge in self.get_edges_from(current, min_conductivity):
                path.append(edge)
                dfs(edge.target, path, depth + 1)
                path.pop()
            
            visited.remove(current)
        
        dfs(start, [], 0)
        return paths
    
    def reinforce_path(self, path: List[Edge]) -> None:
        """Reinforce all edges in a path."""
        for edge in path:
            edge.reinforce(self.reinforcement_amount)
            self.stats["reinforcements"] += 1
    
    def verify_edge(
        self, 
        source: str, 
        predicate: str, 
        target: str
    ) -> bool:
        """
        Externally verify an edge and inject nutrient spike.
        
        Rule: When external verification confirms A→B, inject nutrient spike.
        
        Returns:
            True if edge was found and verified, False otherwise
        """
        edge = self._find_edge(source, predicate, target)
        if edge:
            edge.inject_nutrient(self.nutrient_spike)
            self.stats["nutrient_injections"] += 1
            return True
        return False
    
    def run_decay_cycle(self) -> int:
        """
        Run one decay cycle on all edges.
        
        Rule: Every N cycles, reduce C by a decay factor (e.g., C=C×0.95).
        Result: Noise and outdated facts naturally wither away.
        
        Returns:
            Number of edges pruned
        """
        self.cycle_count += 1
        edges_to_prune = []
        
        for edge_id, edge in self.edges.items():
            edge.decay(self.decay_factor)
            
            if not edge.is_alive(self.decay_threshold):
                edges_to_prune.append(edge_id)
        
        # Prune dead edges
        for edge_id in edges_to_prune:
            self._prune_edge(edge_id)
        
        self.stats["edges_pruned"] += len(edges_to_prune)
        return len(edges_to_prune)
    
    def _prune_edge(self, edge_id: str) -> None:
        """Remove an edge from the graph."""
        if edge_id not in self.edges:
            return
        
        edge = self.edges[edge_id]
        
        # Remove from source node
        if edge.source in self.nodes:
            self.nodes[edge.source].outgoing_edges.pop(edge_id, None)
        
        # Remove from target node
        if edge.target in self.nodes:
            self.nodes[edge.target].incoming_edges.pop(edge_id, None)
        
        # Remove from edges dict
        del self.edges[edge_id]
    
    def get_alive_edges(self) -> List[Edge]:
        """Get all edges above decay threshold."""
        return [e for e in self.edges.values() if e.is_alive(self.decay_threshold)]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        alive_edges = self.get_alive_edges()
        return {
            **self.stats,
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "alive_edges": len(alive_edges),
            "cycle_count": self.cycle_count,
            "avg_conductivity": (
                sum(e.conductivity for e in alive_edges) / len(alive_edges)
                if alive_edges else 0
            ),
            "max_conductivity": (
                max(e.conductivity for e in alive_edges)
                if alive_edges else 0
            )
        }
    
    def export_graph(self) -> Dict[str, Any]:
        """Export the entire graph as a dictionary."""
        return {
            "nodes": list(self.nodes.keys()),
            "edges": [e.to_dict() for e in self.edges.values()],
            "statistics": self.get_statistics()
        }
    
    def get_subgraph_around(
        self, 
        node_name: str, 
        depth: int = 2,
        min_conductivity: float = 0.0
    ) -> Dict[str, Any]:
        """Get a subgraph around a specific node."""
        if node_name not in self.nodes:
            return {"nodes": [], "edges": []}
        
        visited_nodes: Set[str] = set()
        edges_in_subgraph: List[Edge] = []
        
        def explore(current: str, remaining_depth: int):
            if remaining_depth < 0 or current in visited_nodes:
                return
            
            visited_nodes.add(current)
            
            for edge in self.get_edges_from(current, min_conductivity):
                edges_in_subgraph.append(edge)
                explore(edge.target, remaining_depth - 1)
            
            for edge in self.get_edges_to(current, min_conductivity):
                edges_in_subgraph.append(edge)
                explore(edge.source, remaining_depth - 1)
        
        explore(node_name, depth)
        
        return {
            "nodes": list(visited_nodes),
            "edges": [e.to_dict() for e in edges_in_subgraph]
        }
    
    def find_contradictions(
        self, 
        node_name: str, 
        predicate: str
    ) -> List[Tuple[Edge, Edge]]:
        """
        Find edges that might be contradictory.
        
        Returns pairs of edges with the same predicate but different targets.
        """
        if node_name not in self.nodes:
            return []
        
        # Get all edges with the given predicate
        predicate_edges = [
            e for e in self.nodes[node_name].outgoing_edges.values()
            if e.predicate == predicate
        ]
        
        # Find pairs with different targets
        contradictions = []
        for i, e1 in enumerate(predicate_edges):
            for e2 in predicate_edges[i+1:]:
                if e1.target != e2.target:
                    contradictions.append((e1, e2))
        
        return contradictions
    
    def resolve_contradiction(
        self, 
        node_name: str, 
        predicate: str
    ) -> Optional[Edge]:
        """
        Resolve contradictions by returning the highest conductivity edge.
        
        This is the Physarum way: the thickest tube wins.
        """
        if node_name not in self.nodes:
            return None
        
        predicate_edges = [
            e for e in self.nodes[node_name].outgoing_edges.values()
            if e.predicate == predicate
        ]
        
        if not predicate_edges:
            return None
        
        return max(predicate_edges, key=lambda e: e.combined_weight())
