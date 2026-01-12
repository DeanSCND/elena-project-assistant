#!/usr/bin/env python3
"""
Enhanced Construction Agent with Deep Analysis
Implements multi-step reasoning, document comprehension, and re-analysis capabilities
"""

import os
import json
import asyncio
from pathlib import Path
from typing import AsyncGenerator, List, Dict, Any, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict
import re
import uuid
from enum import Enum
from dotenv import load_dotenv
import base64
from io import BytesIO

from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import tempfile
import httpx
from PIL import Image

from openai import AsyncOpenAI

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize FastAPI app
app = FastAPI(title="Enhanced Construction Agent")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Enhanced data structures for document analysis
@dataclass
class DrawingReference:
    """Represents a reference to a drawing or document"""
    doc_id: str
    title: str
    revision: str
    date: str
    content_hash: str

@dataclass
class Dimension:
    """Represents a dimensional measurement"""
    value: float
    unit: str
    description: str
    location: str  # Grid reference or area
    source: DrawingReference

@dataclass
class Component:
    """Represents a construction component"""
    component_id: str
    name: str
    type: str
    material: str
    dimensions: Dict[str, Dimension]
    quantity: int
    location: str
    source: DrawingReference
    related_components: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)

@dataclass
class AnalysisResult:
    """Result of document analysis"""
    components: Dict[str, Component]
    dimensions: List[Dimension]
    conflicts: List[Dict[str, Any]]
    patterns: List[Dict[str, Any]]
    summary: str
    confidence: float

class KnowledgeGraph:
    """Knowledge graph for document relationships and reasoning"""

    def __init__(self):
        self.components = {}  # component_id -> Component
        self.dimensions = defaultdict(list)  # location -> [Dimension]
        self.relationships = defaultdict(set)  # component_id -> {related_ids}
        self.conflicts = []
        self.patterns = []
        self.documents = {}  # doc_id -> DrawingReference
        self.raw_content = {}  # doc_id -> raw text/data
        self.images = {}  # image_path -> PIL Image

    def add_component(self, component: Component):
        """Add a component to the knowledge graph"""
        self.components[component.component_id] = component
        for related_id in component.related_components:
            self.relationships[component.component_id].add(related_id)
            self.relationships[related_id].add(component.component_id)

    def find_similar_components(self, target: Component, threshold: float = 0.9) -> List[Component]:
        """Find components with similar dimensions"""
        similar = []
        for comp_id, comp in self.components.items():
            if comp_id == target.component_id:
                continue

            # Compare dimensions
            similarity = self._calculate_dimension_similarity(target, comp)
            if similarity >= threshold:
                similar.append(comp)

        return sorted(similar, key=lambda c: self._calculate_dimension_similarity(target, c), reverse=True)

    def _calculate_dimension_similarity(self, comp1: Component, comp2: Component) -> float:
        """Calculate dimensional similarity between components"""
        if not comp1.dimensions or not comp2.dimensions:
            return 0.0

        common_dims = set(comp1.dimensions.keys()) & set(comp2.dimensions.keys())
        if not common_dims:
            return 0.0

        total_similarity = 0.0
        for dim_key in common_dims:
            dim1 = comp1.dimensions[dim_key]
            dim2 = comp2.dimensions[dim_key]

            if dim1.unit == dim2.unit and dim1.value > 0 and dim2.value > 0:
                # Calculate relative difference
                diff = abs(dim1.value - dim2.value) / max(dim1.value, dim2.value)
                similarity = 1.0 - diff
                total_similarity += max(0, similarity)

        return total_similarity / len(common_dims)

    def identify_base_components(self, variation_key: str = "length") -> Dict[str, List[Component]]:
        """Identify base components that vary only in specific dimension"""
        base_groups = defaultdict(list)

        # Group components by type and constant dimensions
        for comp in self.components.values():
            if variation_key not in comp.dimensions:
                continue

            # Create a signature from non-varying dimensions
            signature_parts = []
            for dim_key, dim in comp.dimensions.items():
                if dim_key != variation_key:
                    signature_parts.append(f"{dim_key}:{dim.value}{dim.unit}")

            signature = f"{comp.type}|{comp.material}|{'|'.join(sorted(signature_parts))}"
            base_groups[signature].append(comp)

        # Filter to only groups with multiple variations
        return {sig: comps for sig, comps in base_groups.items() if len(comps) > 1}

    def analyze_patterns(self):
        """Analyze patterns in the component data"""
        patterns = []

        # Pattern 1: Identify base components
        base_components = self.identify_base_components()
        for signature, components in base_components.items():
            pattern = {
                "type": "base_component_family",
                "signature": signature,
                "count": len(components),
                "variations": [c.component_id for c in components]
            }
            patterns.append(pattern)

        # Pattern 2: Identify conflict zones
        conflict_zones = defaultdict(list)
        for conflict in self.conflicts:
            if "location" in conflict:
                conflict_zones[conflict["location"]].append(conflict)

        for zone, conflicts in conflict_zones.items():
            if len(conflicts) > 1:
                pattern = {
                    "type": "conflict_zone",
                    "location": zone,
                    "conflict_count": len(conflicts),
                    "conflicts": conflicts
                }
                patterns.append(pattern)

        self.patterns = patterns
        return patterns

class DocumentAnalyzer:
    """Advanced document analyzer with multi-step reasoning"""

    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
        self.analysis_cache = {}

    async def analyze_shop_drawings(self, content: str, doc_ref: DrawingReference) -> AnalysisResult:
        """Perform deep analysis of shop drawings"""

        # Step 1: Extract structured data
        components = await self._extract_components(content, doc_ref)

        # Step 2: Identify patterns and relationships
        for comp in components.values():
            similar = self.kg.find_similar_components(comp)
            comp.related_components = [c.component_id for c in similar[:5]]

        # Step 3: Check for conflicts
        conflicts = await self._identify_conflicts(components)

        # Step 4: Analyze patterns
        patterns = self._analyze_component_patterns(components)

        # Step 5: Generate summary
        summary = await self._generate_analysis_summary(components, conflicts, patterns)

        return AnalysisResult(
            components=components,
            dimensions=[d for comp in components.values() for d in comp.dimensions.values()],
            conflicts=conflicts,
            patterns=patterns,
            summary=summary,
            confidence=0.95  # High confidence with structured extraction
        )

    async def _extract_components(self, content: str, doc_ref: DrawingReference) -> Dict[str, Component]:
        """Extract components from drawing content using LLM"""

        prompt = """Analyze this shop drawing and extract ALL components with their EXACT dimensions.

For each component, extract:
1. Component ID/Part Number
2. Name/Description
3. Type (beam, frame, support, cap, etc.)
4. Material specification
5. ALL dimensions with units (width, height, length, thickness)
6. Quantity
7. Grid location or area

Focus on identifying BASE COMPONENTS that repeat with different lengths.

Output as JSON:
{
  "components": [
    {
      "id": "...",
      "name": "...",
      "type": "...",
      "material": "...",
      "dimensions": {
        "width": {"value": 17.875, "unit": "inch", "description": "Overall width"},
        "height": {"value": 8, "unit": "inch", "description": "Overall height"},
        "length": {"value": 120, "unit": "inch", "description": "Length"}
      },
      "quantity": 1,
      "location": "Grid A-B/1-2"
    }
  ]
}

Document content:
"""

        try:
            response = await openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at reading construction shop drawings. Extract precise dimensional data."},
                    {"role": "user", "content": prompt + content[:8000]}  # Limit for token size
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=2000
            )

            data = json.loads(response.choices[0].message.content)

            # Convert to Component objects
            components = {}
            for comp_data in data.get("components", []):
                dimensions = {}
                for dim_key, dim_data in comp_data.get("dimensions", {}).items():
                    dimensions[dim_key] = Dimension(
                        value=dim_data["value"],
                        unit=dim_data["unit"],
                        description=dim_data.get("description", ""),
                        location=comp_data.get("location", ""),
                        source=doc_ref
                    )

                component = Component(
                    component_id=comp_data["id"],
                    name=comp_data["name"],
                    type=comp_data["type"],
                    material=comp_data.get("material", ""),
                    dimensions=dimensions,
                    quantity=comp_data.get("quantity", 1),
                    location=comp_data.get("location", ""),
                    source=doc_ref
                )

                components[component.component_id] = component
                self.kg.add_component(component)

            return components

        except Exception as e:
            print(f"Error extracting components: {e}")
            return {}

    async def _identify_conflicts(self, components: Dict[str, Component]) -> List[Dict[str, Any]]:
        """Identify potential conflicts between components"""
        conflicts = []

        # Check for spatial conflicts
        location_groups = defaultdict(list)
        for comp in components.values():
            if comp.location:
                location_groups[comp.location].append(comp)

        for location, comps in location_groups.items():
            if len(comps) > 1:
                # Check if components might interfere
                for i, comp1 in enumerate(comps):
                    for comp2 in comps[i+1:]:
                        if self._check_spatial_conflict(comp1, comp2):
                            conflicts.append({
                                "type": "spatial_conflict",
                                "location": location,
                                "component1": comp1.component_id,
                                "component2": comp2.component_id,
                                "description": f"Potential interference between {comp1.name} and {comp2.name}"
                            })

        return conflicts

    def _check_spatial_conflict(self, comp1: Component, comp2: Component) -> bool:
        """Check if two components might have spatial conflict"""
        # Simplified check - in real implementation would use 3D geometry
        if comp1.type == "trellis" and comp2.type == "hvac":
            return True  # Known conflict type
        return False

    def _analyze_component_patterns(self, components: Dict[str, Component]) -> List[Dict[str, Any]]:
        """Analyze patterns in component specifications"""
        patterns = []

        # Find repeating dimension patterns
        dimension_groups = defaultdict(list)
        for comp in components.values():
            for dim_key, dim in comp.dimensions.items():
                if dim_key in ["width", "height", "thickness"]:
                    dimension_groups[f"{dim_key}:{dim.value}{dim.unit}"].append(comp)

        for dim_spec, comps in dimension_groups.items():
            if len(comps) > 3:  # Significant pattern
                patterns.append({
                    "type": "common_dimension",
                    "specification": dim_spec,
                    "count": len(comps),
                    "components": [c.component_id for c in comps[:5]]  # Sample
                })

        return patterns

    async def _generate_analysis_summary(self, components: Dict[str, Component],
                                        conflicts: List[Dict], patterns: List[Dict]) -> str:
        """Generate comprehensive analysis summary"""

        base_groups = self.kg.identify_base_components()

        summary_parts = []

        # Summarize base components
        if base_groups:
            summary_parts.append(f"Identified {len(base_groups)} base component families:")
            for i, (sig, comps) in enumerate(base_groups.items(), 1):
                if i <= 5:  # Top 5
                    summary_parts.append(f"  {i}. {comps[0].type} - {len(comps)} variations")

        # Summarize conflicts
        if conflicts:
            summary_parts.append(f"\nIdentified {len(conflicts)} potential conflicts")

        # Summarize patterns
        if patterns:
            summary_parts.append(f"\nFound {len(patterns)} dimensional patterns")

        return "\n".join(summary_parts)

class ReasoningEngine:
    """Multi-step reasoning engine for complex queries"""

    def __init__(self, knowledge_graph: KnowledgeGraph, analyzer: DocumentAnalyzer):
        self.kg = knowledge_graph
        self.analyzer = analyzer
        self.reasoning_chain = []

    async def reason_about_query(self, query: str) -> Dict[str, Any]:
        """Perform multi-step reasoning about a query"""

        # Step 1: Understand the query intent
        intent = await self._analyze_query_intent(query)
        self.reasoning_chain.append({"step": "intent_analysis", "result": intent})

        # Step 2: Identify required information
        required_info = await self._identify_required_information(query, intent)
        self.reasoning_chain.append({"step": "info_requirements", "result": required_info})

        # Step 3: Search knowledge graph
        search_results = await self._search_knowledge_graph(required_info)
        self.reasoning_chain.append({"step": "knowledge_search", "result": len(search_results)})

        # Step 4: Perform analysis if needed
        if intent.get("requires_analysis"):
            analysis = await self._perform_deep_analysis(query, search_results)
            self.reasoning_chain.append({"step": "deep_analysis", "result": analysis})
        else:
            analysis = None

        # Step 5: Synthesize response
        response = await self._synthesize_response(query, search_results, analysis)
        self.reasoning_chain.append({"step": "synthesis", "result": "complete"})

        return {
            "response": response,
            "reasoning_chain": self.reasoning_chain,
            "confidence": self._calculate_confidence(),
            "sources": self._get_sources(search_results)
        }

    async def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze what the user is asking for"""

        prompt = f"""Analyze this construction query and identify:
1. Primary intent (lookup, analysis, comparison, calculation)
2. Subject matter (components, dimensions, conflicts, etc.)
3. Required depth (simple fact vs deep analysis)
4. Specific items mentioned

Query: {query}

Output as JSON:
{{
  "intent": "...",
  "subject": "...",
  "requires_analysis": true/false,
  "specific_items": ["..."]
}}"""

        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2
        )

        return json.loads(response.choices[0].message.content)

    async def _identify_required_information(self, query: str, intent: Dict) -> List[str]:
        """Identify what information is needed to answer the query"""

        required = []

        if "trellis" in query.lower():
            required.extend(["trellis_components", "shop_drawings_TRE"])

        if "base component" in query.lower() or "similar" in query.lower():
            required.append("component_analysis")

        if "conflict" in query.lower():
            required.append("conflict_analysis")

        if any(word in query.lower() for word in ["height", "dimension", "width", "length"]):
            required.append("dimensional_data")

        return required

    async def _search_knowledge_graph(self, required_info: List[str]) -> List[Any]:
        """Search knowledge graph for required information"""

        results = []

        for requirement in required_info:
            if requirement == "trellis_components":
                trellis_comps = [c for c in self.kg.components.values() if "trellis" in c.type.lower() or "TRE" in c.component_id]
                results.extend(trellis_comps)

            elif requirement == "component_analysis":
                base_groups = self.kg.identify_base_components()
                results.append({"base_components": base_groups})

            elif requirement == "conflict_analysis":
                results.append({"conflicts": self.kg.conflicts})

            elif requirement == "dimensional_data":
                results.append({"dimensions": self.kg.dimensions})

        return results

    async def _perform_deep_analysis(self, query: str, search_results: List[Any]) -> Dict[str, Any]:
        """Perform deep analysis on the search results"""

        # For trellis base component analysis
        if "base component" in query.lower():
            components = [r for r in search_results if isinstance(r, Component)]

            # Group by similar dimensions
            base_groups = defaultdict(list)
            for comp in components:
                # Create signature from width, height, material
                if "width" in comp.dimensions and "height" in comp.dimensions:
                    sig = f"{comp.dimensions['width'].value}x{comp.dimensions['height'].value}_{comp.material}"
                    base_groups[sig].append(comp)

            # Analyze each group
            analysis = {
                "base_component_count": len(base_groups),
                "groups": []
            }

            for sig, comps in base_groups.items():
                group_analysis = {
                    "signature": sig,
                    "count": len(comps),
                    "length_variations": sorted(set(
                        comp.dimensions.get("length", Dimension(0, "", "", "", None)).value
                        for comp in comps if "length" in comp.dimensions
                    )),
                    "sample_components": [c.component_id for c in comps[:3]]
                }
                analysis["groups"].append(group_analysis)

            return analysis

        return {}

    async def _synthesize_response(self, query: str, search_results: List[Any], analysis: Optional[Dict]) -> str:
        """Synthesize final response from all gathered information"""

        # Prepare context for LLM
        context_parts = []

        # Add search results
        for result in search_results[:10]:  # Limit for context
            if isinstance(result, Component):
                context_parts.append(f"Component: {result.component_id} - {result.name}")
                for dim_key, dim in result.dimensions.items():
                    context_parts.append(f"  {dim_key}: {dim.value} {dim.unit}")
            elif isinstance(result, dict):
                context_parts.append(json.dumps(result, indent=2)[:1000])

        # Add analysis
        if analysis:
            context_parts.append(f"\nAnalysis Results:\n{json.dumps(analysis, indent=2)[:2000]}")

        # Generate response
        prompt = f"""Based on the following information, answer this construction query accurately and specifically:

Query: {query}

Available Information:
{chr(10).join(context_parts)}

Provide a detailed, accurate answer that:
1. Directly addresses the question
2. Cites specific components and dimensions
3. Explains any analysis performed
4. Highlights important findings

If this is about base components, clearly identify them and explain what makes them "base" components."""

        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert construction analyst. Provide detailed, accurate technical answers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )

        return response.choices[0].message.content

    def _calculate_confidence(self) -> float:
        """Calculate confidence in the reasoning chain"""
        # Simple heuristic - could be made more sophisticated
        if len(self.reasoning_chain) >= 4:
            return 0.95
        elif len(self.reasoning_chain) >= 3:
            return 0.85
        else:
            return 0.75

    def _get_sources(self, search_results: List[Any]) -> List[str]:
        """Extract source references"""
        sources = set()
        for result in search_results:
            if isinstance(result, Component) and result.source:
                sources.add(f"{result.source.doc_id} (Rev {result.source.revision})")
        return list(sources)

# Global instances
knowledge_graph = KnowledgeGraph()
document_analyzer = DocumentAnalyzer(knowledge_graph)
reasoning_engine = ReasoningEngine(knowledge_graph, document_analyzer)

# Enhanced document loading with analysis
async def load_and_analyze_documents():
    """Load and deeply analyze all Aurora documents"""

    aurora_path = Path(__file__).parent.parent.parent / "Aurora (Safeway) Regina, SK"

    if not aurora_path.exists():
        print(f"Aurora path not found: {aurora_path}")
        return

    print(f"Loading and analyzing documents from: {aurora_path}")

    # Load shop drawings with analysis
    tc_drawings_path = aurora_path / "Active Drawing" / "TC Drawings"
    if tc_drawings_path.exists():
        # Process .AI.md files (pre-analyzed content)
        for ai_file in tc_drawings_path.glob("*.AI.md"):
            print(f"Analyzing {ai_file.name}...")

            with open(ai_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create document reference
            doc_ref = DrawingReference(
                doc_id=ai_file.stem.replace(".AI", ""),
                title=ai_file.stem,
                revision=extract_revision(ai_file.name),
                date="2025-03-25",
                content_hash=str(hash(content))
            )

            knowledge_graph.documents[doc_ref.doc_id] = doc_ref
            knowledge_graph.raw_content[doc_ref.doc_id] = content

            # Perform deep analysis if it's a trellis drawing
            if "TRE" in ai_file.name:
                result = await document_analyzer.analyze_shop_drawings(content, doc_ref)
                print(f"  Found {len(result.components)} components")
                print(f"  {result.summary}")

    # Analyze patterns across all documents
    patterns = knowledge_graph.analyze_patterns()
    print(f"\nIdentified {len(patterns)} patterns across documents")

    # Load images for multi-modal analysis
    for img_dir in aurora_path.glob("**/*_images"):
        for img_file in img_dir.glob("*.png"):
            try:
                img = Image.open(img_file)
                knowledge_graph.images[str(img_file)] = img
                print(f"Loaded image: {img_file.name}")
            except Exception as e:
                print(f"Error loading image {img_file}: {e}")

    print(f"\nKnowledge Graph Summary:")
    print(f"  - Components: {len(knowledge_graph.components)}")
    print(f"  - Documents: {len(knowledge_graph.documents)}")
    print(f"  - Images: {len(knowledge_graph.images)}")
    print(f"  - Patterns: {len(knowledge_graph.patterns)}")

def extract_revision(filename: str) -> str:
    """Extract revision from filename"""
    import re
    match = re.search(r'R(\d+)', filename)
    return f"R{match.group(1)}" if match else "R0"

# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize knowledge graph on startup"""
    await load_and_analyze_documents()

@app.post("/chat")
async def enhanced_chat(message: dict):
    """Enhanced chat with reasoning"""

    query = message.get("message", "")

    # Perform multi-step reasoning
    result = await reasoning_engine.reason_about_query(query)

    # Stream response with reasoning chain visible
    async def stream_response():
        # Send reasoning steps
        yield f"data: {json.dumps({'type': 'REASONING_START', 'data': {'steps': len(result['reasoning_chain'])}})}\n\n"

        for step in result["reasoning_chain"]:
            yield f"data: {json.dumps({'type': 'REASONING_STEP', 'data': step})}\n\n"
            await asyncio.sleep(0.1)  # Visual effect

        # Send main response
        yield f"data: {json.dumps({'type': 'TEXT_MESSAGE_START', 'data': {'role': 'assistant'}})}\n\n"

        # Stream response in chunks
        response_text = result["response"]
        chunk_size = 50
        for i in range(0, len(response_text), chunk_size):
            chunk = response_text[i:i+chunk_size]
            yield f"data: {json.dumps({'type': 'TEXT_MESSAGE_CHUNK', 'data': {'content': chunk}})}\n\n"
            await asyncio.sleep(0.02)

        # Add sources and confidence
        yield f"data: {json.dumps({'type': 'METADATA', 'data': {'confidence': result['confidence'], 'sources': result['sources']}})}\n\n"

        yield f"data: {json.dumps({'type': 'TEXT_MESSAGE_END', 'data': {'full_text': response_text}})}\n\n"

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/analyze_image")
async def analyze_image(image: UploadFile = File(...), query: str = ""):
    """Analyze construction drawing image"""

    try:
        # Read image
        contents = await image.read()
        img = Image.open(BytesIO(contents))

        # Convert to base64 for GPT-4V
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Analyze with GPT-4 Vision
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": query or "Analyze this construction drawing. Extract all dimensions, components, and specifications."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                    ]
                }
            ],
            max_tokens=1000
        )

        return {"analysis": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge_graph")
async def get_knowledge_graph():
    """Get current knowledge graph state"""

    base_components = knowledge_graph.identify_base_components()

    return {
        "components_count": len(knowledge_graph.components),
        "documents_count": len(knowledge_graph.documents),
        "patterns_count": len(knowledge_graph.patterns),
        "base_component_families": len(base_components),
        "conflicts": knowledge_graph.conflicts[:10],  # Sample
        "sample_components": list(knowledge_graph.components.keys())[:10],
        "patterns": knowledge_graph.patterns[:5]
    }

@app.post("/reanalyze")
async def reanalyze_document(doc_id: str):
    """Re-analyze a specific document"""

    if doc_id not in knowledge_graph.documents:
        raise HTTPException(status_code=404, detail="Document not found")

    doc_ref = knowledge_graph.documents[doc_id]
    content = knowledge_graph.raw_content.get(doc_id, "")

    if not content:
        raise HTTPException(status_code=400, detail="No content available for document")

    # Re-analyze
    result = await document_analyzer.analyze_shop_drawings(content, doc_ref)

    # Update patterns
    knowledge_graph.analyze_patterns()

    return {
        "doc_id": doc_id,
        "components_found": len(result.components),
        "conflicts_found": len(result.conflicts),
        "patterns_found": len(result.patterns),
        "summary": result.summary
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8100))
    print(f"\n🚀 Starting Enhanced Construction Agent on port {port}")
    print("=" * 50)

    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)