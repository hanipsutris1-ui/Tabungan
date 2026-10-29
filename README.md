# Tabungan

Aplikasi pencatat keuangan satu file (HTML) dengan tiga tab: **Dompetku** (keuangan pribadi/keluarga), **Warga** (tabungan warga per periode) dan **Pribadi** (khusus admin).
Dibuat untuk istri tercinta Nyonya Sara oleh Nurrachman.

## Fitur
- Setoran, penarikan, periode, rekap dan bagikan ke WhatsApp (gambar/teks)
- Dompetku: pemasukan/pengeluaran, kategori, anggaran, perbandingan 6 bulan
- Backup/pulihkan (JSON), ekspor Excel/CSV
- Tema terang/gelap, hapus periode dan rekening
- Versi APK Android (WebView) dengan penyimpanan lokal

## Struktur
- `index.html`: seluruh aplikasi (HTML+CSS+JS)
- `apk/build.py`, `apk/shim.js`, `apk/icon.png`: pembuat APK
- `docs/`: catatan

## Membuat APK
Butuh APK WebView pembungkus sebagai templat (bukan bagian repo) dan Python + `cryptography`:

```
pip install cryptography
cp /lokasi/templat.apk template.apk
cd apk && python3 build.py Tabungan.apk
```
Kunci tanda tangan dibuat di `apk/release.key`. **Simpan kunci ini**; tanpa kunci yang sama, versi baru tidak bisa dipasang menimpa versi lama. Jangan di-commit.

## Catatan
Versi web memakai database artifact (koleksi: anggota, setoran, tarik, periode, pribadi, pset, ptarik, dkas, dcfg). Versi APK memakai penyimpanan lokal lewat `shim.js`.
