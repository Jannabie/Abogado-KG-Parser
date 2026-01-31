import struct
import os
import sys

def read_pft_template(pft_path):
    """Membaca PFT asli untuk mendapatkan urutan dan setting header"""
    entries = []
    header_info = {}
    
    with open(pft_path, "rb") as f:

        header_bytes = f.read(8)
        header_size, cluster_size, count = struct.unpack("<HHi", header_bytes)
        
        header_info = {
            "header_size": header_size,
            "cluster_size": cluster_size,
            "count": count
        }
        
        print(f"[Template] Header Size: {header_size}, Cluster: {cluster_size}, Files: {count}")
        

        f.seek(header_size)
        
        for i in range(count):
            entry_data = f.read(16)
            if len(entry_data) < 16:
                break
                
            raw_name, _, _ = struct.unpack("<8sII", entry_data)
            

            name = raw_name.split(b'\0', 1)[0].decode('ascii', errors='ignore')
            entries.append(name)
            
    return header_info, entries

def find_file_in_folder(base_name, folder_path):
    """Mencari file di folder dengan nama dasar tertentu (mengabaikan ekstensi)"""

    target = base_name.upper()
    
    for filename in os.listdir(folder_path):
        name_part = os.path.splitext(filename)[0].upper()
        if name_part == target:
            return os.path.join(folder_path, filename)
            
    return None

def repack_with_template(template_pft, input_folder, output_base):
    if not os.path.exists(template_pft):
        print("Error: File template PFT tidak ditemukan.")
        return

    print(f"--- Membaca Template: {template_pft} ---")
    header_info, file_order = read_pft_template(template_pft)
    
    out_dsk = output_base + ".dsk"
    out_pft = output_base + ".pft"
    
    print(f"--- Memulai Repack ke: {out_dsk} ---")
    
    files_written = 0
    missing_files = []
    
    with open(out_pft, 'wb') as f_pft, open(out_dsk, 'wb') as f_dsk:
        

        f_pft.write(struct.pack("<HHi", 
                                header_info['header_size'], 
                                header_info['cluster_size'], 
                                header_info['count']))
        

        if header_info['header_size'] > 8:
            f_pft.write(b'\x00' * (header_info['header_size'] - 8))
            
        cluster_size = header_info['cluster_size']
        if cluster_size == 0: cluster_size = 2048
        

        for name in file_order:

            file_path = find_file_in_folder(name, input_folder)
            
            if file_path:
                file_size = os.path.getsize(file_path)
                

                current_pos = f_dsk.tell()
                remainder = current_pos % cluster_size
                if remainder != 0:
                    padding = cluster_size - remainder
                    f_dsk.write(b'\x00' * padding)
                    current_pos += padding
                

                offset_index = current_pos // cluster_size
                

                with open(file_path, 'rb') as src:
                    f_dsk.write(src.read())
                

                name_bytes = name.encode('ascii', errors='ignore')[:8].ljust(8, b'\x00')
                f_pft.write(struct.pack("<8sII", name_bytes, offset_index, file_size))
                

                files_written += 1
            else:
                print(f"[WARNING] File hilang: {name}. Membuat entry kosong (0 byte).")
                missing_files.append(name)
                

                name_bytes = name.encode('ascii', errors='ignore')[:8].ljust(8, b'\x00')
                f_pft.write(struct.pack("<8sII", name_bytes, 0, 0))

    print("\n--- Selesai ---")
    print(f"Total file ditulis: {files_written}/{header_info['count']}")
    if missing_files:
        print(f"File yang hilang ({len(missing_files)}): {', '.join(missing_files[:5])}...")
    else:
        print("Semua file lengkap dan urutan sesuai original!")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Cara Pakai: python ArcPACK.py <PFT_ASLI> <FOLDER_DATA> <NAMA_OUTPUT>")
        print("Contoh: python ArcPACK.py GRAPHIC.PFT<ORIGINAL> extracted_folder GRAPHIC_NEW")
    else:
        orig_pft = sys.argv[1]
        inp_folder = sys.argv[2]
        out_name = sys.argv[3]
        repack_with_template(orig_pft, inp_folder, out_name)