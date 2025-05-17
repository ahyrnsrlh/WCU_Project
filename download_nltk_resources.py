#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script untuk mendownload semua resource NLTK yang diperlukan untuk preprocessing NLP.
Digunakan untuk menghindari masalah download otomatis saat runtime.
"""

import nltk
import sys
import os

def download_all_resources():
    """Download semua resource NLTK yang diperlukan"""
    resources = [
        'punkt',           # untuk tokenisasi
        'stopwords',       # untuk stopword removal
        'wordnet',         # untuk lemmatization
        'omw-1.4',         # Open Multilingual Wordnet
    ]
    
    print("Mulai mendownload resource NLTK...")
    
    for resource in resources:
        print(f"Downloading {resource}...")
        try:
            nltk.download(resource)
            print(f"✓ {resource} berhasil didownload")
        except Exception as e:
            print(f"✗ Gagal mendownload {resource}: {e}")
    
    # Coba mengatasi masalah punkt_tab khusus
    try:
        # Pastikan direktori tokenizers/punkt ada
        nltk_data_path = os.path.join(os.path.expanduser('~'), 'nltk_data')
        punkt_dir = os.path.join(nltk_data_path, 'tokenizers', 'punkt')
        
        if os.path.exists(punkt_dir):
            print("\nMencoba menyelesaikan masalah punkt_tab...")
            # Cek apakah direktori punkt_tab sudah ada
            punkt_tab_dir = os.path.join(nltk_data_path, 'tokenizers', 'punkt_tab')
            if not os.path.exists(punkt_tab_dir):
                os.makedirs(os.path.join(punkt_tab_dir, 'english'), exist_ok=True)
            
            # Copy file PY awal ke direktori ini
            english_dir = os.path.join(punkt_dir, 'english')
            if os.path.exists(english_dir):
                # Buat file kosong
                with open(os.path.join(punkt_tab_dir, 'english', 'punkt.py'), 'w') as f:
                    f.write("# Placeholder untuk mengatasi masalah punkt_tab\n")
                print("✓ Berhasil membuat file placeholder untuk punkt_tab")
            else:
                print("✗ Direktori english dari punkt tidak ditemukan")
        else:
            print("✗ Direktori punkt tidak ditemukan, download punkt terlebih dahulu")
    except Exception as e:
        print(f"✗ Gagal menyelesaikan masalah punkt_tab: {e}")
    
    print("\nProses download selesai!")
    print("Jika masih mengalami masalah, coba jalankan di Python console:")
    print("import nltk; nltk.download()")

if __name__ == "__main__":
    print("=" * 60)
    print("NLTK Resource Downloader for HLS Project NLP Processing")
    print("=" * 60)
    
    download_all_resources()
    
    print("\nLangkah selanjutnya:")
    print("1. Jalankan preprocessing NLP:")
    print("   python main.py --only-nlp data/csv/nama_file.csv")
    
    sys.exit(0) 