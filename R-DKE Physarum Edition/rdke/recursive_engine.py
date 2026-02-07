"""
Module C: The Recursive Engine (Reasoning Layer)
=================================================

Goal: The system must "breathe" (Oscillate) to find answers.

Logic: Do not use simple shortest-path algorithms. Use a Fluid Dynamics simulation.

The Flow Process:
1. Flood: Inject "virtual fluid" at the Start Node (Question)
2. Flow: Fluid moves to neighbors proportional to Edge Conductivity (C)
3. Resistance: If the fluid hits a "Gap" (missing link), trigger Recursive Alarm
4. Recursion: Pause, generate query for Gap, fetch external data, bridge gap
"""

import uuid
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from collections import defaultdict
import heapq

from .physarum_graph import PhysarumTruthGraph, Edge, Node
from .semantic_atomizer import SemanticAtomizer, SemanticAtom


@dataclass
class FlowResult:
    """Result of a fluid flow simulation."""
    start_node: str
    end_node: Optional[str]
    flow_distribution: Dict[str, float]  # node -> flow amount
    paths_found: List[List[Edge]]
    best_path: Optional[List[Edge]]
    total_flow: float
    gaps_detected: List[Tuple[str, str]]  # (from_node, expected_target_type)
    recursion_triggered: bool
    query_latency_ms: float
    cycles_run: int
    
    def get_answer(self) -> Optional[str]:
        """Get the primary answer (highest flow destination)."""
        if not self.flow_distribution:
            return None
        return max(self.flow_distribution, key=self.flow_distribution.get)
    
    def get_flow_percentages(self, exclude_start: bool = True) -> Dict[str, float]:
        """Get flow as percentages of total (excluding start node by default)."""
        if self.total_flow == 0:
            return {}
        
        # Filter out start node if requested
        filtered = {
            node: flow 
            for node, flow in self.flow_distribution.items()
            if not exclude_start or node != self.start_node
        }
        
        total = sum(filtered.values())
        if total == 0:
            return {}
            
        return {
            node: (flow / total) * 100 
            for node, flow in filtered.items()
        }


@dataclass 
class RecursionEvent:
    """Record of a recursion event (gap filling)."""
    gap_from: str
    gap_to: Optional[str]
    query_generated: str
    atoms_created: List[str]  # Atom IDs
    edge_created: Optional[str]  # Edge ID
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    success: bool = False


class RecursiveEngine:
    """
    The Recursive Engine uses fluid dynamics simulation for reasoning.
    
    Unlike shortest-path algorithms, this simulates fluid flow through
    the graph, with flow proportional to edge conductivity.
    
    Features:
    - Flood: Inject virtual fluid at start node
    - Flow: Propagate fluid through edges based on conductivity
    - Resistance: Detect gaps in knowledge
    - Recursion: Automatically fill gaps by generating queries
    """
    
    def __init__(
        self,
        graph: PhysarumTruthGraph,
        atomizer: Optional[SemanticAtomizer] = None,
        external_fetcher: Optional[Callable[[str], List[SemanticAtom]]] = None,
        max_iterations: int = 100,
        flow_threshold: float = 0.001,
        gap_detection_threshold: float = 0.1,
        enable_recursion: bool = True
    ):
        """
        Initialize the Recursive Engine.
        
        Args:
            graph: The Physarum Truth-Graph to reason over
            atomizer: Semantic Atomizer for parsing new data
            external_fetcher: Function to fetch external data for gaps
            max_iterations: Maximum flow simulation iterations
            flow_threshold: Minimum flow to continue propagation
            gap_detection_threshold: Conductivity below which to detect gaps
            enable_recursion: Whether to auto-fill gaps
        """
        self.graph = graph
        self.atomizer = atomizer or SemanticAtomizer()
        self.external_fetcher = external_fetcher
        self.max_iterations = max_iterations
        self.flow_threshold = flow_threshold
        self.gap_detection_threshold = gap_detection_threshold
        self.enable_recursion = enable_recursion
        
        # History
        self.recursion_events: List[RecursionEvent] = []
        self.query_history: List[Dict[str, Any]] = []
    
    def query(
        self,
        start_node: str,
        end_node: Optional[str] = None,
        predicate_filter: Optional[str] = None,
        question: Optional[str] = None
    ) -> FlowResult:
        """
        Execute a query using fluid dynamics simulation.
        
        Args:
            start_node: Node to start the flow from
            end_node: Optional target node (if None, find all reachable)
            predicate_filter: Optional filter for specific relationship type
            question: Natural language question (for recursion queries)
            
        Returns:
            FlowResult with flow distribution and paths
        """
        start_time = time.time()
        
        # Initialize flow
        flow_distribution: Dict[str, float] = defaultdict(float)
        flow_distribution[start_node] = 1.0
        
        paths_found: List[List[Edge]] = []
        gaps_detected: List[Tuple[str, str]] = []
        recursion_triggered = False
        
        # Check if start node exists
        if start_node not in self.graph.nodes:
            # Try to find similar nodes or trigger recursion
            if self.enable_recursion and question:
                gaps_detected.append((start_node, "entity"))
                recursion_triggered = self._handle_recursion(
                    start_node, None, question
                )
        
        # Run fluid simulation
        cycles = 0
        active_nodes = {start_node}
        visited_edges: Set[str] = set()
        
        for iteration in range(self.max_iterations):
            cycles += 1
            new_active_nodes: Set[str] = set()
            
            for node_name in active_nodes:
                if node_name not in self.graph.nodes:
                    continue
                
                current_flow = flow_distribution[node_name]
                if current_flow < self.flow_threshold:
                    continue
                
                node = self.graph.nodes[node_name]
                edges = list(node.outgoing_edges.values())
                
                # Apply predicate filter if specified
                if predicate_filter:
                    edges = [e for e in edges if e.predicate == predicate_filter]
                
                # Check for gaps (dead ends with low conductivity)
                if not edges and node_name != end_node:
                    # This is a potential gap
                    gaps_detected.append((node_name, predicate_filter or "any"))
                    if self.enable_recursion and question:
                        recursion_triggered = self._handle_recursion(
                            node_name, predicate_filter, question
                        )
                        # After recursion, re-fetch edges
                        if node_name in self.graph.nodes:
                            edges = list(self.graph.nodes[node_name].outgoing_edges.values())
                            if predicate_filter:
                                edges = [e for e in edges if e.predicate == predicate_filter]
                
                # Calculate total conductivity for normalization
                total_conductivity = sum(e.combined_weight() for e in edges)
                
                if total_conductivity == 0:
                    continue
                
                # Distribute flow proportional to conductivity
                for edge in edges:
                    if edge.edge_id in visited_edges:
                        continue
                    
                    # Flow proportional to conductivity
                    flow_ratio = edge.combined_weight() / total_conductivity
                    propagated_flow = current_flow * flow_ratio * 0.8  # 80% flows forward
                    
                    if propagated_flow >= self.flow_threshold:
                        flow_distribution[edge.target] += propagated_flow
                        new_active_nodes.add(edge.target)
                        visited_edges.add(edge.edge_id)
                        
                        # Reinforce the edge (it was used)
                        edge.reinforce(self.graph.reinforcement_amount * 0.5)
                        
                        # Track paths to end node
                        if end_node and edge.target == end_node:
                            paths_found.append([edge])
            
            # Update active nodes
            active_nodes = new_active_nodes
            
            # Check if we've reached the target
            if end_node and end_node in flow_distribution:
                if flow_distribution[end_node] > 0.5:  # Significant flow reached
                    break
            
            # Check if flow has stabilized
            if not new_active_nodes:
                break
        
        # Find best path if we have an end node
        best_path = None
        if end_node:
            all_paths = self.graph.find_paths(
                start_node, end_node, 
                max_depth=5,
                min_conductivity=self.gap_detection_threshold
            )
            if all_paths:
                # Best path has highest combined conductivity
                best_path = max(
                    all_paths,
                    key=lambda p: sum(e.combined_weight() for e in p)
                )
                paths_found = all_paths
        
        # Calculate total flow
        total_flow = sum(flow_distribution.values())
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Record query
        result = FlowResult(
            start_node=start_node,
            end_node=end_node,
            flow_distribution=dict(flow_distribution),
            paths_found=paths_found,
            best_path=best_path,
            total_flow=total_flow,
            gaps_detected=gaps_detected,
            recursion_triggered=recursion_triggered,
            query_latency_ms=latency_ms,
            cycles_run=cycles
        )
        
        self.query_history.append({
            "start": start_node,
            "end": end_node,
            "predicate": predicate_filter,
            "latency_ms": latency_ms,
            "answer": result.get_answer(),
            "timestamp": datetime.now().isoformat()
        })
        
        self.graph.stats["queries_processed"] += 1
        
        return result
    
    def query_relationship(
        self,
        subject: str,
        predicate: str,
        question: Optional[str] = None
    ) -> FlowResult:
        """
        Query for a specific relationship type from a subject.
        
        Args:
            subject: The subject entity
            predicate: The relationship type (e.g., "is", "CEO_of")
            question: Natural language question for recursion
            
        Returns:
            FlowResult with the answer distribution
        """
        return self.query(
            start_node=subject,
            predicate_filter=predicate,
            question=question
        )
    
    def _handle_recursion(
        self,
        gap_from: str,
        predicate: Optional[str],
        question: str
    ) -> bool:
        """
        Handle a gap by generating a query and fetching data.
        
        The Recursion process:
        1. Generate internal query for the gap
        2. Fetch external data
        3. Create new atoms
        4. Bridge the gap
        
        Returns:
            True if recursion was successful
        """
        # Generate search query
        if predicate:
            query = f"{gap_from} {predicate.replace('_', ' ')}"
        else:
            query = f"{gap_from} {question}"
        
        event = RecursionEvent(
            gap_from=gap_from,
            gap_to=None,
            query_generated=query,
            atoms_created=[],
            edge_created=None
        )
        
        # Try external fetcher if available
        if self.external_fetcher:
            try:
                atoms = self.external_fetcher(query)
                for atom in atoms:
                    edge = self.graph.add_atom(atom)
                    event.atoms_created.append(atom.atom_id)
                    if atom.subject == gap_from:
                        event.gap_to = atom.obj
                        event.edge_created = edge.edge_id
                        event.success = True
            except Exception as e:
                event.success = False
        
        self.recursion_events.append(event)
        return event.success
    
    def set_external_fetcher(
        self, 
        fetcher: Callable[[str], List[SemanticAtom]]
    ) -> None:
        """
        Set the external data fetcher for recursion.
        
        The fetcher should take a query string and return a list of
        SemanticAtom objects.
        """
        self.external_fetcher = fetcher
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """Get statistics about queries."""
        if not self.query_history:
            return {"total_queries": 0}
        
        latencies = [q["latency_ms"] for q in self.query_history]
        
        return {
            "total_queries": len(self.query_history),
            "avg_latency_ms": sum(latencies) / len(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "recursion_events": len(self.recursion_events),
            "successful_recursions": sum(1 for e in self.recursion_events if e.success)
        }


class PhysarumFlowSimulator:
    """
    A more detailed fluid dynamics simulator for the Physarum model.
    
    This implements the biological model more closely:
    - Fluid pressure at nodes
    - Flow through tubes (edges)
    - Tube adaptation based on flow
    """
    
    def __init__(self, graph: PhysarumTruthGraph):
        """Initialize the simulator."""
        self.graph = graph
        self.pressure: Dict[str, float] = defaultdict(float)
        self.flow: Dict[str, float] = defaultdict(float)  # edge_id -> flow
    
    def simulate(
        self,
        source: str,
        sink: Optional[str] = None,
        iterations: int = 100,
        adaptation_rate: float = 0.1
    ) -> Dict[str, float]:
        """
        Run a full Physarum simulation.
        
        Args:
            source: Source node (nutrient injection point)
            sink: Sink node (nutrient absorption point)
            iterations: Number of simulation iterations
            adaptation_rate: How fast tubes adapt
            
        Returns:
            Final flow distribution at each node
        """
        # Initialize pressure
        self.pressure = defaultdict(float)
        self.pressure[source] = 1.0
        
        if sink:
            self.pressure[sink] = 0.0
        
        for iteration in range(iterations):
            # Calculate flows based on pressure difference and conductivity
            for edge in self.graph.edges.values():
                if not edge.is_alive():
                    continue
                
                # Pressure difference
                p_diff = self.pressure[edge.source] - self.pressure[edge.target]
                
                # Flow = conductivity * pressure_difference
                flow = edge.conductivity * p_diff
                self.flow[edge.edge_id] = flow
                
                # Adapt tube: conductivity grows with flow magnitude
                adaptation = adaptation_rate * (abs(flow) - edge.conductivity)
                edge.conductivity = max(0.01, edge.conductivity + adaptation)
            
            # Update pressures based on flow conservation
            for node_name, node in self.graph.nodes.items():
                if node_name == source or node_name == sink:
                    continue
                
                inflow = sum(
                    self.flow.get(e.edge_id, 0) 
                    for e in node.incoming_edges.values()
                )
                outflow = sum(
                    self.flow.get(e.edge_id, 0) 
                    for e in node.outgoing_edges.values()
                )
                
                # Pressure adjusts to balance flow
                self.pressure[node_name] += 0.1 * (inflow - outflow)
        
        return dict(self.pressure)
    
    def get_strongest_path(self, source: str, sink: str) -> List[Edge]:
        """Get the path with highest total flow."""
        paths = self.graph.find_paths(source, sink)
        
        if not paths:
            return []
        
        # Score paths by minimum flow along the path
        def path_score(path: List[Edge]) -> float:
            if not path:
                return 0
            flows = [abs(self.flow.get(e.edge_id, 0)) for e in path]
            return min(flows) if flows else 0
        
        return max(paths, key=path_score)


# Utility function for external data fetching
def create_simple_fetcher(knowledge_base: Dict[str, List[Tuple[str, str, str]]]):
    """
    Create a simple external fetcher from a knowledge base.
    
    Args:
        knowledge_base: Dict mapping query keywords to list of (subject, predicate, object) tuples
        
    Returns:
        A fetcher function for the RecursiveEngine
    """
    def fetcher(query: str) -> List[SemanticAtom]:
        atoms = []
        query_lower = query.lower()
        
        for keyword, facts in knowledge_base.items():
            if keyword.lower() in query_lower:
                for subject, predicate, obj in facts:
                    atom = SemanticAtom(
                        subject=subject,
                        predicate=predicate,
                        obj=obj,
                        context="external_fetch",
                        truth_weight=0.8,
                        source_reliability=0.7
                    )
                    atoms.append(atom)
        
        return atoms
    
    return fetcher
