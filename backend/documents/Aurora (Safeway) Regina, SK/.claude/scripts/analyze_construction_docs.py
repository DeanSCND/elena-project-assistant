#!/usr/bin/env python3
"""
Construction Drawing Analysis Orchestrator

Finds extracted construction drawings and prepares them for AI analysis.
Outputs a JSON task list for the analysis agent to process.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

class DrawingAnalysisOrchestrator:
    def __init__(self, base_dir, output_file=None):
        self.base_dir = Path(base_dir)
        self.output_file = output_file or self.base_dir / ".claude" / "analysis_tasks.json"
        self.drawings = []

    def find_drawings(self):
        """Find all extracted drawings (markdown + image directories)"""
        print("=" * 70)
        print("CONSTRUCTION DRAWING ANALYSIS ORCHESTRATOR")
        print("=" * 70)
        print(f"Scanning: {self.base_dir}\n")

        # Find all .md files with companion _images directories
        for root, dirs, files in os.walk(self.base_dir):
            # Skip hidden directories
            if '/.claude' in root or '/__' in root:
                continue

            for filename in files:
                if filename.endswith('.md') and not filename.endswith('.AI.md'):
                    md_path = Path(root) / filename
                    img_dir_name = filename.replace('.md', '_images')
                    img_dir = Path(root) / img_dir_name

                    # Check if companion image directory exists
                    if img_dir.exists() and img_dir.is_dir():
                        # Count images
                        image_files = list(img_dir.glob('*.png')) + \
                                    list(img_dir.glob('*.jpg')) + \
                                    list(img_dir.glob('*.jpeg')) + \
                                    list(img_dir.glob('*.gif'))

                        if image_files:
                            # Check if already analyzed
                            ai_md_path = md_path.with_suffix('.AI.md')
                            needs_analysis = not ai_md_path.exists()

                            self.drawings.append({
                                'name': filename.replace('.md', ''),
                                'md_path': str(md_path.relative_to(self.base_dir)),
                                'img_dir': str(img_dir.relative_to(self.base_dir)),
                                'ai_md_path': str(ai_md_path.relative_to(self.base_dir)),
                                'image_count': len(image_files),
                                'needs_analysis': needs_analysis,
                                'md_size': md_path.stat().st_size,
                                'category': self.categorize_drawing(filename)
                            })

        self.drawings.sort(key=lambda x: x['name'])
        return self.drawings

    def categorize_drawing(self, filename):
        """Categorize drawing by type based on filename"""
        filename_upper = filename.upper()

        if 'SAF-TRE' in filename_upper or 'SHOP' in filename_upper:
            return 'shop_drawing'
        elif 'RFI' in filename_upper:
            return 'rfi'
        elif 'PCN' in filename_upper or 'CLAR' in filename_upper:
            return 'clarification'
        elif 'RCP' in filename_upper or 'CEILING' in filename_upper:
            return 'rcp'
        elif 'IFC' in filename_upper:
            return 'ifc_drawings'
        elif 'DECOR' in filename_upper:
            return 'decor'
        else:
            return 'general'

    def generate_task_manifest(self):
        """Generate task manifest for agent processing"""
        manifest = {
            'project': {
                'name': 'Aurora Food Store (Safeway) Regina, SK',
                'type': 'grocery_store',
                'base_dir': str(self.base_dir),
                'generated': datetime.now().isoformat()
            },
            'analysis_config': {
                'focus_areas': [
                    'hvac_clearances',
                    'structural_conflicts',
                    'color_coding',
                    'ceiling_heights',
                    'cross_references'
                ],
                'critical_elements': [
                    'trellis structures',
                    'bulkheads',
                    'exposed structure',
                    'equipment clearances'
                ]
            },
            'drawings': self.drawings,
            'summary': {
                'total_drawings': len(self.drawings),
                'need_analysis': sum(1 for d in self.drawings if d['needs_analysis']),
                'already_analyzed': sum(1 for d in self.drawings if not d['needs_analysis']),
                'total_images': sum(d['image_count'] for d in self.drawings),
                'by_category': {}
            }
        }

        # Count by category
        for drawing in self.drawings:
            cat = drawing['category']
            manifest['summary']['by_category'][cat] = \
                manifest['summary']['by_category'].get(cat, 0) + 1

        return manifest

    def print_summary(self, manifest):
        """Print summary of findings"""
        summary = manifest['summary']

        print(f"\n📊 Found {summary['total_drawings']} drawings:")
        print(f"   ✓ Already analyzed: {summary['already_analyzed']}")
        print(f"   ⏳ Need analysis: {summary['need_analysis']}")
        print(f"   🖼️  Total images: {summary['total_images']:,}")

        print(f"\n📁 By category:")
        for cat, count in sorted(summary['by_category'].items()):
            print(f"   {cat}: {count}")

        if summary['need_analysis'] > 0:
            print(f"\n🎯 Drawings to analyze:")
            for drawing in self.drawings:
                if drawing['needs_analysis']:
                    print(f"   • {drawing['name']} ({drawing['image_count']} images)")

    def save_manifest(self, manifest):
        """Save task manifest to file"""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"\n💾 Task manifest saved: {self.output_file}")

    def run(self, save_manifest=True):
        """Main orchestration"""
        self.find_drawings()
        manifest = self.generate_task_manifest()
        self.print_summary(manifest)

        if save_manifest:
            self.save_manifest(manifest)

        return manifest

if __name__ == "__main__":
    base_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    orchestrator = DrawingAnalysisOrchestrator(base_dir)
    manifest = orchestrator.run()

    # Output for slash command to parse
    print(f"\n✅ Ready for analysis: {manifest['summary']['need_analysis']} drawings")
    sys.exit(0)
