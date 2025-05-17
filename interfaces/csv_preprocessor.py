import pandas as pd
import re
import os
import numpy as np
from datetime import datetime

def preprocess_csv(input_file, output_file=None):
    """
    Melakukan preprocessing pada file CSV hasil scraping
    
    Args:
        input_file: Path ke file CSV yang akan dipreprocessing
        output_file: Path untuk menyimpan hasil preprocessing (jika None, akan menggunakan nama input + '_processed')
    
    Returns:
        Path ke file hasil preprocessing
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File {input_file} tidak ditemukan")
    
    # Buat nama file output jika tidak disediakan
    if output_file is None:
        filename, ext = os.path.splitext(input_file)
        output_file = f"{filename}_processed{ext}"
    
    print(f"Memulai preprocessing file {input_file}...")
    
    # Baca file CSV dengan parameter yang lebih toleran terhadap format yang tidak standar
    try:
        # Coba berbagai opsi parsingnya
        df = pd.read_csv(input_file, on_bad_lines='warn', encoding='utf-8', engine='python')
    except Exception as e:
        print(f"Error membaca CSV: {e}")
        print("Mencoba metode alternatif...")
        # Jika gagal, gunakan delimiter yang lebih spesifik
        df = pd.read_csv(input_file, delimiter=',', on_bad_lines='skip', encoding='utf-8', engine='python')
    
    # Tampilkan informasi awal
    print(f"Data awal: {df.shape[0]} baris, {df.shape[1]} kolom")
    print(f"Kolom: {', '.join(df.columns)}")
    
    # 1. Penanganan nilai kosong
    print("Memeriksa nilai kosong...")
    null_counts = df.isnull().sum()
    print(f"Nilai kosong per kolom: {null_counts.to_dict()}")
    
    # Isi nilai kosong
    df['Authors'] = df['Authors'].fillna('Unknown')
    df['Year'] = df['Year'].fillna('Unknown')
    df['Cited'] = df['Cited'].fillna('0')
    
    # 2. Normalisasi kolom Title
    print("Normalisasi kolom Title...")
    # Hapus whitespace berlebih
    df['Title'] = df['Title'].str.strip()
    # Standarisasi kutipan
    df['Title'] = df['Title'].apply(lambda x: re.sub(r'["""]', '"', str(x)))
    
    # 3. Normalisasi kolom Authors
    print("Normalisasi kolom Authors...")
    # Hapus awalan "Authors : " dari kolom Authors
    df['Authors'] = df['Authors'].apply(lambda x: re.sub(r'^Authors\s*:\s*', '', str(x)))
    # Standardisasi format penulis
    df['Authors'] = df['Authors'].apply(lambda x: re.sub(r'\s+', ' ', str(x)).strip())
    
    # 4. Konversi kolom Year ke format standar
    print("Konversi kolom Year...")
    # Ekstrak tahun dari format yang mungkin berbeda
    df['Year'] = df['Year'].apply(extract_year)
    
    # 5. Konversi kolom Cited ke numerik
    print("Konversi kolom Cited...")
    # Hapus kata 'cited' dan ubah ke numerik
    df['Cited'] = df['Cited'].apply(lambda x: str(x).replace('cited', '').strip())
    df['Cited'] = pd.to_numeric(df['Cited'].str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).astype(int)
    
    # 8. Hapus duplikat terakhir (jika ada)
    print("Memeriksa duplikat...")
    duplicate_count = df.duplicated(subset=['Title', 'Year']).sum()
    print(f"Menemukan {duplicate_count} duplikat")
    
    if duplicate_count > 0:
        df = df.drop_duplicates(subset=['Title', 'Year'], keep='first')
    
    # 9. Urutkan berdasarkan tahun dan sitasi (jika diminta)
    # Menghapus pengurutan untuk mempertahankan urutan asli
    # print("Mengurutkan data...")
    # df = df.sort_values(by=['Year', 'Cited'], ascending=[False, False])
    
    # 10. Pastikan hanya kolom yang diinginkan yang disimpan
    # Hapus kolom yang tidak diinginkan jika ada
    columns_to_keep = ['Title', 'Link', 'Authors', 'Year', 'Cited']
    for col in columns_to_keep:
        if col not in df.columns:
            print(f"Perhatian: Kolom {col} tidak ditemukan dalam data. Menambahkan kolom kosong.")
            df[col] = 'Unknown'
    
    df = df[columns_to_keep]
    
    # Simpan hasil preprocessing
    df.to_csv(output_file, index=False)
    print(f"Preprocessing selesai. Data akhir: {df.shape[0]} baris, {df.shape[1]} kolom")
    print(f"Hasil preprocessing disimpan di {output_file}")
    
    return output_file

def extract_year(year_str):
    """
    Ekstrak tahun dari berbagai format
    
    Args:
        year_str: String tahun yang akan diekstrak
    
    Returns:
        String tahun dalam format standard (YYYY)
    """
    # Coba ekstrak 4 digit tahun
    year_match = re.search(r'(19|20)\d{2}', str(year_str))
    
    if year_match:
        return year_match.group(0)
    else:
        return "Unknown" 