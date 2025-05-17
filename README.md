# Proyek Scraping Data Jurnal Sinta Unila

## Deskripsi

Proyek ini adalah aplikasi scraping data untuk mengambil informasi publikasi jurnal dari Sinta Universitas Lampung (Unila). Aplikasi ini menggunakan Selenium dan BeautifulSoup untuk mengotomatisasi proses login dan ekstraksi data jurnal dari portal Sinta Kemdikbud.

## Fitur

- Login otomatis ke akun Sinta menggunakan kredensial dari file .env
- Scraping data jurnal dari halaman yang ditentukan
- Penyimpanan data dalam format CSV
- Pencegahan duplikasi data dengan mekanisme normalisasi judul
- Penanganan error dan percobaan ulang otomatis
- Penyimpanan kemajuan secara berkala
- Preprocessing data CSV untuk analisis lebih lanjut
- Preprocessing NLP pada judul artikel untuk analisis teks

## Teknologi yang Digunakan

- **Python 3.x** - Bahasa pemrograman utama
- **Selenium** - Framework otomatisasi web
- **BeautifulSoup4** - Library parsing HTML
- **Chrome WebDriver** - Driver browser untuk Selenium
- **Pandas** - Library untuk manipulasi dan analisis data
- **NumPy** - Library untuk operasi numerik
- **NLTK** - Natural Language Toolkit untuk pemrosesan bahasa alami
- **scikit-learn** - Library untuk machine learning dan vektorisasi teks
- **Sastrawi** - Library stemming untuk Bahasa Indonesia
- **langdetect** - Library untuk deteksi bahasa
- **googletrans** - Library untuk terjemahan teks
- **Python Libraries**:
  - csv - Untuk operasi file CSV
  - os - Untuk operasi file dan direktori
  - re - Untuk penggunaan regular expressions
  - time - Untuk pengaturan waktu tunggu
  - python-dotenv - Untuk manajemen variabel lingkungan
  - argparse - Untuk parsing argumen command line
  - joblib - Untuk menyimpan dan memuat model scikit-learn

## Persyaratan Sistem

- Python 3.6 atau lebih tinggi
- Google Chrome Browser
- Koneksi internet yang stabil

## Instalasi

1. Clone repositori ini:

```bash
git clone https://github.com/username/HLS_Project.git
cd HLS_Project
```

2. Instal dependensi:

```bash
pip install selenium beautifulsoup4 python-dotenv pandas numpy nltk scikit-learn langdetect googletrans==4.0.0-rc1 Sastrawi joblib tqdm
```

3. Download dan instal Chrome WebDriver:

   - Kunjungi: https://sites.google.com/chromium.org/driver/
   - Unduh versi yang sesuai dengan Chrome yang diinstal
   - Letakkan file executable di lokasi yang terdaftar di PATH sistem

4. Buat file `.env` di direktori root proyek:

```
SINTA_EMAIL=email_anda@example.com
SINTA_PASSWORD=password_anda
```

## Penggunaan

### Konfigurasi Dasar

1. Jalankan aplikasi dengan konfigurasi default (halaman 2503-3336):

```bash
python main.py
```

2. Atau tentukan rentang halaman:

```bash
python main.py --start 2503 --end 3336
```

3. Hasil scraping akan disimpan dalam file CSV dengan format: `sinta_articles_[START_PAGE]_to_[END_PAGE].csv`

### Preprocessing Data

Setelah melakukan scraping, Anda dapat melakukan preprocessing pada data hasil scraping dengan dua cara:

#### Cara 1: Menjalankan scraping dan preprocessing sekaligus

```bash
python main.py --preprocess
```

Atau dengan rentang halaman kustom:

```bash
python main.py --start 2503 --end 3336 --preprocess
```

#### Cara 2: Hanya menjalankan preprocessing pada file CSV yang sudah ada

```bash
python main.py --only-preprocess data/csv/sinta_articles_2503_to_3336.csv
```

Preprocessing data mencakup:

- Penanganan nilai kosong
- Normalisasi kolom judul dan penulis
- Standarisasi format tahun
- Konversi sitasi ke nilai numerik
- Penghapusan duplikat
- Pengurutan berdasarkan tahun dan jumlah sitasi

Hasil preprocessing akan disimpan dengan format: `[namafile]_processed.csv`

### Preprocessing NLP pada Judul Artikel

Anda dapat melakukan preprocessing NLP (Natural Language Processing) pada judul artikel untuk persiapan analisis teks lanjutan:

#### Cara 1: Menjalankan scraping, preprocessing data, dan NLP sekaligus

```bash
python main.py --preprocess --nlp
```

#### Cara 2: Hanya menjalankan NLP pada file CSV yang sudah ada

```bash
python main.py --only-nlp data/csv/sinta_articles_2503_to_3336.csv
```

#### Cara 3: Menjalankan preprocessing data dan NLP pada file yang sudah ada

```bash
python main.py --only-preprocess data/csv/sinta_articles_2503_to_3336.csv --nlp
```

Untuk menerjemahkan judul dalam bahasa asing ke Bahasa Indonesia (lambat), tambahkan flag `--translate`:

```bash
python main.py --only-nlp data/csv/sinta_articles_2503_to_3336.csv --translate
```

Preprocessing NLP mencakup:

1. **Case folding** - Mengubah semua teks menjadi huruf kecil
2. **Punctuation removal** - Menghapus tanda baca dan simbol
3. **Language detection** - Mendeteksi bahasa dari judul artikel
4. **Translation** (opsional) - Menerjemahkan judul non-Indonesia ke Bahasa Indonesia
5. **Tokenization** - Memecah teks menjadi token (kata-kata)
6. **Stopword removal** - Menghapus kata-kata umum yang tidak informatif
7. **Stemming** - Mengubah kata menjadi bentuk dasar (menggunakan Sastrawi untuk Bahasa Indonesia)
8. **Vectorization** - Mengubah teks menjadi representasi vektor menggunakan TF-IDF

Hasil preprocessing NLP akan disimpan dengan format: `[namafile]_nlp.csv`, dan
vektorisasi disimpan sebagai file terpisah: `[namafile]_nlp_tfidf_vectorizer.pkl` dan `[namafile]_nlp_tfidf_features.pkl`.

### Opsi Tambahan

- **Penyesuaian Waktu Tunggu**: Edit nilai `time.sleep()` di `usecases/scraper.py` untuk mengatur kecepatan scraping
- **Rentang Halaman**: Sesuaikan `START_PAGE` dan `END_PAGE` di `main.py` untuk mengubah jangkauan scraping

## Struktur Proyek

```
HLS_Project/
├── .env                     # File kredensial (jangan commit ke repositori)
├── .gitignore               # File konfigurasi git
├── main.py                  # File utama untuk menjalankan aplikasi (scraping & preprocessing)
├── entities/
│   └── article.py           # Entitas artikel (model data)
├── interfaces/
│   ├── fetcher_selenium.py  # Interface untuk mengambil data menggunakan Selenium
│   ├── writer.py            # Interface untuk menulis data ke CSV
│   ├── csv_preprocessor.py  # Interface untuk preprocessing data CSV
│   └── nlp_processor.py     # Interface untuk preprocessing NLP pada judul artikel
└── usecases/
    └── scraper.py           # Implementasi logika utama scraping
```

## Arsitektur Aplikasi

Proyek ini mengikuti prinsip Clean Architecture dengan pemisahan:

1. **Entities Layer** - Representasi data (artikel jurnal)
2. **Interfaces Layer** - Mekanisme akses data (fetcher), output (writer), dan processing (csv_preprocessor)
3. **Use Cases Layer** - Logika bisnis untuk scraping dan pengolahan data

## Penanganan Error

Aplikasi ini dirancang dengan mekanisme error handling yang kuat:

- **Retries** - Percobaan ulang otomatis (hingga 3x) ketika terjadi kesalahan pada halaman
- **Progress Saving** - Penyimpanan data berkala untuk mencegah kehilangan data
- **Auto Re-login** - Login ulang otomatis ketika sesi berakhir
- **Deduplikasi** - Pencegahan data duplikat dengan normalisasi judul

## Praktik Terbaik

- Gunakan aplikasi ini dengan tanggung jawab dan hormati Terms of Service dari Sinta Kemdikbud
- Hindari melakukan request terlalu cepat untuk mencegah IP Anda diblokir
- Secara berkala periksa hasil CSV untuk memastikan kualitas data
- Lakukan preprocessing data sebelum melakukan analisis untuk memastikan keakuratan hasil

## Analisis Data

Setelah data dipreprocessing, Anda dapat melakukan berbagai analisis seperti:

- Distribusi publikasi per tahun
- Tren publikasi berdasarkan jumlah sitasi
- Analisis penulis paling produktif
- Identifikasi topik jurnal populer berdasarkan judul

### Analisis NLP Lanjutan

Setelah melakukan preprocessing NLP, beberapa analisis yang dapat dilakukan:

- **Topic Modeling** - Menemukan topik umum dari judul artikel
- **Clustering** - Mengelompokkan artikel berdasarkan kesamaan judul
- **Keyword Extraction** - Mengidentifikasi kata kunci penting dalam penelitian
- **Sentiment Analysis** - Menganalisis sentimen dari judul artikel
- **Trend Analysis** - Menganalisis tren topik penelitian dari waktu ke waktu

## Pengembangan Selanjutnya

- [ ] Implementasi paralelisasi untuk mempercepat proses scraping
- [ ] Penambahan antarmuka grafis (GUI)
- [ ] Ekspor ke format lain (Excel, JSON, dll)
- [ ] Integrasi dengan database relasional atau NoSQL
- [ ] Analisis data pada artikel yang diambil
- [ ] Visualisasi data otomatis dari hasil preprocessing
- [ ] Analisis sentimen dari judul artikel

## Troubleshooting

**Masalah Login**:

- Pastikan kredensial di file `.env` sudah benar
- Periksa file `login_debug.html` untuk analisis masalah login

**Scraping Lambat**:

- Coba turunkan waktu tunggu di `usecases/scraper.py`
- Batasi rentang halaman untuk pengujian awal

**Chrome Driver Error**:

- Pastikan versi Chrome WebDriver sesuai dengan versi browser Chrome
- Restart browser dan aplikasi jika mengalami masalah koneksi

**Error Preprocessing**:

- Pastikan format CSV sesuai dengan yang diharapkan (memiliki kolom Title, Link, Authors, Year, Cited)
- Periksa apakah pandas dan numpy sudah terinstal dengan benar

## Kontributor

- [Nama Anda]
- [Nama Kontributor Lain]

## Lisensi

[Jenis Lisensi] - Lihat file LICENSE untuk detail

---

Dibuat dengan ❤️ oleh [Nama Tim]
