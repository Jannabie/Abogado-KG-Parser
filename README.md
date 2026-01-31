# Abogado KG Parser

Archive tools untuk **Shuumatsu no Sugoshikata ~The World is Drawing to an W/end.~** - KiriKiri Engine

## Deskripsi

Tool untuk ekstrak dan repack file archive KiriKiri (format .xp3, .kg) dari visual novel berbasis KiriKiri engine. Berguna untuk modding, translation, atau ekstraksi asset.

## Fitur

- **Extract Archive**: Ekstrak file dari archive KG/XP3
- **Repack Archive**: Pack kembali file yang sudah dimodifikasi
- **Patch System**: Buat dan apply patch untuk update
- **Format Support**: Support untuk berbagai format KiriKiri

## File Utama

| File | Fungsi |
|------|--------|
| `ArcKG.py` | Ekstrak file dari archive KG |
| `ArcKGPACK.py` | Pack file ke format KG |
| `ArcPACK.py` | Generic archive packer |
| `ArcPATCH.py` | Buat dan apply patch file |
| `COMPARISON.md` | Dokumentasi perbandingan format |

## Cara Pakai

### 1. Extract Archive

```bash
python ArcKG.py archive.kg
```

File akan diekstrak ke folder `archive_extracted/`

### 2. Modifikasi File

Edit file yang sudah diekstrak sesuai kebutuhan (gambar, script, audio, dll)

### 3. Repack Archive

```bash
python ArcKGPACK.py archive_extracted/ archive_new.kg
```

### 4. Buat Patch (Optional)

```bash
python ArcPATCH.py archive_original.kg archive_new.kg patch.diff
```

## Requirements

- Python 3.x
- Modul standar Python (struct, os, sys)

## Struktur Archive KG

Archive KG biasanya berisi:
- File script (.ks, .tjs)
- Image asset (.png, .tlg)
- Audio files (.ogg, .wav)
- Video files (.mpg, .wmv)
- Font dan resource lainnya

## Tips

- Selalu backup file original sebelum modifikasi
- Perhatikan encoding text (biasanya Shift-JIS atau UTF-8)
- Ukuran file hasil repack mungkin berbeda dari original
- Test di game sebelum distribusi

## Catatan

Tool ini khusus untuk KiriKiri engine. Untuk engine lain (seperti format SCF), gunakan [Abogado-Parser](https://github.com/ObyyAVN/Abogado-Parser).

## Troubleshooting

**Archive tidak bisa dibuka**
- Pastikan format file benar (KG/XP3)
- Check apakah file ter-encrypt

**Repack gagal**
- Pastikan struktur folder sesuai dengan hasil extract
- Check permission file dan folder

**Game crash setelah repack**
- Verifikasi integritas file
- Pastikan tidak ada file yang corrupt
- Check format encoding text

## Disclaimer

Tool ini untuk keperluan edukasi dan research. Patuhi copyright dan ToS dari game original.

## Kontribusi

Pull request dan issue welcome. Diskusi di issue dulu untuk perubahan major.

## License

Lihat file LICENSE untuk detail.
