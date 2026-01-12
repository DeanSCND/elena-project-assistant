#!/usr/bin/env python3
"""
Construction Drawing Analysis Orchestrator
"""

import os
import json
from pathlib import Path
from datetime import datetime

class DrawingAnalysisOrchestrator:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.drawings = []

    def find_drawings(self):
        """Find all extracted drawings"""
        print("🔍 Scanning for construction drawings...\n")

        for md_file in self.base_dir.rglob("*.md"):
            if md_file.name.endswith(".AI.md") or md_file.name == "DESIGN.md":
                continue

            images_dir = md_file.parent / f"{md_file.stem}_images"

            drawing_info = {
                "md_file": str(md_file),
                "images_dir": str(images_dir) if images_dir.exists() else None,
                "ai_file": str(md_file.with_suffix(".AI.md")),
                "category": self.categorize_drawing(md_file.name),
                "image_count": len(list(images_dir.iterdir())) if images_dir.exists() else 0,
                "already_analyzed": md_file.with_suffix(".AI.md").exists()
            }

            self.drawings.append(drawing_info)

        return self.drawings

    def categorize_drawing(self, filename):
        """Categorize drawing by type"""
        filename_lower = filename.lower()

        if filename_lower.startswith("saf-"):
            return "shop_drawing"
        elif filename_lower.startswith("rfi"):
            return "rfi"
        elif "pcn" in filename_lower or "clar" in filename_lower:
            return "clarification"
        elif "rcp" in filename_lower:
            return "rcp"
        elif "ifc" in filename_lower:
            return "ifc_drawings"
        elif "decor" in filename_lower:
            return "decor"
        else:
            return "general"

    def print_summary(self):
        """Print summary"""
        categories = {}
        for drawing in self.drawings:
            cat = drawing["category"]
            categories[cat] = categories.get(cat, 0) + 1

        print(f"📊 Found {len(self.drawings)} drawings:\n")
        for category, count in sorted(categories.items()):
            print(f"   {category:20s}: {count:3d} drawings")

        analyzed = sum(1 for d in self.drawings if d["already_analyzed"])
        print(f"\n✅ Already analyzed: {analyzed}/{len(self.drawings)}")
        print(f"⏳ Remaining:        {len(self.drawings) - analyzed}/{len(self.drawings)}\n")

if __name__ == "__main__":
    orchestrator = DrawingAnalysisOrchestrator()
    orchestrator.find_drawings()
    orchestrator.print_summary()
    print(f"\n✨ Ready for AI analysis!")
