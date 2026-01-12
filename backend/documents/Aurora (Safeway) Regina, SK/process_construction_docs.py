#!/usr/bin/env python3
"""
One Script to Rule Them All - Construction Document Processor

Recursively processes PDFs to markdown with optimized image cleanup
"""

import os
import sys
from pathlib import Path
import shutil
import fitz  # PyMuPDF
from multiprocessing import Pool, cpu_count
from PIL import Image
import imagehash
from datetime import datetime

# PROTECTED PATTERNS - images from these won't be deleted
PROTECTED_PATTERNS = [
    'SAF-',           # Shop drawings
    'Submittal',      # Submittal packages
    'Detail',         # Detail sheets
    'Schedule',       # Equipment schedules
    'Diagram',        # System diagrams
    '_SD_',           # Shop Drawing prefix
    'RFI',            # Requests for Information
]

KNOWN_LOGOS = ['sobeys', 'safeway', 'logo', 'header', 'footer', 'watermark', 'banner', 'branding']

class ConstructionDocProcessor:
    def __init__(self, base_dir, workers=None):
        self.base_dir = Path(base_dir)
        self.workers = workers or max(1, cpu_count() - 1)
        self.stats = {
            'pdfs_processed': 0,
            'pdfs_failed': 0,
            'pages_extracted': 0,
            'images_extracted': 0,
            'images_deleted': 0,
            'images_kept': 0,
            'images_protected': 0,
            'deleted_simple_shapes': 0,
            'deleted_blank': 0,
            'deleted_tiny': 0,
            'deleted_icon': 0,
            'deleted_by_name': 0,
            'deleted_duplicate': 0,
            'bytes_saved': 0,
        }

    def find_pdfs_recursive(self):
        """Find all PDFs recursively, excluding backups"""
        pdfs = []
        for root, dirs, files in os.walk(self.base_dir):
            # Skip backup directories
            dirs[:] = [d for d in dirs if 'backup' not in d.lower()]

            for filename in files:
                if filename.lower().endswith('.pdf'):
                    pdfs.append(Path(root) / filename)
        return sorted(pdfs)

    def extract_pdf(self, pdf_path):
        """Extract a single PDF to markdown with images positioned inline"""
        try:
            print(f"\n📄 Processing: {pdf_path.relative_to(self.base_dir)}")

            # Create output paths
            output_name = pdf_path.stem
            output_md = pdf_path.with_suffix('.md')
            output_img_dir = pdf_path.parent / f"{output_name}_images"

            # Skip if already processed
            if output_md.exists():
                print(f"   ⏭️  Already processed (found {output_md.name})")
                return True

            # Open PDF
            doc = fitz.open(pdf_path)
            total_pages = len(doc)

            # Create image directory
            output_img_dir.mkdir(exist_ok=True)

            markdown_content = []
            markdown_content.append(f"# {output_name}\n\n")
            markdown_content.append(f"**Source**: `{pdf_path.name}`  \n")
            markdown_content.append(f"**Pages**: {total_pages}  \n")
            markdown_content.append(f"**Extracted**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            markdown_content.append("---\n\n")

            image_count = 0

            for page_num in range(total_pages):
                page = doc[page_num]
                markdown_content.append(f"## Page {page_num + 1}\n\n")

                # Get content blocks with positions
                content_items = []

                # Extract text blocks with positions
                text_dict = page.get_text("dict")
                for block in text_dict.get("blocks", []):
                    if block.get("type") == 0:  # Text block
                        bbox = block.get("bbox", [0, 0, 0, 0])
                        # Extract text from block
                        block_text = ""
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                block_text += span.get("text", "")
                            block_text += "\n"

                        if block_text.strip():
                            content_items.append({
                                'type': 'text',
                                'y': bbox[1],  # Top Y coordinate
                                'content': block_text
                            })

                # Extract images with positions
                image_list = page.get_images(full=True)
                page_has_images = len(image_list) > 0

                for img_index, img_info in enumerate(image_list):
                    xref = img_info[0]

                    # Get image position on page
                    image_rects = page.get_image_rects(xref)
                    if image_rects:
                        bbox = image_rects[0]  # Use first occurrence

                        # Extract and save image
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]

                        img_filename = f"page{page_num+1:03d}_img{img_index+1:03d}.{image_ext}"
                        img_path = output_img_dir / img_filename

                        with open(img_path, "wb") as img_file:
                            img_file.write(image_bytes)

                        content_items.append({
                            'type': 'image',
                            'y': bbox.y0,  # Top Y coordinate
                            'filename': img_filename,
                            'path': f"{output_img_dir.name}/{img_filename}"
                        })
                        image_count += 1

                # FALLBACK: If no embedded images, render page as PNG
                # This captures vector-based drawings (floor plans, RCPs, etc.)
                if not page_has_images:
                    # Render page at 150 DPI (good quality for AI analysis)
                    mat = fitz.Matrix(150/72, 150/72)  # 72 DPI = 1x scale
                    pix = page.get_pixmap(matrix=mat)

                    img_filename = f"page{page_num+1:03d}_rendered.png"
                    img_path = output_img_dir / img_filename
                    pix.save(str(img_path))

                    # Add to content (place at top of page since it's the whole page)
                    content_items.append({
                        'type': 'image',
                        'y': 0,  # Top of page
                        'filename': img_filename,
                        'path': f"{output_img_dir.name}/{img_filename}"
                    })
                    image_count += 1

                # Sort content by vertical position (top to bottom)
                content_items.sort(key=lambda x: x['y'])

                # Generate markdown with inline images
                for item in content_items:
                    if item['type'] == 'text':
                        markdown_content.append(item['content'])
                        markdown_content.append("\n")
                    else:  # image
                        markdown_content.append(f"![{item['filename']}]({item['path']})\n\n")

                markdown_content.append("\n")

                if (page_num + 1) % 10 == 0:
                    print(f"   Processing page {page_num + 1}/{total_pages}...")

            doc.close()

            # Write markdown
            with open(output_md, 'w', encoding='utf-8') as f:
                f.writelines(markdown_content)

            self.stats['pdfs_processed'] += 1
            self.stats['pages_extracted'] += total_pages
            self.stats['images_extracted'] += image_count

            print(f"   ✓ Extracted {total_pages} pages, {image_count} images")
            return True

        except Exception as e:
            print(f"   ❌ Failed: {e}")
            self.stats['pdfs_failed'] += 1
            return False

    def is_protected_source(self, img_dir_name):
        """Check if image directory is from protected source"""
        for pattern in PROTECTED_PATTERNS:
            if pattern in img_dir_name:
                return True
        return False

    def is_obvious_logo_by_name(self, filename):
        """Check filename for logo indicators"""
        filename_lower = filename.lower()
        for term in KNOWN_LOGOS:
            if term in filename_lower:
                return True
        return False

    def analyze_image(self, img_path):
        """Analyze single image for deletion (parallel execution)"""
        try:
            file_size = os.path.getsize(img_path)

            # Skip very small files
            if file_size < 2000:
                return {'path': img_path, 'delete': True, 'reason': 'tiny', 'size': file_size}

            img = Image.open(img_path)

            # Check if blank/white
            extrema = img.convert('L').getextrema()
            if extrema == (255, 255):
                return {'path': img_path, 'delete': True, 'reason': 'blank', 'size': file_size}

            # Check if blank/black
            if extrema == (0, 0):
                return {'path': img_path, 'delete': True, 'reason': 'blank', 'size': file_size}

            # Check if very small dimensions
            if img.width < 50 and img.height < 50:
                return {'path': img_path, 'delete': True, 'reason': 'icon', 'size': file_size}

            # Improved simple shape detection
            # Check for images with very few colors (likely simple shapes/fills)
            if img.mode in ('RGB', 'RGBA'):
                colors = img.getcolors(maxcolors=10)
                if colors and len(colors) <= 2:
                    # Only 1-2 colors = simple fill/shape
                    return {'path': img_path, 'delete': True, 'reason': 'simple_shape', 'size': file_size}
            else:
                # For grayscale, check if it's just a single tone
                grayscale_colors = img.convert('L').getcolors(maxcolors=5)
                if grayscale_colors and len(grayscale_colors) <= 2:
                    return {'path': img_path, 'delete': True, 'reason': 'simple_shape', 'size': file_size}

            # Get hash for duplicate detection
            img_hash = str(imagehash.average_hash(img))
            return {'path': img_path, 'delete': False, 'hash': img_hash, 'size': file_size}

        except Exception:
            return {'path': img_path, 'delete': False, 'size': 0}

    def cleanup_images(self):
        """Fast parallel image cleanup"""
        print("\n" + "=" * 70)
        print("IMAGE CLEANUP - Fast Parallel Mode")
        print("=" * 70)
        print(f"Workers: {self.workers}")

        # Find all image directories
        image_dirs = []
        for root, dirs, files in os.walk(self.base_dir):
            for dirname in dirs:
                if dirname.endswith('_images') and '__backup__' not in root:
                    image_dirs.append(Path(root) / dirname)

        if not image_dirs:
            print("No image directories found - cleanup skipped")
            return

        print(f"Found {len(image_dirs)} image directories")

        seen_hashes = set()

        for img_dir in sorted(image_dirs):
            dir_name = img_dir.name
            rel_path = img_dir.relative_to(self.base_dir)

            # Check if protected
            if self.is_protected_source(dir_name):
                images = list(img_dir.glob('*.png')) + list(img_dir.glob('*.jpg')) + \
                        list(img_dir.glob('*.jpeg')) + list(img_dir.glob('*.gif'))
                count = len(images)
                self.stats['images_protected'] += count
                self.stats['images_kept'] += count
                print(f"\n🛡️  PROTECTED: {rel_path} ({count} images)")
                continue

            print(f"\n📋 Processing: {rel_path}")

            # Get all images
            images = list(img_dir.glob('*.png')) + list(img_dir.glob('*.jpg')) + \
                    list(img_dir.glob('*.jpeg')) + list(img_dir.glob('*.gif')) + \
                    list(img_dir.glob('*.bmp'))

            if not images:
                continue

            # First pass: filename-based deletion
            remaining_images = []
            for img_path in images:
                if self.is_obvious_logo_by_name(img_path.name):
                    file_size = img_path.stat().st_size
                    img_path.unlink()
                    self.stats['images_deleted'] += 1
                    self.stats['bytes_saved'] += file_size
                else:
                    remaining_images.append(img_path)

            if len(images) - len(remaining_images) > 0:
                deleted_by_name = len(images) - len(remaining_images)
                print(f"   Deleted {deleted_by_name} by filename")
                self.stats['deleted_by_name'] += deleted_by_name

            if not remaining_images:
                continue

            # Second pass: parallel analysis
            print(f"   Analyzing {len(remaining_images)} images...")

            with Pool(self.workers) as pool:
                results = pool.map(self.analyze_image, [str(p) for p in remaining_images])

            # Process results
            for result in results:
                if result.get('delete'):
                    Path(result['path']).unlink()
                    self.stats['images_deleted'] += 1
                    self.stats['bytes_saved'] += result['size']

                    # Track deletion reason
                    reason = result.get('reason')
                    if reason == 'simple_shape':
                        self.stats['deleted_simple_shapes'] += 1
                    elif reason == 'blank':
                        self.stats['deleted_blank'] += 1
                    elif reason == 'tiny':
                        self.stats['deleted_tiny'] += 1
                    elif reason == 'icon':
                        self.stats['deleted_icon'] += 1
                else:
                    img_hash = result.get('hash')
                    if img_hash:
                        if img_hash in seen_hashes:
                            Path(result['path']).unlink()
                            self.stats['images_deleted'] += 1
                            self.stats['deleted_duplicate'] += 1
                            self.stats['bytes_saved'] += result['size']
                        else:
                            seen_hashes.add(img_hash)
                            self.stats['images_kept'] += 1
                    else:
                        self.stats['images_kept'] += 1

            # Remove directory if empty
            try:
                if not any(img_dir.iterdir()):
                    img_dir.rmdir()
                    print(f"   ✓ Removed empty directory")
            except:
                pass

    def print_summary(self):
        """Print final summary"""
        print("\n" + "=" * 70)
        print("PROCESSING COMPLETE")
        print("=" * 70)
        print(f"PDFs processed:           {self.stats['pdfs_processed']}")
        print(f"PDFs failed:              {self.stats['pdfs_failed']}")
        print(f"Pages extracted:          {self.stats['pages_extracted']:,}")
        print(f"Images extracted:         {self.stats['images_extracted']:,}")
        print(f"Images protected:         {self.stats['images_protected']:,}")
        print(f"Images deleted:           {self.stats['images_deleted']:,}")
        print(f"  - By filename:          {self.stats['deleted_by_name']:,}")
        print(f"  - Simple shapes:        {self.stats['deleted_simple_shapes']:,}")
        print(f"  - Blank/solid:          {self.stats['deleted_blank']:,}")
        print(f"  - Tiny (<2KB):          {self.stats['deleted_tiny']:,}")
        print(f"  - Icons (<50px):        {self.stats['deleted_icon']:,}")
        print(f"  - Duplicates:           {self.stats['deleted_duplicate']:,}")
        print(f"Images kept:              {self.stats['images_kept']:,}")
        print(f"Space saved:              {self.stats['bytes_saved'] / (1024*1024):.1f} MB")

    def run(self):
        """Main processing pipeline"""
        print("=" * 70)
        print("CONSTRUCTION DOCUMENT PROCESSOR")
        print("=" * 70)
        print(f"Base directory: {self.base_dir}")
        print(f"CPU workers: {self.workers}")
        print()

        # Find PDFs
        pdfs = self.find_pdfs_recursive()
        if not pdfs:
            print("No PDFs found!")
            return

        print(f"Found {len(pdfs)} PDFs to process")
        print()

        # Extract PDFs
        for pdf in pdfs:
            self.extract_pdf(pdf)

        # Cleanup images
        self.cleanup_images()

        # Print summary
        self.print_summary()

if __name__ == "__main__":
    base_dir = os.getcwd()

    print("\n⚡ ONE SCRIPT TO RULE THEM ALL")
    print("\nThis will:")
    print("  1. Find all PDFs recursively (including subdirectories)")
    print("  2. Extract each PDF to markdown + images")
    print("  3. Clean up images using fast parallel processing")
    print("  4. Protect shop drawings, RFIs, submittals")
    print(f"\nWorking directory: {base_dir}")

    response = input("\nProceed? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborting.")
        sys.exit(0)

    processor = ConstructionDocProcessor(base_dir)
    processor.run()
