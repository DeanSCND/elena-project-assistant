#!/usr/bin/env python3
"""
Fast image cleanup - Whitelist-only approach with parallel processing
Major speedup: Only opens images that aren't protected, uses multiprocessing
"""

import os
import sys
from pathlib import Path
import shutil
from multiprocessing import Pool, cpu_count
from PIL import Image
import imagehash

# WHITELIST: Never delete images from these source files
PROTECTED_PATTERNS = [
    'SAF-',           # Shop drawings
    'Submittal',      # Submittal packages
    'Detail',         # Detail sheets
    'Schedule',       # Equipment schedules
    'Diagram',        # System diagrams
    '_SD_',           # Shop Drawing prefix
    'RFI',            # Requests for Information
]

# Only delete if filename contains these
KNOWN_LOGOS = [
    'sobeys', 'safeway', 'logo', 'header', 'footer',
    'watermark', 'banner', 'branding'
]

def is_protected_source(img_dir_name):
    """Check if image comes from protected source document"""
    for pattern in PROTECTED_PATTERNS:
        if pattern in img_dir_name:
            return True
    return False

def is_obvious_logo_by_name(img_filename):
    """Check if filename suggests logo (no image opening required)"""
    filename_lower = img_filename.lower()
    for logo_term in KNOWN_LOGOS:
        if logo_term in filename_lower:
            return True
    return False

def analyze_image(img_path):
    """Analyze a single image - designed for parallel execution"""
    try:
        file_size = os.path.getsize(img_path)

        # Skip very small files without opening (likely tiny icons)
        if file_size < 2000:  # 2KB
            return {'path': img_path, 'delete': True, 'reason': 'tiny', 'size': file_size}

        # Open image
        img = Image.open(img_path)

        # Check if blank/white
        extrema = img.convert('L').getextrema()
        if extrema == (255, 255):
            return {'path': img_path, 'delete': True, 'reason': 'blank', 'size': file_size}

        # Check if very small dimensions
        if img.width < 50 and img.height < 50:
            return {'path': img_path, 'delete': True, 'reason': 'icon', 'size': file_size}

        # Get hash for duplicate detection
        img_hash = str(imagehash.average_hash(img))

        return {'path': img_path, 'delete': False, 'hash': img_hash, 'size': file_size}

    except Exception as e:
        # If we can't open it, keep it (might be corrupted but better safe)
        return {'path': img_path, 'delete': False, 'error': str(e), 'size': 0}

def find_image_dirs_recursive(base_dir):
    """Find all *_images directories recursively"""
    image_dirs = []
    for root, dirs, files in os.walk(base_dir):
        for dirname in dirs:
            if dirname.endswith('_images'):
                full_path = os.path.join(root, dirname)
                # Skip backup directories
                if '__backup__' not in full_path:
                    image_dirs.append(full_path)
    return sorted(image_dirs)

def cleanup_images_fast(base_dir, create_backup=True, workers=None):
    """Fast cleanup using whitelist and parallel processing"""

    if workers is None:
        workers = max(1, cpu_count() - 1)  # Leave one CPU free

    print("=" * 70)
    print("FAST IMAGE CLEANUP - Whitelist + Parallel Processing")
    print("=" * 70)
    print(f"CPU workers: {workers}")
    print("\nProtected patterns (images from these will be KEPT):")
    for pattern in PROTECTED_PATTERNS:
        print(f"  ✓ {pattern}")

    # Create backup
    if create_backup:
        backup_dir = os.path.join(base_dir, "__images_backup__")
        if os.path.exists(backup_dir):
            print(f"\n✓ Using existing backup: {backup_dir}")
        else:
            print(f"\n✓ Creating backup: {backup_dir}")
            os.makedirs(backup_dir, exist_ok=True)

    # Find all image directories
    image_dirs = find_image_dirs_recursive(base_dir)
    print(f"\nFound {len(image_dirs)} image directories")

    stats = {
        'total': 0,
        'protected': 0,
        'deleted_by_name': 0,
        'deleted_blank': 0,
        'deleted_tiny': 0,
        'deleted_icon': 0,
        'deleted_duplicate': 0,
        'kept': 0,
        'bytes_saved': 0,
        'skipped_analysis': 0  # Protected images we didn't even analyze
    }

    seen_hashes = set()

    for dir_path in image_dirs:
        dir_name = os.path.basename(dir_path)
        rel_path = os.path.relpath(dir_path, base_dir)

        # Backup this directory
        if create_backup:
            backup_path = os.path.join(backup_dir, rel_path.replace('/', '_').replace('\\', '_'))
            if not os.path.exists(backup_path):
                try:
                    shutil.copytree(dir_path, backup_path)
                except Exception as e:
                    print(f"⚠️  Couldn't backup {dir_name}: {e}")

        # Check if this is a protected source
        is_protected = is_protected_source(dir_name)

        if is_protected:
            # Don't even scan these - just count and skip
            images = [f for f in os.listdir(dir_path)
                     if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            count = len(images)
            stats['total'] += count
            stats['protected'] += count
            stats['kept'] += count
            stats['skipped_analysis'] += count
            print(f"\n🛡️  PROTECTED: {rel_path} ({count} images, skipped analysis)")
            continue

        print(f"\n📋 Processing: {rel_path}")

        # Get all images
        images = [f for f in os.listdir(dir_path)
                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

        if not images:
            continue

        stats['total'] += len(images)

        # First pass: Delete by filename (no image opening needed)
        remaining_images = []
        for img_file in images:
            if is_obvious_logo_by_name(img_file):
                img_path = os.path.join(dir_path, img_file)
                file_size = os.path.getsize(img_path)
                os.remove(img_path)
                stats['deleted_by_name'] += 1
                stats['bytes_saved'] += file_size
            else:
                remaining_images.append(img_file)

        if stats['deleted_by_name'] > 0:
            print(f"  Deleted {stats['deleted_by_name']} by filename")

        if not remaining_images:
            continue

        # Second pass: Analyze remaining images IN PARALLEL
        img_paths = [os.path.join(dir_path, f) for f in remaining_images]

        print(f"  Analyzing {len(img_paths)} images with {workers} workers...")

        with Pool(workers) as pool:
            results = pool.map(analyze_image, img_paths)

        # Process results and delete/track
        for result in results:
            if result.get('delete'):
                os.remove(result['path'])
                stats['bytes_saved'] += result['size']
                reason = result.get('reason', 'unknown')
                if reason == 'blank':
                    stats['deleted_blank'] += 1
                elif reason == 'tiny':
                    stats['deleted_tiny'] += 1
                elif reason == 'icon':
                    stats['deleted_icon'] += 1
            else:
                # Check for duplicates
                img_hash = result.get('hash')
                if img_hash:
                    if img_hash in seen_hashes:
                        os.remove(result['path'])
                        stats['deleted_duplicate'] += 1
                        stats['bytes_saved'] += result['size']
                    else:
                        seen_hashes.add(img_hash)
                        stats['kept'] += 1
                else:
                    stats['kept'] += 1

        # Remove directory if empty
        try:
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                print(f"  ✓ Removed empty directory")
        except:
            pass

    # Final report
    print("\n" + "=" * 70)
    print("CLEANUP COMPLETE")
    print("=" * 70)
    print(f"Total images:             {stats['total']:,}")
    print(f"Protected (not analyzed): {stats['protected']:,}")
    print(f"Deleted by filename:      {stats['deleted_by_name']:,}")
    print(f"Deleted - Blank:          {stats['deleted_blank']:,}")
    print(f"Deleted - Tiny:           {stats['deleted_tiny']:,}")
    print(f"Deleted - Icon:           {stats['deleted_icon']:,}")
    print(f"Deleted - Duplicates:     {stats['deleted_duplicate']:,}")

    total_deleted = (stats['deleted_by_name'] + stats['deleted_blank'] +
                    stats['deleted_tiny'] + stats['deleted_icon'] + stats['deleted_duplicate'])

    if stats['total'] > 0:
        print(f"Total deleted:            {total_deleted:,} ({(total_deleted / stats['total'] * 100):.1f}%)")
        print(f"Images kept:              {stats['kept']:,} ({(stats['kept'] / stats['total'] * 100):.1f}%)")

    print(f"Space saved:              {stats['bytes_saved'] / (1024*1024):.1f} MB")
    print(f"\n⚡ Performance: Skipped analysis on {stats['skipped_analysis']:,} protected images")

    return stats

if __name__ == "__main__":
    base_dir = os.getcwd()

    print("\n⚡ FAST CLEANUP MODE")
    print("\nOptimizations:")
    print("  ✓ Whitelist approach - protected images aren't even opened")
    print("  ✓ Parallel processing - uses all CPU cores")
    print("  ✓ Filename-first deletion - no image opening for obvious logos")
    print(f"\nWorking directory: {base_dir}")

    response = input("\nProceed? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborting.")
        sys.exit(0)

    cleanup_images_fast(base_dir, create_backup=True)
