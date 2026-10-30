import re
import os
import sys
import urllib.request
from downloader import unduh_dengan_ytdlp
from urllib.parse import urljoin,urlparse, parse_qs
from playwright.sync_api import sync_playwright


def buat_nama_file(judul, url, resolusi, season=None, episode=None):
    judul_bersih = re.sub(r'[\\/*?:"<>|]', "", judul).strip()
    judul_bersih = re.sub(r"\s+", "_", judul_bersih)

    if "tmdb-tv-" in url.lower() and season is not None and episode is not None:
        return f"{judul_bersih}_S{season}E{episode}_{resolusi}.mp4"

    return f"{judul_bersih}_{resolusi}.mp4"

def ambil_season_episode(url):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    try:
        season = int(params["season"][0])
        episode = int(params["episode"][0])

        print(f"      ➔ Season   : {season}")
        print(f"      ➔ Episode  : {episode}")

        return season, episode

    except (KeyError, ValueError, IndexError):
        print("      ➔ Season/episode tidak ditemukan pada URL.")
        return None, None

def cetak_hasil_rapi(judul, tmdb_id, daftar_resolusi):
    """Mencetak hasil ekstraksi dengan format visual yang rapi di terminal."""
    garis_tebal = "═" * 65
    garis_tipis = "─" * 65

    print("\n" + garis_tebal)
    print(" HASIL EKSTRAKSI VIDEO STREAMING ".center(65))
    print(garis_tebal)
    
    # Detail Informasi Film
    print(f" Judul Film  : {judul}")
    print(f" TMDB ID     : {tmdb_id}")
    print(garis_tipis)
    
    # Daftar Resolusi & URL Stream 
    print(" DAFTAR RESOLUSI & STREAM URL TERSEDIA:")
    print(garis_tipis)
    
    if daftar_resolusi:
        for res, url in daftar_resolusi:
            print(f" [{res.upper():^6}] : {url}")
    else:
        print("Tidak ada resolusi yang berhasil diekstrak.")
        
    print(garis_tebal + "\n")

def main(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 1. Buka Halaman Film 
        print("[1/4] Memuat halaman")
        page.goto(url)
        
        # 2. Parsing Judul Film dan TMDB ID 
        page.wait_for_selector("h1", timeout=10000)
        judul_film = page.locator("h1").inner_text()
        tmdb_id = page.url.split("/")[-1].replace('tmdb-tv-', '').replace('tmdb-mov-', '')
        print(f"      ➔ [BERHASIL] {judul_film} ({tmdb_id})")
        
        # 3. Variabel Penampung URL Master Manifest
        master_url = None

        # Pasang listener jaringan untuk menangkap URL master.m3u8 secara dinamis
        def tangkap_network(response):
            nonlocal master_url
            if "master.m3u8" in response.url:
                master_url = response.url

        page.on("response", tangkap_network)
        
        # 4. Navigasi ke Struktur Nested Iframe
        page.wait_for_selector("iframe[src*='vsembed']", timeout=15000)
        outer_frame = page.frame_locator("iframe[src*='vsembed']")
        inner_frame = outer_frame.frame_locator("#player_iframe")
        level3_frame = inner_frame.frame_locator("iframe").first
        
        # 5. Penanganan Tombol Play & Overlay Iklan
        print("[2/4] Menembus iframe & memicu pemutar video...")
        play_button = inner_frame.locator("#bigPlay")
        
        max_klik = 5
        player_aktif = False

        for i in range(1, max_klik + 1):
            if play_button.is_visible():
                print(f"      ➔ Mencoba klik tombol play ({i}/{max_klik})")
                play_button.click(force=True)
                page.wait_for_timeout(2000)
            else:
                print(f"      ➔ Pemutar sedang memuat ({i}/{max_klik})")

            # Cek apakah kontrol pemutar (#controls) di level3_frame sudah muncul
            try:
                controls_element = level3_frame.locator("#controls")
                controls_element.wait_for(state="visible", timeout=3000)
                # print("      ➔ Kontrol pemutar (#controls) berhasil muncul! Video siap diputar.")
                player_aktif = True
                # break
            except Exception:
                print(f"      ➔ Skip iklan ({i}/{max_klik})")

        if not player_aktif:
            print("      ➔ [PERINGATAN]: Elemen #controls tidak terdeteksi, melanjutkan pemeriksaan")

        # 6. Pemeriksaan Status Pemutaran Video 
        print("[3/4] Memeriksa status pemutaran")
        max_percobaan = 3
        for percobaan in range(1, max_percobaan + 1):
            print(f"      ➔ Pemeriksaan video ({percobaan}/{max_percobaan})")
            page.wait_for_timeout(10000)
            
            try:
                video_element = level3_frame.locator("video").first
                is_playing = video_element.evaluate("v => !v.paused && v.currentTime > 0")
                
                if is_playing:
                    print("      ➔ [STATUS] Video BERHASIL terputar di iframe tingkat 3!")
                    break
                else:
                    print("      ➔ [STATUS] Video masih buffering atau belum berjalan")
            except Exception:
                print("      ➔ Elemen video belum siap")

        # 7. Mengurai File master.m3u8 untuk Pemetaan Resolusi 📐
        hasil_resolusi = []
        if master_url:
            print("[4/4] Mengurai isi master.m3u8 secara dinamis...")
            try:
                req = urllib.request.Request(master_url, headers={'User-Agent': 'Mozilla/5.0'})
                content = urllib.request.urlopen(req).read().decode('utf-8')
                
                lines = content.splitlines()
                
                for i in range(len(lines)):
                    if "#EXT-X-STREAM-INF" in lines[i]:
                        info = lines[i]
                        
                        # Ambil nilai tinggi resolusi (misal 360 dari 480x360)
                        if "RESOLUTION=" in info:
                            dimensi = info.split("RESOLUTION=")[1].split(",")[0]
                            tinggi = dimensi.split("x")[-1]
                            label_res = f"{tinggi}p"
                        else:
                            label_res = "Unknown"
                        
                        # Ambil URL relatif/absolut di baris berikutnya
                        raw_stream_url = lines[i + 1].strip()
                        stream_url = urljoin(master_url, raw_stream_url)
                        
                        hasil_resolusi.append((label_res, stream_url))

            except Exception as e:
                print(f"      ➔ Gagal mengurai file master.m3u8: {e}")
        else:
            print("      ➔ URL master.m3u8 tidak berhasil ditangkap dari jaringan.")

        page.wait_for_timeout(1000)
        season, episode = ambil_season_episode(url)

        if season is not None and episode is not None:
            print(f"      ➔ Season   : {season}")
            print(f"      ➔ Episode  : {episode}")
        else:
            print("      ➔ Season/episode tidak ditemukan.")

        # 8. Cetak Tampilan Akhir Secara Rapi 
        cetak_hasil_rapi(judul_film, tmdb_id, hasil_resolusi)

        url_halaman = page.url

        page.wait_for_timeout(3000)
        browser.close()
        # 9. Mengunduh seluruh stream dari resolusi terkecil
        if hasil_resolusi:
            print("[5/5] Memulai pengunduhan seluruh resolusi...")

            # Urutkan berdasarkan angka tinggi resolusi.
            streams_urut = sorted(
                hasil_resolusi,
                key=lambda item: int(
                    re.search(r"\d+", item[0]).group()
                ) if re.search(r"\d+", item[0]) else 0
            )

            # Bersihkan judul untuk digunakan sebagai nama file.
            judul_file = re.sub(
                r'[\\/*?:"<>|]',
                "",
                judul_film
            ).strip()

            for nomor, (resolusi, stream_url) in enumerate(
                streams_urut, start=1
            ):
                nama_output = buat_nama_file(
                    judul=judul_film,
                    url=url_halaman,
                    resolusi=resolusi,
                    season=season,
                    episode=episode,
                )

                print(
                    f"\n      ➔ Mengunduh resolusi {resolusi}"
                )

                unduh_dengan_ytdlp(
                    stream_url=stream_url,
                    judul_film=judul_film,
                    resolusi=resolusi,
                    nama_output=nama_output,
                    season=season,
                    episode=episode,
                )
        else:
            print("[PERINGATAN] Tidak ada URL stream untuk diunduh.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Penggunaan:")
        print("  Movie     : python extractor.py <url_movie>")
        print("  TV Series : python extractor.py <url_tv>")
        print()
        print("Contoh:")
        print(
            "  Movie     : python extractor.py "
            '"https://cinema.zetware.id/watch/tmdb-mov-456"'
        )
        print(
            "  TV Series : python extractor.py "
            '"https://cinema.zetware.id/watch/tmdb-tv-456?season=1&episode=2"'
        )
        sys.exit(1)

    url = sys.argv[1]
    main(url)