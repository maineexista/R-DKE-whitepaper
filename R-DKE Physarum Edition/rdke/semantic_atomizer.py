"""
Module A: The Semantic Atomizer (Input Layer)
==============================================

Goal: Do not store raw text. Store "Atoms of Meaning."

Instead of chunking text by character count, the system parses 
input into Semantic Atoms with Subject-Predicate-Object structure.
"""

import uuid
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple


@dataclass
class SemanticAtom:
    """
    A Semantic Atom represents an atomic unit of meaning.
    
    Data Structure (from whitepaper):
    {
      "Atom_ID": "UUID",
      "Subject": "Entity (e.g., Apple_Inc)",
      "Predicate": "Action (e.g., decreased_revenue)",
      "Object": "Target (e.g., 5_percent)",
      "Context": "Q3_Earnings_Report",
      "Truth_Weight": 1.0,  // Initial confidence
      "Source_Reliability": 0.9, // Weight of the source
      "Timestamp": "ISO_DATE"
    }
    """
    subject: str
    predicate: str
    obj: str  # 'object' is reserved in Python
    context: str = ""
    truth_weight: float = 1.0
    source_reliability: float = 0.5
    atom_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert atom to dictionary format."""
        return {
            "Atom_ID": self.atom_id,
            "Subject": self.subject,
            "Predicate": self.predicate,
            "Object": self.obj,
            "Context": self.context,
            "Truth_Weight": self.truth_weight,
            "Source_Reliability": self.source_reliability,
            "Timestamp": self.timestamp
        }
    
    def to_json(self) -> str:
        """Convert atom to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SemanticAtom":
        """Create atom from dictionary."""
        return cls(
            atom_id=data.get("Atom_ID", str(uuid.uuid4())),
            subject=data["Subject"],
            predicate=data["Predicate"],
            obj=data["Object"],
            context=data.get("Context", ""),
            truth_weight=data.get("Truth_Weight", 1.0),
            source_reliability=data.get("Source_Reliability", 0.5),
            timestamp=data.get("Timestamp", datetime.now().isoformat())
        )
    
    def combined_weight(self) -> float:
        """Calculate combined weight from truth and source reliability."""
        return self.truth_weight * self.source_reliability
    
    def __repr__(self) -> str:
        return f"Atom({self.subject} --[{self.predicate}]--> {self.obj}, weight={self.combined_weight():.2f})"


class SemanticAtomizer:
    """
    The Semantic Atomizer parses natural language into Semantic Atoms.
    
    This is a rule-based parser. In production, you would use a small,
    fast LLM (like Llama-3-8B) as the parser to convert natural language
    into the JSON structure.
    """
    
    # Common relationship patterns for extraction
    RELATION_PATTERNS = [
        # "X is Y" pattern
        (r"(?:the\s+)?(\w+(?:\s+\w+)?)\s+(?:is|are)\s+(\w+(?:\s+\w+)?)", "is"),
        # "X has Y" pattern
        (r"(?:the\s+)?(\w+(?:\s+\w+)?)\s+(?:has|have)\s+(\w+(?:\s+\w+)?)", "has"),
        # "X founded Y" pattern
        (r"(\w+(?:\s+\w+)?)\s+founded\s+(\w+(?:\s+\w+)?)", "founded"),
        # "X CEO of Y" pattern
        (r"(\w+(?:\s+\w+)?)\s+(?:is\s+)?(?:the\s+)?CEO\s+of\s+(\w+(?:\s+\w+)?)", "is_CEO_of"),
        # "X works at Y" pattern
        (r"(\w+(?:\s+\w+)?)\s+works?\s+(?:at|for)\s+(\w+(?:\s+\w+)?)", "works_at"),
        # "X decreased Y" pattern
        (r"(\w+(?:\s+\w+)?)\s+decreased\s+(\w+(?:\s+\w+)?)", "decreased"),
        # "X increased Y" pattern
        (r"(\w+(?:\s+\w+)?)\s+increased\s+(\w+(?:\s+\w+)?)", "increased"),
    ]
    
    def __init__(self, default_source_reliability: float = 0.5):
        """
        Initialize the Semantic Atomizer.
        
        Args:
            default_source_reliability: Default reliability score for parsed atoms
        """
        self.default_source_reliability = default_source_reliability
        self._atom_cache: List[SemanticAtom] = []
    
    def parse_text(
        self, 
        text: str, 
        context: str = "",
        source_reliability: Optional[float] = None
    ) -> List[SemanticAtom]:
        """
        Parse natural language text into Semantic Atoms.
        
        Args:
            text: The natural language text to parse
            context: Optional context label for the atoms
            source_reliability: Reliability score of the source (0.0 to 1.0)
            
        Returns:
            List of SemanticAtom objects extracted from the text
        """
        reliability = source_reliability or self.default_source_reliability
        atoms = []
        
        # Try each pattern
        for pattern, predicate in self.RELATION_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                subject = self._normalize_entity(match.group(1))
                obj = self._normalize_entity(match.group(2))
                
                atom = SemanticAtom(
                    subject=subject,
                    predicate=predicate,
                    obj=obj,
                    context=context,
                    truth_weight=1.0,
                    source_reliability=reliability
                )
                atoms.append(atom)
        
        # If no patterns matched, try simple Subject-Predicate-Object extraction
        if not atoms:
            atoms = self._fallback_parse(text, context, reliability)
        
        self._atom_cache.extend(atoms)
        return atoms
    
    def parse_triple(
        self,
        subject: str,
        predicate: str,
        obj: str,
        context: str = "",
        truth_weight: float = 1.0,
        source_reliability: Optional[float] = None
    ) -> SemanticAtom:
        """
        Create a Semantic Atom directly from a triple.
        
        Args:
            subject: The subject entity
            predicate: The relationship/action
            obj: The object entity
            context: Optional context label
            truth_weight: Initial truth confidence (0.0 to 1.0)
            source_reliability: Reliability of the source (0.0 to 1.0)
            
        Returns:
            A SemanticAtom object
        """
        reliability = source_reliability or self.default_source_reliability
        
        atom = SemanticAtom(
            subject=self._normalize_entity(subject),
            predicate=self._normalize_predicate(predicate),
            obj=self._normalize_entity(obj),
            context=context,
            truth_weight=truth_weight,
            source_reliability=reliability
        )
        
        self._atom_cache.append(atom)
        return atom
    
    def parse_json(self, json_str: str) -> SemanticAtom:
        """
        Parse a JSON string into a Semantic Atom.
        
        Args:
            json_str: JSON string in the atom format
            
        Returns:
            A SemanticAtom object
        """
        data = json.loads(json_str)
        atom = SemanticAtom.from_dict(data)
        self._atom_cache.append(atom)
        return atom
    
    def _normalize_entity(self, entity: str) -> str:
        """Normalize entity names for consistency."""
        # Remove extra whitespace and convert to title case
        entity = " ".join(entity.split())
        # Replace spaces with underscores for graph storage
        entity = entity.replace(" ", "_")
        return entity
    
    def _normalize_predicate(self, predicate: str) -> str:
        """Normalize predicate names for consistency."""
        predicate = predicate.lower().strip()
        predicate = predicate.replace(" ", "_")
        return predicate
    
    def _fallback_parse(
        self, 
        text: str, 
        context: str, 
        reliability: float
    ) -> List[SemanticAtom]:
        """
        Fallback parsing for when patterns don't match.
        Attempts basic Subject-Verb-Object extraction.
        """
        atoms = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]', text)
        
        for sentence in sentences:
            words = sentence.strip().split()
            if len(words) >= 3:
                # Very basic SVO extraction (first word = subject, second = predicate, rest = object)
                subject = self._normalize_entity(words[0])
                predicate = self._normalize_predicate(words[1])
                obj = self._normalize_entity(" ".join(words[2:]))
                
                atom = SemanticAtom(
                    subject=subject,
                    predicate=predicate,
                    obj=obj,
                    context=context,
                    truth_weight=0.5,  # Lower confidence for fallback parsing
                    source_reliability=reliability
                )
                atoms.append(atom)
        
        return atoms
    
    def get_cached_atoms(self) -> List[SemanticAtom]:
        """Return all cached atoms."""
        return self._atom_cache.copy()
    
    def clear_cache(self) -> None:
        """Clear the atom cache."""
        self._atom_cache.clear()
    
    def export_atoms_json(self) -> str:
        """Export all cached atoms as JSON."""
        return json.dumps([atom.to_dict() for atom in self._atom_cache], indent=2)


# Example LLM parser interface (for production use)
class LLMAtomizer:
    """
    Production-grade atomizer using an LLM for parsing.
    
    Developer Note from whitepaper: Use a small, fast LLM (like Llama-3-8B) 
    strictly as a parser to convert natural language into the JSON structure 
    before entering the graph.
    
    This is a placeholder interface - implement with your LLM of choice.
    """
    
    SYSTEM_PROMPT = """You are a semantic parser. Convert the input text into 
    one or more Semantic Atoms. Each atom must have this JSON structure:
    
    {
      "Subject": "Entity name",
      "Predicate": "Action or relationship",
      "Object": "Target entity or value",
      "Context": "Optional context"
    }
    
    Return a JSON array of atoms. Extract ALL meaningful relationships.
    Be precise and atomic - one relationship per atom."""
    
    def __init__(self, llm_client=None):
        """
        Initialize with an LLM client.
        
        Args:
            llm_client: An LLM client with a .generate() method
        """
        self.llm_client = llm_client
    
    def parse(
        self, 
        text: str, 
        source_reliability: float = 0.5
    ) -> List[SemanticAtom]:
        """
        Parse text using LLM.
        
        Args:
            text: Natural language text to parse
            source_reliability: Reliability score for the source
            
        Returns:
            List of SemanticAtom objects
        """
        if self.llm_client is None:
            raise ValueError("LLM client not configured. Use SemanticAtomizer for rule-based parsing.")
        
        # This would call the LLM in production
        # response = self.llm_client.generate(
        #     system=self.SYSTEM_PROMPT,
        #     user=text
        # )
        # atoms_data = json.loads(response)
        # return [SemanticAtom.from_dict(a) for a in atoms_data]
        
        raise NotImplementedError("Configure llm_client for LLM-based parsing")
