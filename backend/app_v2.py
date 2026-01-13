#!/usr/bin/env python3
"""
Enhanced Construction Agent POC V2
With deep document analysis and multi-step reasoning
"""

import os
import json
import asyncio
from pathlib import Path
from typing import AsyncGenerator, List, Dict, Any, Optional
from datetime import datetime
import uuid
import re
from collections import defaultdict
from dataclasses import dataclass
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse, Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import tempfile
import httpx

from openai import AsyncOpenAI

# Import knowledge manager
from knowledge_manager import get_knowledge_manager, KnowledgeEntry

# Import Firestore conversation database
from firestore_db import ConversationDB

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing knowledge base...")
    await load_and_analyze_documents()
    yield
    # Shutdown (if needed)
    print("Shutting down...")

# Initialize FastAPI app with lifespan
app = FastAPI(title="Construction Agent V2", lifespan=lifespan)

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

# Document knowledge base
@dataclass
class DocumentChunk:
    """Chunk of document content with source metadata"""
    id: str
    content: str
    metadata: Dict[str, Any]  # PDF name, page, section, coordinates
    embedding: Optional[List[float]] = None  # For semantic search

    def get_citation_ref(self) -> str:
        """Get formatted citation reference for users"""
        pdf = self.metadata.get("source_pdf", "Unknown")
        page = self.metadata.get("page")
        section = self.metadata.get("section")

        # Build user-friendly reference
        ref = pdf
        if page:
            ref += f", page {page}"
        if section and section != "Introduction":
            ref += f", section '{section}'"

        return ref

@dataclass
class DocumentKnowledge:
    """Structured knowledge extracted from documents"""
    components: Dict[str, Dict[str, Any]] = None
    dimensions: Dict[str, List[Dict]] = None
    patterns: List[Dict] = None
    conflicts: List[Dict] = None
    base_components: Dict[str, List] = None
    raw_content: Dict[str, str] = None
    analysis_cache: Dict[str, Any] = None
    chunks: List[DocumentChunk] = None  # NEW: Structured chunks with metadata
    chunk_index: Dict[str, DocumentChunk] = None  # NEW: Quick lookup by ID

    def __post_init__(self):
        self.components = self.components or {}
        self.dimensions = self.dimensions or defaultdict(list)
        self.patterns = self.patterns or []
        self.conflicts = self.conflicts or []
        self.base_components = self.base_components or {}
        self.raw_content = self.raw_content or {}
        self.analysis_cache = self.analysis_cache or {}
        self.chunks = self.chunks or []
        self.chunk_index = self.chunk_index or {}

# Global knowledge base
KNOWLEDGE = DocumentKnowledge()

# Conversation memory for tracking citations
@dataclass
class ConversationMemory:
    """Tracks which chunks were cited in each response"""
    response_citations: Dict[str, List[str]] = None  # message_index → chunk_ids

    def __post_init__(self):
        self.response_citations = self.response_citations or {}

    def store_citations(self, message_index: int, chunk_ids: List[str]):
        """Store which chunks were cited in a response"""
        self.response_citations[str(message_index)] = chunk_ids

    def get_cited_chunks(self, message_index: int) -> List[DocumentChunk]:
        """Retrieve chunks that were cited in a previous message"""
        chunk_ids = self.response_citations.get(str(message_index), [])
        return [KNOWLEDGE.chunk_index[cid] for cid in chunk_ids if cid in KNOWLEDGE.chunk_index]

    def extract_citations_from_text(self, text: str) -> List[str]:
        """Extract <c>chunk_id</c> markers from generated text"""
        return re.findall(r'<c>([^<>]+)</c>', text)

MEMORY = ConversationMemory()

# Initialize knowledge manager
knowledge_manager = get_knowledge_manager()

# Enhanced system prompts
ANALYSIS_PROMPT = """You are an expert construction document analyst with deep understanding of:
- Shop drawings and technical specifications
- Dimensional analysis and pattern recognition
- Component relationships and dependencies
- Conflict identification and resolution

Your analysis should be:
1. PRECISE - Use exact dimensions and specifications
2. COMPREHENSIVE - Consider all relevant factors
3. STRUCTURED - Organize information logically
4. ACTIONABLE - Provide practical insights
"""

REASONING_PROMPT = """You are performing multi-step reasoning on construction documents.

For each query:
1. UNDERSTAND - What is being asked? What information is needed?
2. SEARCH - Find relevant components, dimensions, and specifications
3. ANALYZE - Identify patterns, relationships, and potential issues
4. VERIFY - Cross-reference with other documents
5. SYNTHESIZE - Provide a complete, accurate answer

Always show your reasoning process."""

class ConversationMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    reasoning_mode: bool = True  # Enable deep reasoning by default
    model: str = "gpt-4o"  # Default to GPT-4o
    conversation_history: List[ConversationMessage] = []  # Previous messages for context

def search_chunks(query: str, top_k: int = 5) -> List[DocumentChunk]:
    """
    Search chunks for relevant content (simple keyword-based for now).
    Returns chunks with source metadata intact.
    """
    query_lower = query.lower()
    query_terms = set(query_lower.split())

    scored_chunks = []

    for chunk in KNOWLEDGE.chunks:
        content_lower = chunk.content.lower()

        # Simple scoring: count matching terms
        score = sum(1 for term in query_terms if term in content_lower)

        # Boost score if exact phrase match
        if query_lower in content_lower:
            score += 5

        if score > 0:
            scored_chunks.append((score, chunk))

    # Sort by score and return top_k
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored_chunks[:top_k]]

def create_chunks_from_content(content: str, filename: str, source_pdf: str) -> List[DocumentChunk]:
    """
    Create chunks from document content with metadata.
    Follows Tensorlake citation pattern: chunk with source tracking.
    """
    chunks = []

    # Split content into logical sections
    # Strategy: Split by headers (## or ###) to maintain semantic coherence
    sections = re.split(r'\n(#{2,3}\s+.*?)\n', content)

    chunk_id_base = filename.replace(".AI.md", "").replace(" ", "_")
    current_section = "Introduction"
    chunk_counter = 0

    for i, section in enumerate(sections):
        # Skip empty sections
        if not section.strip():
            continue

        # Check if this is a header
        if section.startswith("##"):
            current_section = section.replace("#", "").strip()
            continue

        # This is content - create a chunk
        if len(section.strip()) > 100:  # Only chunk substantial content
            chunk_id = f"{chunk_id_base}_chunk_{chunk_counter:03d}"

            # Extract page number from content if available (look for "Page X" patterns)
            page_match = re.search(r'[Pp]age\s+(\d+)', section)
            page = int(page_match.group(1)) if page_match else None

            chunk = DocumentChunk(
                id=chunk_id,
                content=section.strip()[:2000],  # Limit chunk size
                metadata={
                    "source_pdf": source_pdf,
                    "source_md": filename,
                    "section": current_section,
                    "page": page,
                    "chunk_index": chunk_counter
                }
            )

            chunks.append(chunk)
            KNOWLEDGE.chunk_index[chunk_id] = chunk
            chunk_counter += 1

    return chunks

async def analyze_shop_drawing_content(content: str, filename: str) -> Dict[str, Any]:
    """Deeply analyze shop drawing content"""

    # Special handling for trellis drawings
    if "TRE" in filename:
        prompt = """Analyze this trellis shop drawing and extract:

1. BASE COMPONENTS (parts with same width/height, varying lengths):
   - Component type and material
   - Fixed dimensions (width, height, thickness)
   - Length variations
   - Quantity of each variation

2. PATTERNS:
   - Repeating dimensional patterns
   - Component families (same profile, different sizes)
   - Assembly relationships

3. SPECIFICATIONS:
   - Material codes (e.g., INFINITY1-2-5X10, PVCWHI1)
   - Exact dimensions with units
   - Grid locations

Extract as structured JSON with these sections:
{
  "base_components": [
    {
      "type": "main_beam",
      "material": "INFINITY1-2-5X10",
      "fixed_dimensions": {
        "width": {"value": 17.875, "unit": "inch"},
        "height": {"value": 8, "unit": "inch"}
      },
      "length_variations": [
        {"length": 120, "unit": "inch", "quantity": 5},
        {"length": 96, "unit": "inch", "quantity": 3}
      ]
    }
  ],
  "patterns": [...],
  "raw_components": [...]
}"""
    else:
        prompt = """Analyze this construction document and extract all technical specifications, dimensions, and components."""

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": ANALYSIS_PROMPT},
                {"role": "user", "content": f"{prompt}\n\nDocument ({filename}):\n{content[:10000]}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=3000
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"Error analyzing {filename}: {e}")
        return {}

async def load_and_analyze_documents():
    """Load Aurora documents with deep analysis"""

    # Use environment variable for documents path, default to relative path
    documents_base = os.getenv('DOCUMENTS_PATH', str(Path(__file__).parent / 'documents'))
    aurora_path = Path(documents_base) / "Aurora (Safeway) Regina, SK"

    if not aurora_path.exists():
        print(f"Warning: Aurora path not found at {aurora_path}")
        return

    print(f"Loading Aurora documents from: {aurora_path}")
    print("=" * 50)

    # Track source PDF mappings
    source_pdf_map = {}

    # Focus on .AI.md files (AI-analyzed content) and key documents
    # Skip PDFs as requested
    patterns = ["**/*.AI.md", "**/*.md"]

    for pattern in patterns:
        for file_path in aurora_path.glob(pattern):
            if file_path.suffix == '.pdf':
                continue  # Skip PDFs

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                filename = file_path.name
                KNOWLEDGE.raw_content[filename] = content

                # Map .AI.md files to their source PDFs
                if ".AI.md" in filename:
                    # Extract source PDF name (e.g., "SAF-TRE-001-R6.AI.md" -> "SAF-TRE-001-R6.pdf")
                    source_pdf = filename.replace(".AI.md", ".pdf")
                    source_pdf_map[filename] = source_pdf

                    # Also check if the PDF exists in the same directory
                    pdf_path = file_path.parent / source_pdf
                    if pdf_path.exists():
                        KNOWLEDGE.analysis_cache[f"source_pdf_{filename}"] = {
                            "md_file": filename,
                            "pdf_file": source_pdf,
                            "pdf_path": str(pdf_path.relative_to(aurora_path)),
                            "pdf_exists": True
                        }

                print(f"Loading {filename} ({len(content):,} chars)...")

                # Create chunks from content (with source PDF metadata)
                if ".AI.md" in filename and filename in source_pdf_map:
                    source_pdf = source_pdf_map[filename]
                    doc_chunks = create_chunks_from_content(content, filename, source_pdf)
                    KNOWLEDGE.chunks.extend(doc_chunks)
                    print(f"  → Created {len(doc_chunks)} chunks with citations")

                # Perform deep analysis on shop drawings
                if "TRE" in filename and ".AI.md" in filename:
                    print(f"  → Analyzing trellis components...")
                    analysis = await analyze_shop_drawing_content(content, filename)

                    if analysis:
                        KNOWLEDGE.analysis_cache[filename] = analysis

                        # Extract base components
                        if "base_components" in analysis:
                            for base_comp in analysis["base_components"]:
                                comp_type = base_comp.get("type", "unknown")
                                if comp_type not in KNOWLEDGE.base_components:
                                    KNOWLEDGE.base_components[comp_type] = []
                                KNOWLEDGE.base_components[comp_type].append(base_comp)

                            print(f"    ✓ Found {len(analysis['base_components'])} base component types")

                        # Store raw components for detailed queries
                        if "raw_components" in analysis:
                            for comp in analysis["raw_components"]:
                                comp_id = comp.get("id", str(uuid.uuid4()))
                                KNOWLEDGE.components[comp_id] = comp

                        # Extract patterns
                        if "patterns" in analysis:
                            KNOWLEDGE.patterns.extend(analysis["patterns"])

            except Exception as e:
                print(f"  ✗ Error loading {filename}: {e}")

    # Summarize loaded knowledge
    print("\n" + "=" * 50)
    print("Knowledge Base Summary:")
    print(f"  Documents loaded: {len(KNOWLEDGE.raw_content)}")
    print(f"  Chunks created: {len(KNOWLEDGE.chunks)}")  # NEW
    print(f"  Components identified: {len(KNOWLEDGE.components)}")
    print(f"  Base component types: {len(KNOWLEDGE.base_components)}")
    print(f"  Patterns found: {len(KNOWLEDGE.patterns)}")
    print(f"  Analyzed documents: {len(KNOWLEDGE.analysis_cache)}")

    if KNOWLEDGE.base_components:
        print("\nBase Component Types Found:")
        for comp_type, instances in KNOWLEDGE.base_components.items():
            print(f"  - {comp_type}: {len(instances)} variations")

async def perform_reasoning(query: str, conversation_history: List[ConversationMessage] = None) -> Dict[str, Any]:
    """Perform multi-step reasoning on query with conversation context"""

    reasoning_steps = []

    # Build conversation context if available
    conversation_context = ""
    if conversation_history:
        conversation_context = "\n\nPrevious conversation:\n"
        for msg in conversation_history[-4:]:  # Include last 4 messages for context
            conversation_context += f"{msg.role.upper()}: {msg.content}\n"

    # Check if this is a learning request
    is_learning, trigger = knowledge_manager.detect_learning_intent(query)
    if is_learning:
        # Extract and save knowledge
        entry = knowledge_manager.extract_knowledge(query, trigger)
        knowledge_manager.save_knowledge(entry)

        return {
            "answer": f"✅ Got it! I'll remember: \"{entry.knowledge}\"\n\nThis has been saved to my knowledge base as a {entry.type}.",
            "reasoning_steps": [
                {
                    "step": "Knowledge Learning",
                    "result": f"Extracted and saved: {entry.knowledge}"
                }
            ],
            "sources_used": 0,
            "source_pdfs": [],
            "source_documents": [],
            "confidence": 1.0,
            "learned": True,
            "knowledge_entry": entry.id
        }

    # Get relevant learned knowledge
    learned_knowledge = knowledge_manager.get_relevant_knowledge(query)
    learned_context = knowledge_manager.format_for_prompt(learned_knowledge)

    # Step 1: Query Understanding
    understanding_prompt = f"""Analyze this construction query:
"{query}"
{conversation_context}

Identify:
1. What specific information is being requested?
2. What type of analysis is needed? (lookup, calculation, comparison, pattern analysis)
3. What components or areas are involved?
4. Is this about base components, dimensions, conflicts, or specifications?
5. Does this question reference information from the previous conversation?

Respond with your analysis."""

    understanding = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": REASONING_PROMPT},
            {"role": "user", "content": understanding_prompt}
        ],
        temperature=0.2,
        max_tokens=500
    )

    reasoning_steps.append({
        "step": "Understanding Query",
        "result": understanding.choices[0].message.content
    })

    # Step 2: Information Retrieval (Chunk-based with source tracking)
    retrieval_context = []
    source_pdfs = set()
    source_documents = []
    retrieved_chunks = []  # Store actual chunk objects for later verification

    # CITATION MEMORY: Check if user is asking about previous citations
    is_source_question = any(keyword in query.lower() for keyword in [
        "what document", "which document", "where did you find", "source", "from what", "what pdf"
    ])

    print(f"\n{'='*80}")
    print(f"DEBUG CITATION FLOW:")
    print(f"  Query: {query[:100]}...")
    print(f"  Is source question: {is_source_question}")
    print(f"  Conversation history length: {len(conversation_history)}")

    if conversation_history:
        print(f"  Last 2 messages:")
        for i, msg in enumerate(conversation_history[-2:]):
            preview = msg.content[:200] if msg.content else "(empty)"
            print(f"    [{i}] {msg.role}: {preview}...")
            if msg.role == "assistant" and "<c>" in msg.content:
                print(f"        ✓ Contains citation markers")

    if is_source_question and conversation_history:
        print(f"\n  SOURCE QUESTION DETECTED - Extracting citations from conversation history")
        # Extract citations from the last assistant message
        for i in range(len(conversation_history) - 1, -1, -1):
            if conversation_history[i].role == "assistant":
                last_assistant_msg = conversation_history[i].content
                print(f"  Last assistant message length: {len(last_assistant_msg)}")
                print(f"  First 500 chars: {last_assistant_msg[:500]}")

                cited_chunk_ids = MEMORY.extract_citations_from_text(last_assistant_msg)
                print(f"  Extracted chunk IDs: {cited_chunk_ids}")

                if cited_chunk_ids:
                    print(f"  ✓ Found {len(cited_chunk_ids)} citations in previous response")
                    # Retrieve the cited chunks
                    for chunk_id in cited_chunk_ids:
                        if chunk_id in KNOWLEDGE.chunk_index:
                            chunk = KNOWLEDGE.chunk_index[chunk_id]
                            retrieved_chunks.append(chunk)

                            # Track source PDFs
                            source_pdf = chunk.metadata.get("source_pdf")
                            if source_pdf:
                                source_pdfs.add(source_pdf)
                                print(f"    [{chunk_id}] → {source_pdf}")

                            # Add chunk to context for verification
                            chunk_text = f"<c>{chunk.id}</c>\n{chunk.content}\n"
                            retrieval_context.append(chunk_text)
                        else:
                            print(f"    ✗ Chunk {chunk_id} not found in index")
                else:
                    print(f"  ✗ No citations found in assistant message")
                break  # Only check the last assistant message
    print(f"{'='*80}\n")

    # NEW: Always search chunks first (context-aware retrieval)
    should_search_chunks = (
        bool(conversation_history) or  # Has conversation context
        any(term in query.lower() for term in ["trellis", "beam", "component", "material", "dimension", "document", "source", "pdf", "where", "which", "what"])
    )

    if should_search_chunks and KNOWLEDGE.chunks and not retrieval_context:
        # Search for relevant chunks (skip if we already retrieved cited chunks)
        relevant_chunks = search_chunks(query, top_k=5)

        if relevant_chunks:
            # Add chunk content to retrieval context WITH citation markers
            for chunk in relevant_chunks:
                # Use <c>chunk_id</c> pattern from research
                chunk_text = f"<c>{chunk.id}</c>\n{chunk.content}\n"
                retrieval_context.append(chunk_text)

                # Track source PDFs from chunk metadata
                source_pdf = chunk.metadata.get("source_pdf")
                if source_pdf:
                    source_pdfs.add(source_pdf)

                source_md = chunk.metadata.get("source_md")
                if source_md:
                    source_documents.append(source_md)

                retrieved_chunks.append(chunk)

            print(f"DEBUG: Retrieved {len(relevant_chunks)} chunks from {len(set(source_pdfs))} PDFs")

    # Fallback: OLD retrieval method if no chunks found
    if not retrieval_context:
        # Check if asking about base components or trellis
        if any(term in query.lower() for term in ["base component", "trellis", "similar", "pattern"]):
            if KNOWLEDGE.base_components:
                retrieval_context.append(f"Base Components Found:\n{json.dumps(KNOWLEDGE.base_components, indent=2)[:3000]}")
            if KNOWLEDGE.patterns:
                retrieval_context.append(f"Patterns Identified:\n{json.dumps(KNOWLEDGE.patterns[:5], indent=2)}")

        # Check for specific documents in cache and track source PDFs
        for doc_name, analysis in KNOWLEDGE.analysis_cache.items():
            if "TRE" in doc_name and "trellis" in query.lower():
                # Skip source_pdf entries to avoid duplication
                if doc_name.startswith("source_pdf_"):
                    continue

                retrieval_context.append(f"Analysis of {doc_name}:\n{json.dumps(analysis, indent=2)[:2000]}")

                # Track the document
                source_documents.append(doc_name)

                # Find corresponding source PDF
                pdf_info_key = f"source_pdf_{doc_name}"
                if pdf_info_key in KNOWLEDGE.analysis_cache:
                    pdf_info = KNOWLEDGE.analysis_cache[pdf_info_key]
                    pdf_name = pdf_info["pdf_file"]
                    source_pdfs.add(pdf_name)
                else:
                    # Infer PDF from .AI.md filename
                    if doc_name.endswith(".AI.md"):
                        inferred_pdf = doc_name.replace(".AI.md", ".pdf")
                        source_pdfs.add(inferred_pdf)


    # Build detailed retrieval result
    retrieval_result = {
        "data_sources_count": len(retrieval_context),
        "documents_used": source_documents[:5],  # Show first 5
        "source_pdfs": list(source_pdfs)[:10]  # Show up to 10 PDFs
    }

    reasoning_steps.append({
        "step": "Information Retrieval",
        "result": json.dumps(retrieval_result, indent=2)
    })

    # Step 3: Analysis
    if retrieval_context:
        # Build PDF source list
        pdf_citations = ""
        if source_pdfs:
            pdf_citations = f"\n\nSource PDF Documents:\n" + "\n".join([f"- {pdf}" for pdf in source_pdfs])

        # Build chunk citation map for reference
        chunk_citation_map = {}
        for chunk in retrieved_chunks:
            chunk_citation_map[chunk.id] = chunk.get_citation_ref()

        # Special handling for source questions
        if is_source_question:
            analysis_prompt = f"""The user is asking about the SOURCE DOCUMENT for information I previously provided.

Previous conversation:
{conversation_context}

Current question:
"{query}"

The chunks I cited in my previous response:
{chr(10).join(retrieval_context)}

Citation Reference Map (chunk_id → user-friendly location):
{json.dumps(chunk_citation_map, indent=2)}

TASK: Tell the user which PDF document(s) I cited in my previous response, using HUMAN-READABLE references.

RESPONSE FORMAT:
1. Identify the specific information they're asking about (e.g., "RAMPA1-4_20")
2. Find which chunk_id(s) contained that information
3. Use the Citation Reference Map to get the user-friendly reference (PDF name, page, section)
4. Answer using the human-readable reference - DO NOT mention "chunk_id" or technical identifiers to the user

Example: "I found the RAMPA1-4_20 information in **SAF-TRE-013 R2.pdf, section 'Missing Documentation'**"

IMPORTANT: Users don't know what "chunks" are. Use only the information from the Citation Reference Map, which includes:
- PDF filename
- Page number (if available)
- Section name (if available)

If the information cannot be traced to a specific source, say: "I apologize, but I cannot trace that specific detail to a source document. Let me search again for that information."
"""
        else:
            analysis_prompt = f"""Based on the retrieved information, analyze and answer this query:
"{query}"
{conversation_context}

{learned_context}

Available Information (with citation markers):
{chr(10).join(retrieval_context)}

Citation Reference Map:
{json.dumps(chunk_citation_map, indent=2)}

{pdf_citations}

CRITICAL CITATION INSTRUCTIONS (Following RAG Best Practices):
1. The information above contains <c>chunk_id</c> markers
2. When you cite information, INCLUDE the <c>chunk_id</c> marker in your response
3. Example: "According to <c>SAF-TRE-003-R3_21__chunk_046</c>, the width is 8 inches"
4. EVERY factual claim MUST have a <c>chunk_id</c> citation
5. Use the Citation Reference Map to see which PDF each chunk_id comes from
6. If you cannot find a chunk to cite, say "I don't have that information in the available documents"

RESPONSE FORMAT:
1. Directly answer the question with inline <c>chunk_id</c> citations
2. Cite specific components and dimensions WITH their chunk_id
3. Explain patterns or relationships found
4. Apply any relevant learned knowledge
5. If the question asks about sources, name the PDF file AND provide the chunk_id

DO NOT reference .md or .AI.md files - only cite the PDF sources using chunk_id markers."""

        analysis = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": ANALYSIS_PROMPT},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )

        final_answer = analysis.choices[0].message.content

        # Extract and store citations from this response
        cited_chunk_ids = MEMORY.extract_citations_from_text(final_answer)
        if cited_chunk_ids:
            # Message index = current conversation length (user messages + assistant responses)
            message_index = len(conversation_history)
            MEMORY.store_citations(message_index, cited_chunk_ids)
            print(f"DEBUG: Stored {len(cited_chunk_ids)} citations for message {message_index}")

        reasoning_steps.append({
            "step": "Analysis & Synthesis",
            "result": "Complete"
        })
    else:
        # No relevant documents found - be honest
        final_answer = await generate_fallback_response(query, conversation_context)
        reasoning_steps.append({
            "step": "No Relevant Documents",
            "result": "Could not find specific information in available documents"
        })

    return {
        "answer": final_answer,
        "reasoning_steps": reasoning_steps,
        "sources_used": len(retrieval_context),
        "source_pdfs": list(source_pdfs) if source_pdfs else [],
        "source_documents": source_documents[:10] if source_documents else [],
        "confidence": 0.95 if retrieval_context else 0.7
    }

async def generate_fallback_response(query: str, conversation_context: str = "") -> str:
    """Generate honest response when specific data not found"""

    # Check if this is a follow-up question about sources
    if any(keyword in query.lower() for keyword in ["what document", "which document", "where did you find", "source", "from what"]):
        if conversation_context:
            return f"I apologize, but I cannot find specific source document information for that detail in my available documents. If I mentioned something in my previous response without a source citation, I should not have - I should only cite information I can trace to specific PDF documents.\n\nCould you please ask your question again, or clarify what specific information you're looking for?"
        else:
            return "I don't have enough context to answer that question about sources. Could you please rephrase or provide more details about what you're looking for?"

    # For general queries where no documents match
    return f"""I couldn't find specific information about "{query}" in the available Aurora Food Store project documents.

The documents I have access to include:
- Trellis shop drawings (SAF-TRE-*.pdf)
- Aurora Food Store construction documents
- PCN (Project Change Notices)
- RFI (Request for Information) documents

Please try:
1. Rephrasing your question with different terms
2. Asking about a different aspect of the project
3. Being more specific about which component or system you're interested in

If you believe this information should be in the documents, please let me know and I can help search for it differently."""

async def stream_reasoning_response(query: str, reasoning_result: Dict[str, Any]) -> AsyncGenerator[str, None]:
    """Stream response with visible reasoning steps"""

    # Send reasoning start event
    yield format_sse_event("REASONING_START", {
        "steps_count": len(reasoning_result["reasoning_steps"])
    })

    # Send each reasoning step with delay for visibility
    for i, step in enumerate(reasoning_result["reasoning_steps"]):
        # Don't truncate Information Retrieval results - they contain JSON we need to parse
        result_to_send = step["result"]
        if step["step"] != "Information Retrieval" and len(step["result"]) > 200:
            result_to_send = step["result"][:200]
            print(f"DEBUG [Stream]: Truncated step '{step['step']}' from {len(step['result'])} to 200 chars")
        else:
            print(f"DEBUG [Stream]: NOT truncating step '{step['step']}' - length: {len(step['result'])}")

        yield format_sse_event("REASONING_STEP", {
            "step_number": i + 1,
            "title": step["step"],
            "result": result_to_send
        })
        await asyncio.sleep(0.3)  # Visual delay

    # Send main response
    yield format_sse_event("TEXT_MESSAGE_START", {"role": "assistant"})

    # Stream the answer in chunks
    answer = reasoning_result["answer"]
    chunk_size = 50

    for i in range(0, len(answer), chunk_size):
        chunk = answer[i:i + chunk_size]
        yield format_sse_event("TEXT_MESSAGE_CHUNK", {"content": chunk})
        await asyncio.sleep(0.02)

    # Send metadata
    yield format_sse_event("ANALYSIS_METADATA", {
        "confidence": reasoning_result["confidence"],
        "sources_used": reasoning_result["sources_used"],
        "source_pdfs": reasoning_result.get("source_pdfs", []),
        "source_documents": reasoning_result.get("source_documents", []),
        "base_components_found": len(KNOWLEDGE.base_components),
        "total_components": len(KNOWLEDGE.components)
    })

    yield format_sse_event("TEXT_MESSAGE_END", {"full_text": answer})
    yield format_sse_event("RUN_FINISHED", {"status": "success"})

def format_sse_event(event_type: str, data: Any) -> str:
    """Format Server-Sent Event"""
    event = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    return f"data: {json.dumps(event)}\n\n"

# API Endpoints
@app.post("/chat")
async def chat_endpoint(message: ChatMessage):
    """Enhanced chat with reasoning"""

    try:
        if message.reasoning_mode:
            # Perform deep reasoning with conversation history
            reasoning_result = await perform_reasoning(
                message.message,
                message.conversation_history
            )

            # Stream response with reasoning steps
            return StreamingResponse(
                stream_reasoning_response(message.message, reasoning_result),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        else:
            # Simple mode (backward compatible)
            # ... existing simple chat logic ...
            pass

    except Exception as e:
        print(f"Error in chat: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Enhanced health check with knowledge base status"""

    return {
        "status": "healthy",
        "documents_loaded": len(KNOWLEDGE.raw_content),
        "chunks_created": len(KNOWLEDGE.chunks),  # NEW: Citation chunks
        "components_identified": len(KNOWLEDGE.components),
        "base_component_types": list(KNOWLEDGE.base_components.keys()),
        "patterns_found": len(KNOWLEDGE.patterns),
        "analyzed_documents": len(KNOWLEDGE.analysis_cache),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }

@app.post("/reprime")
async def reprime_knowledge(request: dict):
    """Re-prime the knowledge base with a different model"""

    model = request.get("model", "gpt-4o")

    async def stream_repriming():
        # Send start event
        yield format_sse_event("REPRIME_START", {"model": model})

        # Clear existing knowledge
        yield format_sse_event("REPRIME_LOG", {"message": "Clearing existing knowledge base..."})
        KNOWLEDGE.components.clear()
        KNOWLEDGE.base_components.clear()
        KNOWLEDGE.patterns.clear()
        KNOWLEDGE.analysis_cache.clear()
        await asyncio.sleep(0.5)

        yield format_sse_event("REPRIME_LOG", {"message": f"Switching to model: {model}"})
        await asyncio.sleep(0.5)

        # Re-analyze documents
        aurora_path = Path(__file__).parent.parent.parent / "Aurora (Safeway) Regina, SK"

        if not aurora_path.exists():
            yield format_sse_event("REPRIME_ERROR", {"error": "Aurora path not found"})
            return

        # Count documents to analyze
        ai_files = list(aurora_path.glob("**/*.AI.md"))
        total_files = len([f for f in ai_files if "TRE" in f.name])

        yield format_sse_event("REPRIME_LOG", {
            "message": f"Found {total_files} trellis shop drawings to analyze"
        })

        analyzed = 0
        for file_path in ai_files:
            if "TRE" in file_path.name:
                analyzed += 1
                yield format_sse_event("REPRIME_PROGRESS", {
                    "current": analyzed,
                    "total": total_files,
                    "file": file_path.name,
                    "message": f"Analyzing {file_path.name}..."
                })

                # Re-analyze with new model
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Simulate analysis time
                await asyncio.sleep(1)  # In production, would call analyze_shop_drawing_content

                # Store in cache
                KNOWLEDGE.analysis_cache[file_path.name] = {
                    "analyzed_with": model,
                    "timestamp": datetime.now().isoformat()
                }

        yield format_sse_event("REPRIME_LOG", {
            "message": f"✓ Successfully analyzed {analyzed} documents with {model}"
        })

        yield format_sse_event("REPRIME_COMPLETE", {
            "model": model,
            "documents_analyzed": analyzed
        })

    return StreamingResponse(
        stream_repriming(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/knowledge")
async def get_knowledge_base():
    """Get current knowledge base state"""

    return {
        "base_components": KNOWLEDGE.base_components,
        "patterns": KNOWLEDGE.patterns[:10],  # Sample
        "component_count": len(KNOWLEDGE.components),
        "document_count": len(KNOWLEDGE.raw_content),
        "sample_components": dict(list(KNOWLEDGE.components.items())[:5])
    }

@app.post("/auto-save-conversation")
async def auto_save_conversation(data: dict):
    """
    Auto-save conversation after each chat response (silent, no UI).
    Creates or updates conversation in Firestore with user_saved=False.
    """
    try:
        conversation_id = data.get("conversation_id")
        messages = data.get("messages", [])

        # Generate ID if not provided
        if not conversation_id:
            conversation_id = ConversationDB.generate_id()

        # Auto-save with user_saved=False
        saved = ConversationDB.save_conversation(
            conversation_id=conversation_id,
            messages=messages,
            title=None,  # No title for auto-saved conversations
            user_saved=False,
            metadata=data.get("metadata", {})
        )

        return {
            "success": True,
            "conversation_id": conversation_id,
            "message_count": len(messages)
        }

    except Exception as e:
        print(f"Error auto-saving conversation: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


@app.post("/save_conversation")
async def save_conversation(data: dict):
    """
    User-initiated save: toggles user_saved=True and sets title.
    Called when user clicks 'Save' button.
    """
    try:
        conversation_id = data.get("conversation_id")
        title = data.get("title", "Untitled Conversation")
        messages = data.get("messages", [])

        if not conversation_id:
            conversation_id = ConversationDB.generate_id()

        # Save or update with user_saved=True
        saved = ConversationDB.save_conversation(
            conversation_id=conversation_id,
            messages=messages,
            title=title,
            user_saved=True,
            metadata=data.get("metadata", {})
        )

        return {
            "success": True,
            "conversation_id": conversation_id,
            "title": title
        }

    except Exception as e:
        print(f"Error saving conversation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations")
async def list_conversations(user_saved_only: bool = True, limit: int = 20):
    """
    List conversations from Firestore.
    By default, only returns user-saved conversations (user_saved=True).
    Set user_saved_only=false to see all conversations including auto-saved.
    """
    try:
        conversations = ConversationDB.list_conversations(
            user_saved_only=user_saved_only,
            limit=limit,
            order_by='updated_at',
            descending=True
        )

        # Format for frontend
        formatted = []
        for conv in conversations:
            formatted.append({
                "conversation_id": conv.get("conversation_id"),
                "title": conv.get("title", "Untitled Conversation"),
                "message_count": conv.get("message_count", 0),
                "user_saved": conv.get("user_saved", False),
                "created_at": conv.get("created_at"),
                "updated_at": conv.get("updated_at")
            })

        return {"conversations": formatted}

    except Exception as e:
        print(f"Error listing conversations: {e}")
        import traceback
        traceback.print_exc()
        return {"conversations": []}

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation from Firestore"""
    try:
        conversation = ConversationDB.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return conversation

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting conversation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_specific_topic(request: dict):
    """Perform specific analysis on demand"""

    topic = request.get("topic", "")

    if topic == "trellis_base_components":
        # Specialized trellis analysis
        trellis_components = {
            k: v for k, v in KNOWLEDGE.components.items()
            if "TRE" in k or "trellis" in str(v).lower()
        }

        # Group by dimensions
        dimension_groups = defaultdict(list)
        for comp_id, comp in trellis_components.items():
            if isinstance(comp, dict):
                dims = comp.get("dimensions", {})
                if dims:
                    key = f"{dims.get('width', {}).get('value', 0)}x{dims.get('height', {}).get('value', 0)}"
                    dimension_groups[key].append(comp)

        return {
            "topic": "trellis_base_components",
            "total_trellis_components": len(trellis_components),
            "dimension_groups": len(dimension_groups),
            "groups": {k: len(v) for k, v in dimension_groups.items()},
            "base_components": KNOWLEDGE.base_components.get("main_beam", [])[:3]  # Sample
        }

    return {"error": "Unknown analysis topic"}

# Keep existing voice endpoints
@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe audio using OpenAI Whisper"""
    try:
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as audio_file:
                transcript = await openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            return {"text": transcript}
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/text-to-speech")
async def text_to_speech(request: dict):
    """Convert text to speech"""
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")

        # Try ElevenLabs first, fallback to OpenAI
        elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")

        if elevenlabs_key:
            voice_id = request.get("voice_id", "21m00Tcm4TlvDq8ikWAM")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={
                        "Accept": "audio/mpeg",
                        "Content-Type": "application/json",
                        "xi-api-key": elevenlabs_key
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_monolingual_v1",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75
                        }
                    }
                )

                if response.status_code == 200:
                    return Response(
                        content=response.content,
                        media_type="audio/mpeg"
                    )

        # Fallback to OpenAI TTS
        response = await openai_client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )

        return Response(
            content=response.content,
            media_type="audio/mpeg"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Knowledge Management Endpoints
@app.get("/learned-knowledge")
async def get_learned_knowledge():
    """Get all learned knowledge organized by type"""
    try:
        km = get_knowledge_manager()
        organized = km.get_all_knowledge()

        # Convert to JSON-serializable format
        result = {}
        for type_key, entries in organized.items():
            result[type_key] = [
                {
                    "id": entry.id,
                    "type": entry.type,
                    "trigger": entry.trigger,
                    "knowledge": entry.knowledge,
                    "context": entry.context,
                    "source": entry.source,
                    "created_at": entry.created_at,
                    "tags": entry.tags,
                    "usage_count": entry.usage_count,
                    "confidence": entry.confidence,
                    "examples": entry.examples
                }
                for entry in entries
            ]

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learned-knowledge/search")
async def search_learned_knowledge(request: dict):
    """Search learned knowledge by query"""
    try:
        query = request.get("query", "")
        km = get_knowledge_manager()
        results = km.search_knowledge(query)

        return [
            {
                "id": entry.id,
                "type": entry.type,
                "knowledge": entry.knowledge,
                "tags": entry.tags,
                "usage_count": entry.usage_count
            }
            for entry in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/learned-knowledge/{entry_id}")
async def update_learned_knowledge(entry_id: str, request: dict):
    """Update a learned knowledge entry"""
    try:
        km = get_knowledge_manager()
        updates = request.get("updates", {})
        success = km.update_entry(entry_id, updates)

        if not success:
            raise HTTPException(status_code=404, detail="Knowledge entry not found")

        return {"success": True, "message": "Knowledge updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/learned-knowledge/{entry_id}")
async def delete_learned_knowledge(entry_id: str):
    """Delete a learned knowledge entry"""
    try:
        km = get_knowledge_manager()
        success = km.delete_entry(entry_id)

        if not success:
            raise HTTPException(status_code=404, detail="Knowledge entry not found")

        return {"success": True, "message": "Knowledge deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learned-knowledge/export")
async def export_learned_knowledge():
    """Export learned knowledge for backup"""
    try:
        km = get_knowledge_manager()
        export_path = km.export_knowledge()

        return {"success": True, "path": export_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files for frontend (production mode)
# Check if built frontend exists
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    print(f"📦 Serving frontend from: {frontend_dist}")
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend for all non-API routes"""
        # If path is API route, let it fall through
        if full_path.startswith(("chat", "learned-knowledge", "health", "model", "docs", "openapi.json")):
            raise HTTPException(status_code=404)

        # Serve index.html for all other routes (SPA routing)
        # Try index_v2.html first (built by Vite), then index.html
        index_file = frontend_dist / "index_v2.html"
        if not index_file.exists():
            index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        raise HTTPException(status_code=404)
else:
    print("⚠️  Frontend dist folder not found - running in API-only mode")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8100))
    print(f"\n🚀 Starting Enhanced Construction Agent V2 on port {port}")
    print("=" * 50)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set!")

    # Run without reload to avoid the import string issue
    uvicorn.run(app, host="0.0.0.0", port=port)