# Proyek Scraping Data Jurnal Sinta Unila

## Deskripsi

Proyek ini adalah aplikasi scraping data untuk mengambil informasi publikasi jurnal dari Sinta Universitas Lampung (Unila). Aplikasi ini menggunakan Selenium dan BeautifulSoup untuk mengotomatisasi proses login dan extraksi data jurnal dari portal Sinta Kemdikbud.

## Fitur

- Login otomatis ke akun Sinta menggunakan kredensial dari file .env
- Scraping data jurnal dari halaman yang ditentukan
- Penyimpanan data dalam format CSV
- Mencegah duplikasi data dengan mekanisme normalisasi judul
- Penanganan error dan percobaan ulang otomatis
- Penyimpanan kemajuan secara berkala

## Persyaratan

- Python 3.x
- Selenium
- BeautifulSoup4
- Chrome WebDriver
- python-dotenv

## Instalasi

1. Clone repositori ini:

```
git clone https://github.com/username/HLS_Project.git
cd HLS_Project
```

2. Instal dependensi:

```
pip install selenium beautifulsoup4 python-dotenv
```

3. Download dan instal Chrome WebDriver sesuai dengan versi Chrome yang digunakan:

   - Kunjungi: https://sites.google.com/chromium.org/driver/
   - Unduh versi yang sesuai dengan Chrome yang diinstal
   - Letakkan file executable di lokasi yang terdaftar di PATH atau tentukan lokasinya secara eksplisit

4. Buat file `.env` di direktori root proyek dengan format:

```
SINTA_EMAIL=email_anda@example.com
SINTA_PASSWORD=password_anda
```

## Penggunaan

1. Konfigurasikan rentang halaman yang ingin di-scrape dengan mengedit nilai `START_PAGE` dan `END_PAGE` di file `main.py`

2. Jalankan aplikasi:

```
python main.py
```

3. Data hasil scraping akan disimpan dalam file CSV dengan format: `sinta_articles_[START_PAGE]_to_[END_PAGE].csv`

## Struktur Proyek

```
HLS_Project/
├── .env                    # File kredensial (jangan commit ke repositori)
├── .gitignore              # File konfigurasi git
├── main.py                 # File utama untuk menjalankan aplikasi
├── entities/
│   └── article.py          # Entitas artikel
├── interfaces/
│   ├── fetcher_selenium.py # Interface untuk mengambil data menggunakan Selenium
│   └── writer.py           # Interface untuk menulis data ke CSV
└── usecases/
    └── scraper.py          # Implementasi use case scraping
```

## Menyesuaikan Scraper

### Mengubah Rentang Halaman

Untuk mengubah rentang halaman yang akan di-scrape, buka file `main.py` dan ubah nilai variabel berikut:

```python
START_PAGE = 2503  # Halaman awal
END_PAGE = 2505    # Halaman akhir
```

### Mengubah Waktu Tunggu

Jika ingin mempercepat proses scraping (dengan risiko terdeteksi sebagai bot), dapat mengubah nilai `time.sleep()` di file `usecases/scraper.py`.

## Penanganan Error

Scraper ini dirancang dengan mekanisme penanganan error dan percobaan ulang:

- Melakukan 3x percobaan ulang jika terjadi kesalahan saat scraping halaman
- Menyimpan kemajuan secara berkala untuk mencegah kehilangan data
- Login ulang secara otomatis jika sesi berakhir

## Catatan Penting

- Gunakan aplikasi ini dengan bijak dan sesuai dengan Terms of Service dari situs target
- Hindari melakukan request terlalu sering dalam waktu singkat untuk mencegah pemblokiran IP
- Jangan mendistribusikan kredensial login Anda

## Pengembangan Selanjutnya

- Implementasi paralelisasi untuk mempercepat proses scraping
- Penambahan antarmuka grafis (GUI)
- Ekspor ke format lain (Excel, JSON, dll)
- Integrasi dengan database

## Kontributor

- [Nama Anda]
- [Nama Kontributor Lain]

## Lisensi

[Jenis Lisensi] - Lihat file LICENSE untuk detail
