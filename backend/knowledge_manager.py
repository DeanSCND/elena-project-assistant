#!/usr/bin/env python3
"""
Knowledge Manager - Handles learning, storing, and retrieving user-taught knowledge
"""

import json
import os
import re
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import shutil

@dataclass
class KnowledgeEntry:
    """Represents a single piece of learned knowledge"""
    id: str
    type: str  # rule, fact, calculation, reference, correction
    trigger: str  # Original user message
    knowledge: str  # Extracted knowledge
    context: str  # Additional context
    source: str  # user_explicit, agent_detected, user_correction
    created_at: str
    tags: List[str]
    usage_count: int = 0
    confidence: float = 1.0
    examples: List[str] = None

    def __post_init__(self):
        if self.examples is None:
            self.examples = []

class KnowledgeManager:
    """Manages learned knowledge from user interactions"""

    # Learning trigger patterns (with typo tolerance)
    LEARNING_PATTERNS = [
        r"^(?:remember|remeber|rember)[,:]?\s+(.+)",  # "Remember," at start (with typos)
        r"\b(?:remember|remeber|rember)[,:]?\s+(.+)",  # "Remember," anywhere (with typos)
        r"(?:remember|remeber|rember)\s+that\s+(.+)",
        r"i want you to (?:remember|remeber|rember)\s+(.+)",
        r"learn that\s+(.+)",
        r"keep in mind that\s+(.+)",
        r"keep in mind[,:]?\s+(.+)",
        r"for future reference[,:]?\s+(.+)",
        r"always\s+(.+)",
        r"never\s+(.+)",
        r"note that\s+(.+)",
        r"don't forget\s+(.+)",
        r"you should know that\s+(.+)",
        r"important[,:]?\s+(.+)",
    ]

    # Correction patterns
    CORRECTION_PATTERNS = [
        r"actually[,]?\s+(.+)",
        r"no[,]?\s+(.+)",
        r"correction[:]?\s+(.+)",
        r"that's wrong[,]?\s+(.+)",
        r"it's actually\s+(.+)",
        r"you're wrong[,]?\s+(.+)",
    ]

    def __init__(self, storage_dir: str = None):
        """Initialize the knowledge manager"""
        if storage_dir is None:
            # Use environment variable for storage path
            # Default to /data/learned_knowledge in production, ./learned_knowledge locally
            storage_path = os.getenv('STORAGE_PATH', str(Path(__file__).parent / "learned_knowledge"))
            storage_dir = storage_path

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True, parents=True)

        # Create subdirectories
        (self.storage_dir / "backup").mkdir(exist_ok=True)
        (self.storage_dir / "exports").mkdir(exist_ok=True)

        # File paths
        self.knowledge_file = self.storage_dir / "knowledge.json"
        self.rules_file = self.storage_dir / "rules.json"
        self.calculations_file = self.storage_dir / "calculations.json"

        # In-memory storage
        self.knowledge: Dict[str, KnowledgeEntry] = {}
        self.rules: List[KnowledgeEntry] = []
        self.calculations: List[KnowledgeEntry] = []

        # Load existing knowledge
        self.load_knowledge()

    def detect_learning_intent(self, message: str) -> Tuple[bool, str]:
        """
        Detect if the user wants to teach something
        Returns (is_learning, matched_pattern)
        """
        message_lower = message.lower().strip()

        print(f"DEBUG [Learning Detection]: Checking message: '{message[:50]}...'")

        for pattern in self.LEARNING_PATTERNS:
            match = re.search(pattern, message_lower, re.IGNORECASE)
            if match:
                print(f"DEBUG [Learning Detection]: ✓ MATCHED pattern: {pattern}")
                print(f"DEBUG [Learning Detection]: Matched text: '{match.group(0)}'")
                return True, match.group(0)

        print(f"DEBUG [Learning Detection]: ✗ No learning pattern matched")
        return False, ""

    def detect_correction(self, message: str) -> Tuple[bool, str]:
        """
        Detect if the user is correcting the agent
        Returns (is_correction, matched_pattern)
        """
        message_lower = message.lower().strip()

        for pattern in self.CORRECTION_PATTERNS:
            match = re.search(pattern, message_lower, re.IGNORECASE)
            if match:
                return True, match.group(0)

        return False, ""

    def extract_knowledge(self, message: str, trigger_pattern: str = None) -> KnowledgeEntry:
        """Extract knowledge from user message"""

        # Determine the type based on content
        knowledge_type = self._determine_type(message)

        # Extract the core knowledge
        if trigger_pattern:
            # Remove the trigger phrase to get the knowledge
            knowledge_text = message
            for pattern in self.LEARNING_PATTERNS:
                knowledge_text = re.sub(pattern, r"\1", knowledge_text, flags=re.IGNORECASE)
                if knowledge_text != message:
                    break
        else:
            knowledge_text = message

        # Extract tags from content
        tags = self._extract_tags(knowledge_text)

        # Determine source
        source = "user_explicit"
        if any(word in message.lower() for word in ["actually", "correction", "wrong"]):
            source = "user_correction"

        # Create knowledge entry
        entry = KnowledgeEntry(
            id=str(uuid.uuid4()),
            type=knowledge_type,
            trigger=message,
            knowledge=knowledge_text.strip(),
            context="Aurora Construction Project",
            source=source,
            created_at=datetime.now().isoformat(),
            tags=tags,
            usage_count=0,
            confidence=1.0
        )

        return entry

    def _determine_type(self, message: str) -> str:
        """Determine the type of knowledge"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["always", "never", "must", "should", "require"]):
            return "rule"
        elif any(word in message_lower for word in ["calculate", "formula", "equation", "+", "-", "*", "/", "="]):
            return "calculation"
        elif any(word in message_lower for word in ["reference", "see", "relates to", "connects"]):
            return "reference"
        elif any(word in message_lower for word in ["actually", "correction", "wrong"]):
            return "correction"
        else:
            return "fact"

    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from text"""
        tags = []
        text_lower = text.lower()

        # Construction-specific keywords
        keywords = [
            "trellis", "hvac", "ceiling", "clearance", "dimension", "height",
            "width", "length", "grid", "beam", "support", "bracket", "mounting",
            "specification", "drawing", "calculation", "material", "safeway",
            "aurora", "regina", "shop drawing", "rcp", "conflict"
        ]

        for keyword in keywords:
            if keyword in text_lower:
                tags.append(keyword)

        # Extract document references (e.g., SAF-TRE-001)
        doc_patterns = re.findall(r'SAF-[A-Z]{3}-\d{3}', text, re.IGNORECASE)
        tags.extend([doc.upper() for doc in doc_patterns])

        return list(set(tags))  # Remove duplicates

    def save_knowledge(self, entry: KnowledgeEntry) -> bool:
        """Save knowledge entry to storage"""
        try:
            # Add to in-memory storage
            self.knowledge[entry.id] = entry

            # Add to specialized lists
            if entry.type == "rule":
                self.rules.append(entry)
            elif entry.type == "calculation":
                self.calculations.append(entry)

            # Backup existing file
            if self.knowledge_file.exists():
                backup_file = self.storage_dir / "backup" / f"knowledge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                shutil.copy(self.knowledge_file, backup_file)

            # Save to file
            self._save_to_file()

            return True
        except Exception as e:
            print(f"Error saving knowledge: {e}")
            return False

    def _save_to_file(self):
        """Save all knowledge to JSON files"""
        # Save main knowledge base
        knowledge_data = {
            entry_id: asdict(entry) for entry_id, entry in self.knowledge.items()
        }
        with open(self.knowledge_file, 'w') as f:
            json.dump(knowledge_data, f, indent=2)

        # Save rules
        rules_data = [asdict(rule) for rule in self.rules]
        with open(self.rules_file, 'w') as f:
            json.dump(rules_data, f, indent=2)

        # Save calculations
        calc_data = [asdict(calc) for calc in self.calculations]
        with open(self.calculations_file, 'w') as f:
            json.dump(calc_data, f, indent=2)

    def load_knowledge(self):
        """Load knowledge from storage"""
        try:
            # Load main knowledge base
            if self.knowledge_file.exists():
                with open(self.knowledge_file, 'r') as f:
                    knowledge_data = json.load(f)

                for entry_id, entry_data in knowledge_data.items():
                    entry = KnowledgeEntry(**entry_data)
                    self.knowledge[entry_id] = entry

                    # Populate specialized lists
                    if entry.type == "rule":
                        self.rules.append(entry)
                    elif entry.type == "calculation":
                        self.calculations.append(entry)

                print(f"Loaded {len(self.knowledge)} knowledge entries")
        except Exception as e:
            print(f"Error loading knowledge: {e}")

    def get_relevant_knowledge(self, query: str, max_items: int = 5) -> List[KnowledgeEntry]:
        """Get knowledge relevant to a query"""
        query_lower = query.lower()
        relevant = []

        # Score each entry based on relevance
        scored_entries = []
        for entry in self.knowledge.values():
            score = 0

            # Check if any tags match
            for tag in entry.tags:
                if tag.lower() in query_lower:
                    score += 2

            # Check if knowledge text is relevant
            knowledge_words = entry.knowledge.lower().split()
            query_words = query_lower.split()
            matching_words = set(knowledge_words) & set(query_words)
            score += len(matching_words)

            # Boost rules and recent entries
            if entry.type == "rule":
                score += 1

            # Boost frequently used entries
            score += entry.usage_count * 0.5

            if score > 0:
                scored_entries.append((score, entry))

        # Sort by score and return top entries
        scored_entries.sort(key=lambda x: x[0], reverse=True)
        relevant = [entry for _, entry in scored_entries[:max_items]]

        # Update usage count
        for entry in relevant:
            entry.usage_count += 1

        return relevant

    def format_for_prompt(self, entries: List[KnowledgeEntry]) -> str:
        """Format knowledge entries for inclusion in prompts"""
        if not entries:
            return ""

        formatted = "## Learned Knowledge:\n"

        # Group by type
        by_type = defaultdict(list)
        for entry in entries:
            by_type[entry.type].append(entry)

        # Format each type
        type_labels = {
            "rule": "📋 Rules",
            "fact": "📌 Facts",
            "calculation": "🔢 Calculations",
            "reference": "🔗 References",
            "correction": "✏️ Corrections"
        }

        for type_key, type_entries in by_type.items():
            label = type_labels.get(type_key, type_key.title())
            formatted += f"\n### {label}:\n"
            for entry in type_entries:
                formatted += f"- {entry.knowledge}\n"
                if entry.examples:
                    formatted += f"  Examples: {', '.join(entry.examples)}\n"

        return formatted

    def update_entry(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing knowledge entry"""
        if entry_id not in self.knowledge:
            return False

        entry = self.knowledge[entry_id]
        for key, value in updates.items():
            if hasattr(entry, key):
                setattr(entry, key, value)

        self._save_to_file()
        return True

    def delete_entry(self, entry_id: str) -> bool:
        """Delete a knowledge entry"""
        if entry_id not in self.knowledge:
            return False

        entry = self.knowledge[entry_id]

        # Remove from specialized lists
        if entry in self.rules:
            self.rules.remove(entry)
        if entry in self.calculations:
            self.calculations.remove(entry)

        # Remove from main storage
        del self.knowledge[entry_id]

        self._save_to_file()
        return True

    def export_knowledge(self, filename: str = None) -> str:
        """Export knowledge to a file for sharing"""
        if filename is None:
            filename = f"knowledge_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        export_path = self.storage_dir / "exports" / filename

        export_data = {
            "exported_at": datetime.now().isoformat(),
            "entry_count": len(self.knowledge),
            "knowledge": {
                entry_id: asdict(entry) for entry_id, entry in self.knowledge.items()
            }
        }

        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        return str(export_path)

    def import_knowledge(self, filepath: str, merge: bool = True) -> int:
        """Import knowledge from a file"""
        try:
            with open(filepath, 'r') as f:
                import_data = json.load(f)

            imported_count = 0
            knowledge_data = import_data.get("knowledge", {})

            for entry_id, entry_data in knowledge_data.items():
                if not merge and entry_id in self.knowledge:
                    continue  # Skip existing entries if not merging

                entry = KnowledgeEntry(**entry_data)
                self.knowledge[entry_id] = entry

                # Add to specialized lists
                if entry.type == "rule" and entry not in self.rules:
                    self.rules.append(entry)
                elif entry.type == "calculation" and entry not in self.calculations:
                    self.calculations.append(entry)

                imported_count += 1

            self._save_to_file()
            return imported_count

        except Exception as e:
            print(f"Error importing knowledge: {e}")
            return 0

    def get_all_knowledge(self) -> Dict[str, List[KnowledgeEntry]]:
        """Get all knowledge organized by type"""
        organized = defaultdict(list)
        for entry in self.knowledge.values():
            organized[entry.type].append(entry)
        return dict(organized)

    def search_knowledge(self, query: str) -> List[KnowledgeEntry]:
        """Search knowledge by text"""
        query_lower = query.lower()
        results = []

        for entry in self.knowledge.values():
            if (query_lower in entry.knowledge.lower() or
                query_lower in entry.trigger.lower() or
                any(query_lower in tag.lower() for tag in entry.tags)):
                results.append(entry)

        return results

# Singleton instance
_knowledge_manager_instance = None

def get_knowledge_manager(storage_dir: str = None) -> KnowledgeManager:
    """Get or create the singleton knowledge manager instance"""
    global _knowledge_manager_instance
    if _knowledge_manager_instance is None:
        _knowledge_manager_instance = KnowledgeManager(storage_dir)
    return _knowledge_manager_instance