# ZEX — Video Stream Extractor

Script Python untuk memeriksa halaman film pada Cinema Zetware, mendeteksi pemutar video berbasis `vsembed`, dan mengidentifikasi URL master manifest HLS (`master.m3u8`) beserta pilihan resolusi yang tersedia.

## Fitur

- Membuka halaman film menggunakan Chromium melalui Playwright.
- Mengambil judul film dari elemen HTML `h1`.
- Mengidentifikasi TMDB ID dari URL halaman film.
- Menemukan iframe player `vsembed` dan struktur iframe bersarang.
- Mendeteksi URL `master.m3u8` melalui respons jaringan.
- Memeriksa status pemutaran video.
- Mengurai manifest HLS untuk memperoleh resolusi dan URL stream.
- Menampilkan hasil ekstraksi dalam format terminal yang rapi.

## Persyaratan

- Python 3.9 atau lebih baru.
- Playwright untuk Python.
- Browser Chromium yang didukung Playwright.
- Koneksi internet.
- Akses yang sah ke halaman dan stream yang diperiksa.

## Instalasi

### 1. Siapkan direktori proyek

Simpan script sebagai `extract.py`.

```text
zex/
├── extract.py
└── README.md
```

### 2. Instal dependensi

```bash
python -m pip install playwright
python -m playwright install chromium
```

Jika perintah `python` tidak tersedia, gunakan `python3`.

## Penggunaan

Jalankan script dengan URL halaman film sebagai argumen.

```bash
python extract.py "https://cinema.zetware.id/watch/tmdb-mov-24428"
```

URL tersebut merupakan contoh halaman film yang akan diperiksa.

### Parameter

| Parameter        | Keterangan                                                 |
| ---------------- | ---------------------------------------------------------- |
| `url`            | URL halaman film yang akan diperiksa                       |
| `page.goto(url)` | Membuka halaman berdasarkan URL yang diberikan             |
| `vsembed`        | Pola iframe player yang dicari oleh script                 |
| `master.m3u8`    | Manifest HLS yang digunakan untuk mendeteksi varian stream |

Script menggunakan URL yang diberikan pada saat dijalankan, sehingga Anda tidak perlu mengubah URL secara manual di dalam kode.

## Alur Kerja

1. Membuka halaman film di Chromium.
2. Membaca judul dan mengidentifikasi TMDB ID.
3. Memasang listener respons jaringan untuk mendeteksi `master.m3u8`.
4. Menemukan iframe `vsembed` dan iframe player di dalamnya.
5. Mencoba mengaktifkan pemutar video dan memeriksa status playback.
6. Mengurai manifest HLS untuk mendapatkan resolusi yang diumumkan server.
7. Menampilkan hasil di terminal.

## Contoh Tampilan Terminal

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

_Contoh tampilan di atas hanya ilustrasi. Resolusi dan URL sebenarnya bergantung pada manifest yang dikirim server._

## Troubleshooting

### `TimeoutError` saat mencari `h1`

Pastikan URL benar, halaman dapat diakses, dan elemen `h1` tersedia. Situs yang lambat atau mengalami perubahan struktur HTML dapat menyebabkan timeout.

### Iframe `vsembed` tidak ditemukan

Periksa apakah halaman masih menggunakan pola iframe `vsembed`. Jika struktur embed berubah, selector pada script perlu disesuaikan.

### URL `master.m3u8` tidak tertangkap

Kemungkinan manifest belum diminta oleh player, format URL berbeda, atau stream menggunakan mekanisme lain. Listener jaringan juga harus dipasang sebelum aktivitas player yang memicu permintaan manifest.

### Tidak ada resolusi yang ditampilkan

Pastikan manifest yang tertangkap merupakan master playlist HLS dan dapat diakses. Playlist media biasa tidak selalu memiliki entri `#EXT-X-STREAM-INF`.

### Error saat mengambil manifest

Server mungkin membutuhkan cookie, header, atau token sesi dari browser. Pengambilan menggunakan `urllib` tidak otomatis mewarisi sesi Chromium.

## Catatan Teknis

- Resolusi yang ditampilkan berasal dari informasi manifest, bukan jaminan bahwa setiap varian dapat diputar.
- URL stream dapat bersifat sementara atau memerlukan sesi autentikasi.
- Script ini bergantung pada struktur halaman dan player yang digunakan situs, sehingga perubahan pada situs dapat memerlukan penyesuaian.
- Gunakan hanya pada konten yang Anda berwenang untuk akses dan pemeriksaannya. Jangan melewati autentikasi atau kontrol akses tanpa izin.

## Lisensi

Tentukan lisensi sesuai kebijakan distribusi proyek sebelum memublikasikan atau membagikan script ini.
