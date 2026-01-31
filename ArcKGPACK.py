import struct
import sys
import os
import json
import glob
from PIL import Image


class BitWriter:
    def __init__(self):
        self.data = bytearray()
        self.current_byte = 0
        self.bit_pos = 8 
    def write_bits(self, value, count):
        while count > 0:
            take = min(count, self.bit_pos)
            shift = self.bit_pos - take
            bits_to_write = (value >> (count - take)) & ((1 << take) - 1)
            self.current_byte |= (bits_to_write << shift)
            self.bit_pos -= take
            count -= take
            if self.bit_pos == 0:
                self.data.append(self.current_byte); self.current_byte = 0; self.bit_pos = 8
    def flush(self):
        if self.bit_pos < 8: self.data.append(self.current_byte); self.current_byte = 0; self.bit_pos = 8
    def get_bytes(self): self.flush(); return bytes(self.data)

def encode_count(writer, count):
    if count < 4 and count > 0: writer.write_bits(count, 2)
    elif count < 19: writer.write_bits(0, 2); writer.write_bits(count - 3, 4)
    elif count < 256: writer.write_bits(0, 2); writer.write_bits(0, 4); writer.write_bits(count, 8)
    else: writer.write_bits(0, 2); writer.write_bits(0, 4); writer.write_bits(0, 8); writer.write_bits(count, 16)

def compress_channel(data):
    writer = BitWriter()
    length = len(data)
    if length == 0: return b""
    writer.write_bits(data[0], 8)
    if length > 1: writer.write_bits(data[1], 8)
    i = 2
    while i < length:
        run_length = 0; current_val = data[i-1]
        max_run = min(length - i, 65535)
        for k in range(max_run):
            if data[i + k] == current_val: run_length += 1
            else: break
        if run_length >= 2:
            writer.write_bits(1, 1); writer.write_bits(0, 1)
            encode_count(writer, run_length); i += run_length
        else:
            writer.write_bits(0, 1); writer.write_bits(1, 1)
            writer.write_bits(data[i], 8); i += 1
    return writer.get_bytes()


def force_convert_8bpp(img):
    """
    Mengubah gambar RGB/RGBA menjadi 8-bit Indexed (Palette)
    Menggunakan Fast Octree (method=2) agar support alpha channel transparansi.
    """
    print("   -> Mengonversi otomatis ke 8bpp (Fast Octree)...")

    return img.quantize(colors=256, method=2, kmeans=0, dither=Image.Dither.FLOYDSTEINBERG)


def pack_single_file(image_path, output_folder, metadata=None):
    filename = os.path.basename(image_path)
    print(f"--- Processing: {filename} ---")
    
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error membuka gambar: {e}")
        return

    # 1. Cek Metadata JSON untuk target BPP
    target_bpp = 0 
    if metadata and filename in metadata:
        info = metadata[filename]
        target_bpp = info.get("bpp", 0)
        print(f"   [Metadata] Original BPP: {target_bpp}")
    
   
    if target_bpp == 8 and img.mode != 'P':
        img = force_convert_8bpp(img)
    

    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    width, height = img.size
    

    is_indexed = (img.mode == 'P')
    
    compressed_data = bytearray()
    
    if is_indexed:

        bpp_code = 1 
        raw_indices = img.tobytes()
        compressed_data.extend(compress_channel(raw_indices))
        
 
        pal = img.getpalette()
        palette_buffer = bytearray(1024)
        if pal:
            count = min(len(pal)//3, 256)
            for i in range(count):
                r, g, b = pal[i*3], pal[i*3+1], pal[i*3+2]
                palette_buffer[i*4] = b; palette_buffer[i*4+1] = g; palette_buffer[i*4+2] = r; palette_buffer[i*4+3] = 0
    else:

        bpp_code = 2 
        img = img.convert('RGB')
        r, g, b = img.split()
        compressed_data.extend(compress_channel(b.tobytes()))
        compressed_data.extend(compress_channel(g.tobytes()))
        compressed_data.extend(compress_channel(r.tobytes()))

    # 4. Buat Header
    header = bytearray(0x30)
    struct.pack_into("2sBB", header, 0, b'KG', 0, bpp_code) 
    struct.pack_into("<HH", header, 4, width, height)
    
    current_pos = 0x30
    if is_indexed:
        struct.pack_into("<I", header, 0xC, current_pos)
        current_pos += 1024
    else:
        struct.pack_into("<I", header, 0xC, 0)
        
    struct.pack_into("<I", header, 0x10, current_pos) 
    struct.pack_into("<I", header, 0x2C, 0) 

    # 5. Save File
    out_name = os.path.splitext(filename)[0] + ".KG"
    out_path = os.path.join(output_folder, out_name)
    
    with open(out_path, "wb") as f:
        f.write(header)
        if is_indexed: f.write(palette_buffer)
        f.write(compressed_data)
        
    print(f"   [Sukses] Saved -> {out_name} (Mode: {'8bpp' if is_indexed else '24bpp'})")

def process_pack(input_target):

    if os.path.isdir(input_target):
        work_dir = input_target
        files = glob.glob(os.path.join(work_dir, "*.png"))
    else:
        work_dir = os.path.dirname(input_target)
        files = [input_target]


    metadata = {}
    json_path = os.path.join(work_dir, "kg_metadata.json")
    if os.path.exists(json_path):
        print(f"Metadata ditemukan: {json_path}")
        try:
            with open(json_path, "r") as jf:
                metadata = json.load(jf)
        except:
            print("Gagal membaca metadata JSON. Menggunakan auto-detect.")


    output_folder = os.path.join(work_dir, "packed_kg")
    os.makedirs(output_folder, exist_ok=True)

    for file_path in files:
        pack_single_file(file_path, output_folder, metadata)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ArcKGPACK.py <folder_png_atau_file>")
    else:
        process_pack(sys.argv[1])