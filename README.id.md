# ZEX — ZTV Extractor

**Bahasa:** [🇮🇩 Bahasa Indonesia](#bahasa-indonesia)

---

<a id="bahasa-indonesia"></a>

# 🇮🇩 Bahasa Indonesia

ZEX (ZTV Extractor) adalah script Python untuk memeriksa halaman film di Cinema Zetware, mendeteksi pemutar video berbasis `vsembed`, dan mengidentifikasi manifest HLS (`master.m3u8`) beserta pilihan resolusi yang tersedia.

## Fitur

- Membuka halaman film menggunakan Chromium melalui Playwright.
- Mengambil judul film dari elemen HTML `h1`.
- Mengidentifikasi TMDB ID dari URL halaman.
- Menemukan iframe player `vsembed` dan iframe bersarang.
- Mendeteksi URL `master.m3u8` melalui respons jaringan.
- Memeriksa status pemutaran video.
- Mengurai manifest HLS untuk memperoleh resolusi dan URL stream.
- Menampilkan hasil pemeriksaan dalam format terminal yang rapi.

## Persyaratan

- Python 3.9 atau lebih baru.
- Playwright untuk Python.
- Browser Chromium yang didukung Playwright.
- Koneksi internet.
- Akses yang sah ke halaman dan stream yang diperiksa.

## Instalasi

### 1. Siapkan proyek

Simpan script sebagai `extract.py`.

```text
ZEx/
├── extract.py
├── requirements.txt
├── README.md
└── .gitignore
```

### 2. Instal dependensi

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Jika perintah `python` tidak tersedia, gunakan `python3`.

Isi `requirements.txt`:

```text
playwright
```

## Penggunaan

Jalankan script dengan URL halaman film sebagai argumen:

```bash
python extract.py "https://cinema.zetware.id/watch/tmdb-mov-24428"
```

URL tersebut merupakan contoh halaman film yang akan diperiksa. Anda dapat menggantinya dengan URL lain yang dapat diakses dan berhak Anda periksa.

### Parameter dan komponen

| Parameter / Komponen | Keterangan                                                |
| -------------------- | --------------------------------------------------------- |
| `url`                | URL halaman film yang diberikan saat menjalankan script   |
| `page.goto(url)`     | Membuka halaman berdasarkan URL tersebut                  |
| `vsembed`            | Pola iframe player yang dicari script                     |
| `master.m3u8`        | Manifest HLS yang diperiksa untuk menemukan varian stream |

## Alur Kerja

1. Membuka halaman film menggunakan Chromium.
2. Membaca judul dan mengidentifikasi TMDB ID.
3. Memantau respons jaringan untuk mendeteksi `master.m3u8`.
4. Menemukan iframe `vsembed` dan iframe player bersarang.
5. Mencoba mengaktifkan player dan memeriksa status pemutaran.
6. Mengurai manifest HLS untuk memperoleh resolusi yang diumumkan server.
7. Menampilkan hasil di terminal.

## Contoh Hasil

```text
═════════════════════════════════════════════════════════════════
              🎬 HASIL EKSTRAKSI VIDEO STREAMING 🎬
═════════════════════════════════════════════════════════════════
 📌 Judul Film  : Contoh Judul Film
 🆔 TMDB ID     : 24428
─────────────────────────────────────────────────────────────────
 📐 DAFTAR RESOLUSI & STREAM URL TERSEDIA:
─────────────────────────────────────────────────────────────────
 🟢 [ 360P ] : URL stream sesuai hasil pemeriksaan
 🟢 [ 720P ] : URL stream sesuai hasil pemeriksaan
═════════════════════════════════════════════════════════════════
```

_Hasil di atas hanya ilustrasi. Resolusi dan URL sebenarnya bergantung pada manifest yang dikirim server._

## Pemecahan Masalah

**`TimeoutError` saat mencari `h1`**

Pastikan URL benar, halaman dapat diakses, dan elemen `h1` tersedia. Halaman yang lambat atau perubahan struktur HTML dapat menyebabkan timeout.

**Iframe `vsembed` tidak ditemukan**

Periksa apakah halaman masih menggunakan pola iframe `vsembed`. Jika struktur embed berubah, selector pada script mungkin perlu disesuaikan.

**URL `master.m3u8` tidak tertangkap**

Manifest mungkin belum diminta oleh player, menggunakan format berbeda, atau memakai mekanisme streaming lain. Listener jaringan harus dipasang sebelum aktivitas player yang memicu permintaan manifest.

**Tidak ada resolusi yang ditampilkan**

Pastikan manifest yang tertangkap merupakan master playlist HLS. Playlist media biasa tidak selalu memiliki entri `#EXT-X-STREAM-INF`.

**Gagal mengambil manifest**

Server mungkin memerlukan cookie, header, atau token sesi. Permintaan menggunakan `urllib` tidak otomatis mewarisi sesi Chromium.

## Catatan Teknis

- Resolusi dalam manifest tidak menjamin setiap varian dapat diputar.
- URL stream dapat bersifat sementara atau memerlukan sesi autentikasi.
- Perubahan struktur halaman dan player dapat memerlukan penyesuaian script.
- Gunakan hanya pada konten yang Anda berwenang untuk akses dan pemeriksaannya. Jangan melewati autentikasi atau kontrol akses tanpa izin.

---
