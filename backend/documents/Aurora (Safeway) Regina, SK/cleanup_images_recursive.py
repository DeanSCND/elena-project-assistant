#!/usr/bin/env python3
"""
Image cleanup script - Recursive with whitelist protection
Works with subdirectories
"""

import os
import sys
from pathlib import Path
import shutil
from PIL import Image
import imagehash

# WHITELIST: Never delete images from these source files
PROTECTED_PATTERNS = [
    'SAF-',           # Shop drawings (SAF-TRE-013, etc.)
    'Submittal',      # Submittal packages
    'Detail',         # Detail sheets
    'Schedule',       # Equipment schedules
    'Diagram',        # System diagrams
    '_SD_',           # Shop Drawing prefix
    'RFI',            # Requests for Information
]

# AGGRESSIVE DELETE: Only delete obvious branding
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

def is_obvious_logo(img_path, img_dir_name):
    """Only flag OBVIOUS logos/branding for deletion"""

    # Check filename
    filename = os.path.basename(img_path).lower()
    for logo_term in KNOWN_LOGOS:
        if logo_term in filename:
            return True

    # Check if directory name suggests branding
    dir_lower = img_dir_name.lower()
    if 'cover' in dir_lower or 'title' in dir_lower:
        return True

    # Very conservative size check (only tiny icons)
    if os.path.getsize(img_path) < 5000:  # 5KB
        return True

    # Very conservative dimension check (only actual icons)
    try:
        img = Image.open(img_path)
        if img.width < 50 and img.height < 50:  # 50px
            return True
    except Exception:
        pass

    return False

def is_all_white(img_path):
    """Check if image is completely blank/white"""
    try:
        img = Image.open(img_path)
        extrema = img.convert('L').getextrema()
        if extrema == (255, 255):
            return True
    except Exception:
        pass
    return False

def get_image_hash(img_path):
    """Get perceptual hash of image"""
    try:
        img = Image.open(img_path)
        return imagehash.average_hash(img)
    except Exception:
        return None

def find_image_dirs_recursive(base_dir):
    """Find all *_images directories recursively"""
    image_dirs = []
    for root, dirs, files in os.walk(base_dir):
        for dirname in dirs:
            if dirname.endswith('_images'):
                full_path = os.path.join(root, dirname)
                image_dirs.append(full_path)
    return sorted(image_dirs)

def cleanup_images_conservative(base_dir, create_backup=True):
    """Conservative cleanup - only delete OBVIOUS non-technical images"""

    print("=" * 70)
    print("IMAGE CLEANUP - RECURSIVE CONSERVATIVE MODE")
    print("=" * 70)
    print("\nProtected source patterns:")
    for pattern in PROTECTED_PATTERNS:
        print(f"  - {pattern}")

    # Create backup
    if create_backup:
        backup_dir = os.path.join(base_dir, "__images_backup__")
        if os.path.exists(backup_dir):
            print(f"\n⚠️  Backup already exists at: {backup_dir}")
            print("   Using existing backup (not overwriting)")
        else:
            print(f"\nCreating backup at: {backup_dir}")
            os.makedirs(backup_dir, exist_ok=True)

    # Find all image directories (including subdirectories)
    image_dirs = find_image_dirs_recursive(base_dir)

    # Filter out backup directory itself
    image_dirs = [d for d in image_dirs if '__backup__' not in d]

    print(f"\nFound {len(image_dirs)} image directories (including subdirectories)")

    stats = {
        'total': 0,
        'protected': 0,
        'deleted_obvious_logo': 0,
        'deleted_blank': 0,
        'deleted_duplicate': 0,
        'kept': 0,
        'bytes_saved': 0
    }

    seen_hashes = {}

    for dir_path in image_dirs:
        dir_name = os.path.basename(dir_path)

        # Get relative path for display
        rel_path = os.path.relpath(dir_path, base_dir)

        # Backup this directory
        if create_backup:
            backup_path = os.path.join(backup_dir, rel_path.replace('/', '_'))
            if not os.path.exists(backup_path):
                try:
                    shutil.copytree(dir_path, backup_path)
                except Exception as e:
                    print(f"Warning: Couldn't backup {dir_name}: {e}")

        # Check if this is a protected source
        is_protected = is_protected_source(dir_name)

        if is_protected:
            print(f"\n🛡️  PROTECTED: {rel_path} (keeping all images)")
        else:
            print(f"\n📋 Processing: {rel_path}")

        images = [f for f in os.listdir(dir_path)
                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

        for img_file in images:
            img_path = os.path.join(dir_path, img_file)
            stats['total'] += 1

            # Skip deletion for protected sources
            if is_protected:
                stats['protected'] += 1
                stats['kept'] += 1
                continue

            file_size = os.path.getsize(img_path)
            delete = False
            reason = ""

            # Check if completely blank
            if is_all_white(img_path):
                delete = True
                reason = "blank/white"
                stats['deleted_blank'] += 1

            # Check if obvious logo
            elif is_obvious_logo(img_path, dir_name):
                delete = True
                reason = "obvious logo/icon"
                stats['deleted_obvious_logo'] += 1

            # Check for duplicates
            else:
                img_hash = get_image_hash(img_path)
                if img_hash:
                    if img_hash in seen_hashes:
                        delete = True
                        reason = f"duplicate"
                        stats['deleted_duplicate'] += 1
                    else:
                        seen_hashes[img_hash] = img_file

            if delete:
                stats['bytes_saved'] += file_size
                os.remove(img_path)
            else:
                stats['kept'] += 1

        # Remove directory if empty
        try:
            remaining = os.listdir(dir_path)
            if not remaining:
                os.rmdir(dir_path)
                print(f"  ✓ Removed empty directory")
        except:
            pass

    # Final report
    print("\n" + "=" * 70)
    print("CLEANUP COMPLETE")
    print("=" * 70)
    print(f"Total images processed:   {stats['total']:,}")
    print(f"Protected (shop dwgs):    {stats['protected']:,}")
    print(f"Deleted - Blank images:   {stats['deleted_blank']:,}")
    print(f"Deleted - Obvious logos:  {stats['deleted_obvious_logo']:,}")
    print(f"Deleted - Duplicates:     {stats['deleted_duplicate']:,}")
    total_deleted = stats['deleted_blank'] + stats['deleted_obvious_logo'] + stats['deleted_duplicate']
    if stats['total'] > 0:
        print(f"Total deleted:            {total_deleted:,} ({(total_deleted / stats['total'] * 100):.1f}%)")
        print(f"Images kept:              {stats['kept']:,} ({(stats['kept'] / stats['total'] * 100):.1f}%)")
    print(f"Space saved:              {stats['bytes_saved'] / (1024*1024):.1f} MB")

    if create_backup:
        print(f"\nBackup location: {backup_dir}")

    return stats

if __name__ == "__main__":
    base_dir = os.getcwd()

    print("\n⚠️  CONSERVATIVE CLEANUP MODE (Recursive)")
    print("\nThis version will:")
    print("  ✓ SCAN subdirectories recursively")
    print("  ✓ KEEP ALL images from shop drawings (SAF-*, submittals, RFIs, etc.)")
    print("  ✓ Only delete OBVIOUS logos, blank images, and duplicates")
    print("  ✓ Use strict thresholds (5KB, 50px)")
    print(f"\nWorking directory: {base_dir}")

    response = input("\nProceed with conservative cleanup? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborting.")
        sys.exit(0)

    cleanup_images_conservative(base_dir, create_backup=True)
