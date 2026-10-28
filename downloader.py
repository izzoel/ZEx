import os
import time
import threading
import sys
import yt_dlp
import re

def tinggi_resolusi(stream):
    height = stream.get("height")

    if height:
        return int(height)

    resolution = str(stream.get("resolution", ""))

    # Format seperti 1920x1080
    match = re.search(r"\d+\s*x\s*(\d+)", resolution)
    if match:
        return int(match.group(1))

    # Format seperti 360p, 720p, 1080p
    match = re.search(r"(\d+)\s*p", resolution, re.IGNORECASE)
    if match:
        return int(match.group(1))

    return 0


def urutkan_stream(streams):
    return sorted(streams, key=tinggi_resolusi)

def unduh_dengan_ytdlp(
    stream_url,
    judul_film,
    resolusi,
    nama_output=None,
    season=None,
    episode=None,
):
    garis = "=" * 65

    # Bentuk nama file otomatis jika belum diberikan.
    if nama_output is None:
        judul_bersih = re.sub(r'[\\/*?:"<>|]', "", judul_film).strip()
        judul_bersih = re.sub(r"\s+", "_", judul_bersih)

        if season is not None and episode is not None:
            nama_output = (
                f"{judul_bersih}_S{season}E{episode}_{resolusi}.mp4"
            )
        else:
            nama_output = f"{judul_bersih}_{resolusi}.mp4"

    # Pastikan ekstensi output tetap mp4.
    if not nama_output.lower().endswith(".mp4"):
        nama_output += ".mp4"

    print(f"\n{garis}")
    print(" MEMULAI PENGUNDUHAN VIDEO STREAMING ".center(65))
    print(garis)
    print(f" Judul     : {judul_film}")
    print(f" Resolusi  : {resolusi}")
    print(f" Output    : {nama_output}")
    print(garis + "\n")

    # Lanjutkan dengan ydl_opts, monitor, dan proses unduhan
    # dari kode Anda yang sekarang.
    
    
    ydl_opts = {
        'outtmpl': nama_output,

        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
        },

        # Gunakan downloader internal yt-dlp
        'concurrent_fragment_downloads': 1,

        # Percobaan ulang ketika permintaan atau fragmen gagal
        'retries': 10,
        'fragment_retries': 10,
        'file_access_retries': 5,

        # Jeda permintaan dan jeda antar-unduhan
        'sleep_interval_requests': 2,
        'sleep_interval': 1,
        'max_sleep_interval': 3,

        'quiet': True,
        'no_warnings': True,
    }

    
    stop_event = threading.Event()

    monitor = threading.Thread(
        target=monitor_download,
        args=(nama_output, stop_event, 1),
        daemon=True,
    )

    try:
        monitor.start()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([stream_url])

        print(f"\n[BERHASIL] Video tersimpan: {nama_output}", flush=True)

    except Exception as e:
        print(f"\n[GAGAL] Terjadi kesalahan: {e}", flush=True)

    finally:
        stop_event.set()
        monitor.join(timeout=2)

def monitor_download(nama_output, stop_event, interval=60):
    waktu_mulai = time.monotonic()
    ukuran_sebelumnya = None

    while not stop_event.is_set():
        try:
            # Periksa file output dan file sementara yt-dlp.
            kandidat = [
                nama_output,
                nama_output + ".part",
            ]

            file_aktif = next(
                (
                    path for path in kandidat
                    if os.path.isfile(path)
                ),
                None
            )

            if file_aktif is None:
                sys.stdout.write(
                    f"\r[MONITOR] Memulai proses unduhan..."
                )
                sys.stdout.flush()
                    
            else:
                ukuran = os.path.getsize(file_aktif)
                ukuran_mb = ukuran / (1024 * 1024)
                durasi = int(time.monotonic() - waktu_mulai)

                if ukuran_sebelumnya is None:
                    status = "DOWNLOAD"
                    tambahan_mb = 0.0
                else:
                    tambahan = ukuran - ukuran_sebelumnya
                    tambahan_mb = tambahan / (1024 * 1024)

                    if tambahan > 0:
                        status = "DOWNLOAD"
                    elif tambahan < 0:
                        status = "MENUNGGU"
                    else:
                        status = "MENUNGGU"

                # sys.stdout.write(
                #     f"\r[{status}] | "
                #     f"Size: {ukuran_mb:.2f} MB | "
                #     f"Durasi: {durasi // 60}m {durasi % 60}s"
                #     " " * 10
                # )
                # sys.stdout.flush()

                ukuran_sebelumnya = ukuran

        except OSError as e:
            print(f"[MONITOR] Error: {e}", flush=True)

        # Tunggu interval, tetapi tetap bisa dihentikan lebih awal.
        if stop_event.wait(interval):
            break

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            "Penggunaan: python downloader.py "
            "<stream_url> <judul_film> <resolusi> [nama_output.mp4]"
        )
        sys.exit(1)

    url_stream = sys.argv[1]
    judul_film = sys.argv[2]
    resolusi = sys.argv[3]
    nama_file = (
        sys.argv[4]
        if len(sys.argv) > 4
        else f"{judul_film}_{resolusi}.mp4"
    )

    unduh_dengan_ytdlp(
        stream_url=url_stream,
        judul_film=judul_film,
        resolusi=resolusi,
        nama_output=nama_file,
    )