#!/usr/bin/env python3
"""
ArcPATCH.py - DSK Archive Patcher
Patches individual files in DSK archive without repacking everything
"""

import struct
import os
import sys

def read_pft(pft_path):
    """Read PFT index file."""
    with open(pft_path, "rb") as f:
        header_size, cluster_size, count = struct.unpack("<HHi", f.read(8))
        f.seek(header_size)
        
        entries = []
        for _ in range(count):
            raw_name, offset_idx, size = struct.unpack("<8sII", f.read(16))
            name = raw_name.split(b'\0')[0].decode('ascii', errors='ignore').strip()
            entries.append({
                'name': name,
                'offset_idx': offset_idx,
                'size': size
            })
        
        return header_size, cluster_size, entries

def patch_dsk(dsk_path, pft_path, patch_folder):
    """
    Patch files in DSK archive.
    
    Args:
        dsk_path: Path to .dsk file
        pft_path: Path to .pft file
        patch_folder: Folder containing modified files
    """
    
    if not os.path.exists(dsk_path):
        print(f"[Error] DSK file not found: {dsk_path}")
        return False
    
    if not os.path.exists(pft_path):
        print(f"[Error] PFT file not found: {pft_path}")
        return False
    
    if not os.path.exists(patch_folder):
        print(f"[Error] Patch folder not found: {patch_folder}")
        return False
    
    print(f"[Info] Reading PFT: {pft_path}")
    header_size, cluster_size, entries = read_pft(pft_path)
    
    print(f"[Info] Cluster size: {cluster_size}")
    print(f"[Info] Total files: {len(entries)}")
    
    # Determine file extension
    default_ext = ".KG"
    for ext in ['.KG', '.kg', '.SCF', '.scf', '.ADP', '.adp']:
        test_files = [f for f in os.listdir(patch_folder) if f.endswith(ext)]
        if test_files:
            default_ext = ext
            break
    
    print(f"[Info] Using extension: {default_ext}")
    print(f"\n[Info] Patching DSK: {dsk_path}")
    
    patched_count = 0
    skipped_count = 0
    
    try:
        with open(dsk_path, "r+b") as dsk:
            for entry in entries:
                filename = entry['name'] + default_ext
                file_path = os.path.join(patch_folder, filename)
                
                # Skip if file doesn't exist (not modified)
                if not os.path.exists(file_path):
                    skipped_count += 1
                    continue
                
                # Read new file data
                with open(file_path, "rb") as f:
                    data = f.read()
                
                real_size = len(data)
                slot_size = entry['size']
                
                # Check size
                if real_size > slot_size:
                    print(f"[Skip] {filename} too large ({real_size} > {slot_size})")
                    skipped_count += 1
                    continue
                
                # Calculate offset and write
                offset = entry['offset_idx'] * cluster_size
                dsk.seek(offset)
                dsk.write(data)
                
                # Pad with zeros
                if real_size < slot_size:
                    dsk.write(b'\x00' * (slot_size - real_size))
                
                print(f"[Patched] {filename} @ offset {offset} ({real_size} bytes)")
                patched_count += 1
        
        print(f"\n[Success] Patching complete!")
        print(f"  Patched: {patched_count} files")
        print(f"  Skipped: {skipped_count} files")
        return True
        
    except Exception as e:
        print(f"[Error] Failed during patching: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("=" * 60)
        print("DSK Archive Patcher")
        print("=" * 60)
        print("\nCara penggunaan:")
        print("  python ArcPATCH.py <file.dsk> <file.pft> <patch_folder>")
        print("\nContoh:")
        print("  python ArcPATCH.py GRAPHIC.dsk GRAPHIC.pft GRAPHIC_modified")
        print("\nPatch folder harus berisi file-file yang ingin diganti.")
        print("File yang tidak ada di folder akan diabaikan (tidak diubah).")
        print("\nPATCH MODE: Mengubah file di tempat TANPA membuat archive baru.")
        print("=" * 60)
    else:
        dsk_file = sys.argv[1]
        pft_file = sys.argv[2]
        patch_dir = sys.argv[3]
        
        patch_dsk(dsk_file, pft_file, patch_dir)
