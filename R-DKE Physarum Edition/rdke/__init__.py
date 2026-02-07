"""
R-DKE (Recursive Deep Knowledge Engine) - Physarum Edition
============================================================

A biologically-inspired knowledge engine using Physarum polycephalum 
(slime mold) principles for adaptive truth-seeking.

Modules:
    - semantic_atomizer: Parse text into Semantic Atoms
    - physarum_graph: Living Truth-Graph with physics-based edges
    - recursive_engine: Fluid dynamics reasoning with recursion
"""

__version__ = "2.0.0"
__author__ = "Based on R-DKE Whitepaper by Marius Gherasim"

from .semantic_atomizer import SemanticAtomizer, SemanticAtom
from .physarum_graph import PhysarumTruthGraph, Edge
from .recursive_engine import RecursiveEngine, FlowResult

__all__ = [
    "SemanticAtomizer",
    "SemanticAtom", 
    "PhysarumTruthGraph",
    "Edge",
    "RecursiveEngine",
    "FlowResult",
]
