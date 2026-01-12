Analyze all construction drawings in the project and generate comprehensive .AI.md files.

This command will:
1. Scan for all extracted markdown files with companion _images directories
2. Launch parallel Claude Code agents to analyze each drawing
3. Generate detailed .AI.md analysis files with:
   - Visual interpretation (color coding, diagrams, spatial layouts)
   - Extracted dimensions and specifications
   - Cross-references to other drawings
   - Identified conflicts and coordination issues
   - Code compliance notes

Each agent reads both the markdown text AND all images to capture visual information that wouldn't otherwise be searchable.
