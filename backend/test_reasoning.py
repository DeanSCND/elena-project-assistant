#!/usr/bin/env python3
"""
Test script for enhanced reasoning capabilities
Tests the agent's ability to analyze trellis components like Claude Code did
"""

import asyncio
import json
from pathlib import Path
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

# Import the enhanced agent
from app_v2 import perform_reasoning, load_and_analyze_documents, KNOWLEDGE

# Test queries similar to what Claude Code handled
TEST_QUERIES = [
    {
        "query": "The trellis is made up of many parts which have the same width and height, only the length is different. The shop drawings show every part which is why there is over 4000 lines. Are you able to compare parts for similar dimensions and determine what the base components are. There are probably only 4-5 base components.",
        "expected_analysis": ["base components", "dimensional patterns", "trellis analysis"]
    },
    {
        "query": "Analyze the trellis shop drawings to identify the base components",
        "expected_analysis": ["base components", "shop drawings", "component identification"]
    },
    {
        "query": "What are the common dimensional patterns in the trellis system?",
        "expected_analysis": ["patterns", "dimensions", "trellis"]
    }
]

async def test_reasoning():
    """Test the reasoning capabilities"""

    print("=" * 60)
    print("Enhanced Construction Agent - Reasoning Test")
    print("=" * 60)

    # Load and analyze documents first
    print("\n📚 Loading and analyzing documents...")
    await load_and_analyze_documents()

    print(f"\n📊 Knowledge Base Status:")
    print(f"  - Documents: {len(KNOWLEDGE.raw_content)}")
    print(f"  - Components: {len(KNOWLEDGE.components)}")
    print(f"  - Base Types: {len(KNOWLEDGE.base_components)}")
    print(f"  - Patterns: {len(KNOWLEDGE.patterns)}")

    # Test each query
    for i, test in enumerate(TEST_QUERIES, 1):
        print(f"\n{'=' * 60}")
        print(f"Test {i}: Reasoning Analysis")
        print(f"{'=' * 60}")
        print(f"Query: {test['query'][:100]}...")

        try:
            # Perform reasoning
            result = await perform_reasoning(test['query'])

            print(f"\n🧠 Reasoning Steps:")
            for step in result['reasoning_steps']:
                print(f"  → {step['step']}")
                if len(step['result']) > 100:
                    print(f"    {step['result'][:100]}...")
                else:
                    print(f"    {step['result']}")

            print(f"\n📝 Final Answer:")
            print("-" * 40)
            print(result['answer'][:500] if len(result['answer']) > 500 else result['answer'])
            print("-" * 40)

            print(f"\n📊 Metrics:")
            print(f"  - Confidence: {result['confidence'] * 100:.0f}%")
            print(f"  - Sources Used: {result['sources_used']}")

            # Check if expected analysis topics were covered
            answer_lower = result['answer'].lower()
            covered = [topic for topic in test['expected_analysis'] if topic in answer_lower]
            print(f"  - Topics Covered: {covered}")

            if len(covered) >= len(test['expected_analysis']) * 0.7:
                print(f"  ✅ Test PASSED - Good coverage of expected topics")
            else:
                print(f"  ⚠️  Test PARTIAL - Some topics may be missing")

        except Exception as e:
            print(f"  ❌ Test FAILED - Error: {e}")

    # Specific base component analysis
    print(f"\n{'=' * 60}")
    print("Base Component Analysis")
    print(f"{'=' * 60}")

    if KNOWLEDGE.base_components:
        print(f"\n🔧 Base Components Found:")
        for comp_type, instances in KNOWLEDGE.base_components.items():
            print(f"\n  {comp_type}:")
            if instances and len(instances) > 0:
                sample = instances[0]
                print(f"    Material: {sample.get('material', 'N/A')}")

                if 'fixed_dimensions' in sample:
                    print(f"    Fixed Dimensions:")
                    for dim_name, dim_data in sample['fixed_dimensions'].items():
                        print(f"      - {dim_name}: {dim_data.get('value', 'N/A')} {dim_data.get('unit', '')}")

                if 'length_variations' in sample:
                    variations = sample['length_variations'][:3]  # Show first 3
                    print(f"    Length Variations: {len(sample['length_variations'])} total")
                    for var in variations:
                        print(f"      - {var.get('length', 'N/A')} {var.get('unit', '')}: {var.get('quantity', 0)} pieces")
    else:
        print("  ⚠️  No base components extracted - may need document analysis")

    # Compare with expected Claude Code results
    print(f"\n{'=' * 60}")
    print("Comparison with Claude Code Analysis")
    print(f"{'=' * 60}")

    expected_components = {
        "Main Beam Profile": {
            "width": 17.875,
            "height": 8,
            "material": "INFINITY1-2-5X10"
        },
        "Aluminum Frame": {
            "profile": "50mm x 30mm",
            "material": "6063-T5 Aluminum"
        },
        "Spacer Support": {
            "width": 8,
            "height": 2,
            "material": "PVCWHI1"
        },
        "End Caps": {
            "size": "8\" x 2\"",
            "material": "STYWHI.020"
        },
        "Joiner Block": {
            "size": "14\" x 7.5\" x 1\"",
            "material": "PVCWHI1"
        }
    }

    print("\nExpected base components (from Claude Code):")
    for comp_name, specs in expected_components.items():
        print(f"  • {comp_name}: {specs}")

    # Check if our analysis found similar components
    found_count = 0
    for comp_type in KNOWLEDGE.base_components.keys():
        for expected_name in expected_components.keys():
            if expected_name.lower() in comp_type.lower() or comp_type.lower() in expected_name.lower():
                found_count += 1
                print(f"\n  ✅ Found match: {comp_type} ≈ {expected_name}")
                break

    coverage = (found_count / len(expected_components)) * 100 if expected_components else 0
    print(f"\n📊 Component Coverage: {coverage:.0f}%")

    if coverage >= 60:
        print("✅ Good component identification!")
    elif coverage >= 40:
        print("⚠️  Partial component identification - may need tuning")
    else:
        print("❌ Low component identification - needs improvement")

    print(f"\n{'=' * 60}")
    print("Test Complete!")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    asyncio.run(test_reasoning())