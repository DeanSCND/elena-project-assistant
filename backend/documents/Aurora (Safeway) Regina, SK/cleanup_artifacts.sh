#!/bin/bash
# Remove all processing artifacts - markdown files and image directories

echo "==================================================================="
echo "CLEANUP ARTIFACTS - Reverting to Original State"
echo "==================================================================="

# Count artifacts
md_count=$(find . -name "*.md" -type f | wc -l | tr -d ' ')
img_dir_count=$(find . -name "*_images" -type d | wc -l | tr -d ' ')

echo "Found:"
echo "  - $md_count markdown files"
echo "  - $img_dir_count image directories"
echo ""

# Calculate size
md_size=$(find . -name "*.md" -type f -exec du -sk {} + 2>/dev/null | awk '{sum+=$1} END {print sum}')
img_size=$(find . -name "*_images" -type d -exec du -sk {} + 2>/dev/null | awk '{sum+=$1} END {print sum}')
total_mb=$(echo "scale=1; ($md_size + $img_size) / 1024" | bc)

echo "Space to reclaim: ${total_mb} MB"
echo ""
echo "This will DELETE:"
echo "  - All .md files generated from PDFs"
echo "  - All *_images directories"
echo ""
read -p "Continue? (yes/no): " response

if [ "$response" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Removing markdown files..."
find . -name "*.md" -type f -delete

echo "Removing image directories..."
find . -name "*_images" -type d -exec rm -rf {} + 2>/dev/null

echo "Removing backup directory..."
rm -rf __images_backup__

echo ""
echo "✓ Cleanup complete - folder reverted to original state"
echo "✓ Reclaimed ${total_mb} MB"
