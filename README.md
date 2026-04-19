# Abogado Arch KG

Image toolkit untuk file arsip visual novel **Shuumatsu no Sugoshikata ～The World is Drawing to an W/end.～** berbasis Abogado Engine.

---

## Apa Ini?

Game ini menyimpan semua aset gambarnya dalam format biner proprietary bernama `.KG`, yang dikemas ke dalam satu file arsip besar berekstensi `.DSK`. Arsip tersebut diindeks oleh file pasangannya berekstensi `.PFT`, yang menyimpan daftar nama file, posisi offset, dan ukuran slot masing-masing gambar di dalam arsip.

Toolkit ini hadir untuk menjembatani semua itu — dari membongkar arsip, mengonversi gambar ke format yang bisa diedit, mengompresi ulang hasil editan kembali ke format `.KG`, hingga menyuntikkan file yang sudah dimodifikasi langsung ke dalam arsip tanpa perlu membongkar ulang semuanya.

Format `.KG` sendiri mendukung tiga kedalaman warna: **8bpp** (indexed/palette), **24bpp** (RGB), dan **32bpp** (RGBA). Masing-masing punya struktur header dan algoritma kompresi yang berbeda, dan toolkit ini menangani ketiganya secara otomatis.

---

## Struktur File

| File | Peran |
|---|---|
| `ArcKGPACK.py` | Mengonversi file `.png` kembali ke format `.KG` dengan kompresi yang sesuai |
| `ArcPACK.py` | Generic packer untuk membangun ulang arsip `.DSK` dari nol |
| `ArcPATCH.py` | Menyuntikkan file `.KG` yang sudah dimodifikasi ke dalam arsip `.DSK` secara langsung |

---

## Tentang `kg_metadata.json`

Ketika gambar diekstrak dari arsip, informasi tentang kedalaman warna aslinya (8bpp, 24bpp, atau 32bpp) disimpan dalam sebuah file `kg_metadata.json` di folder hasil ekstrak. File ini penting — saat proses packing ulang, `ArcKGPACK.py` membaca metadata ini untuk memastikan setiap gambar dikemas kembali dalam format BPP yang sama persis dengan aslinya. Jika gambar yang aslinya 8bpp dikemas sebagai 24bpp, game bisa gagal memuatnya atau tampilannya akan rusak.

---

## Cara Pakai

Alur kerjanya terdiri dari tiga tahap utama: **pack → patch**, dengan satu tahap ekstrak yang biasanya sudah dilakukan sebelumnya oleh tool lain (misalnya GARbro atau tool serupa).

### Tahap 1 — Konversi PNG ke Format KG

Setelah selesai mengedit file gambar dalam format `.png`, jalankan packer untuk mengonversinya kembali ke format `.KG`:

```bash
# Memproses satu file
python ArcKGPACK.py gambar.png

# Memproses seluruh folder sekaligus
python ArcKGPACK.py folder_gambar/
```

Hasil konversi akan disimpan otomatis ke dalam subfolder bernama `packed_kg/` di dalam folder yang sama. Jika `kg_metadata.json` ditemukan di folder tersebut, packer akan menggunakannya untuk menentukan BPP target setiap gambar. Jika tidak ada, packer akan mencoba mendeteksi format secara otomatis.

### Tahap 2 — Patch ke Arsip DSK

Setelah file `.KG` siap, suntikkan langsung ke dalam arsip `.DSK` tanpa perlu membongkar atau membangun ulang arsip dari nol:

```bash
python ArcPATCH.py GRAPHIC.dsk GRAPHIC.pft folder_packed_kg/
```

`ArcPATCH.py` bekerja secara **in-place** — hanya file yang ada di dalam folder patch yang akan diganti. File lain yang tidak disentuh akan dibiarkan apa adanya. Satu catatan penting: ukuran file hasil pack tidak boleh melebihi ukuran slot aslinya yang tercatat di `.PFT`, karena offset di arsip tidak bisa digeser. Jika lebih besar, file tersebut akan dilewati dan diberi tanda `[Skip]`.

### Tentang ArcPACK

`ArcPACK.py` digunakan jika ingin membangun ulang arsip `.DSK` dari nol, misalnya saat menambahkan file baru yang sebelumnya tidak ada di arsip original. Penggunaan ini lebih jarang diperlukan dibanding `ArcPATCH.py`.

---

## Requirements

Tool ini membutuhkan **Python 3.x** dan library **Pillow** untuk pemrosesan gambar. Instalasi dependensi bisa dilakukan dengan:

```bash
pip install Pillow
```

---

## Struktur File Arsip Game

| File | Keterangan |
|---|---|
| `GRAPHIC.DSK` (atau nama lain) | Arsip utama yang berisi semua file `.KG` |
| `GRAPHIC.PFT` | File indeks pasangan `.DSK`, berisi nama, offset, dan ukuran tiap file |
| `kg_metadata.json` | Metadata BPP hasil ekstrak, dibaca saat proses packing ulang |

---

## Sebelum Mulai

Selalu **backup file `.DSK` dan `.PFT` original** sebelum menjalankan proses patch. Operasi patch menulis langsung ke file arsip secara permanen, dan tidak ada mekanisme undo otomatis.

---

## Disclaimer

Toolkit ini dibuat semata-mata untuk keperluan edukasi, penelitian, dan modifikasi personal. Pengguna bertanggung jawab penuh untuk memastikan penggunaannya sesuai dengan aturan copyright dan Terms of Service dari game original.

---

## Kontribusi

Pull request dan issue sangat welcome. Untuk perubahan besar, sebaiknya buka issue terlebih dahulu agar bisa didiskusikan sebelum implementasi.
