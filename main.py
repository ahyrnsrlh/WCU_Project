from usecases.scraper import scrape_articles_with_login
import os
import argparse
from dotenv import load_dotenv
from interfaces.csv_preprocessor import preprocess_csv
from interfaces.nlp_processor import process_nlp

def main():
    # Parse argumen command line
    parser = argparse.ArgumentParser(description='Scrape dan preprocess data jurnal Sinta Unila.')
    parser.add_argument('--start', type=int, default=2503, help='Halaman awal untuk scraping (default: 2503)')
    parser.add_argument('--end', type=int, default=3336, help='Halaman akhir untuk scraping (default: 3336)')
    parser.add_argument('--preprocess', action='store_true', help='Lakukan preprocessing data setelah scraping')
    parser.add_argument('--only-preprocess', help='Hanya lakukan preprocessing pada file CSV yang ditentukan')
    parser.add_argument('--nlp', action='store_true', help='Lakukan preprocessing NLP pada judul artikel')
    parser.add_argument('--translate', action='store_true', help='Terjemahkan judul non-Indonesia ke Bahasa Indonesia (lambat)')
    parser.add_argument('--only-nlp', help='Hanya lakukan preprocessing NLP pada file CSV yang ditentukan')
    
    args = parser.parse_args()
    
    # Jika hanya ingin melakukan preprocessing NLP
    if args.only_nlp:
        if os.path.exists(args.only_nlp):
            print(f"Melakukan preprocessing NLP pada semua kolom (Title, Link, Authors, Year, Cited) dari file {args.only_nlp}...")
            output_file = process_nlp(args.only_nlp, vectorize=True, translate=args.translate)
            print(f"Preprocessing NLP berhasil! Hasil disimpan di: {output_file}")
            return 0
        else:
            print(f"Error: File {args.only_nlp} tidak ditemukan")
            return 1
    
    # Jika hanya ingin melakukan preprocessing data
    if args.only_preprocess:
        if os.path.exists(args.only_preprocess):
            print(f"Melakukan preprocessing pada file {args.only_preprocess}...")
            output_file = preprocess_csv(args.only_preprocess)
            
            # Jika NLP juga diminta, lakukan preprocessing NLP pada hasil
            if args.nlp:
                print(f"\nMelakukan preprocessing NLP pada hasil preprocessing ({output_file})...")
                nlp_output = process_nlp(output_file, vectorize=True, translate=args.translate)
                print(f"Preprocessing NLP berhasil! Hasil disimpan di: {nlp_output}")
            
            print(f"Preprocessing berhasil! Hasil disimpan di: {output_file}")
            return 0
        else:
            print(f"Error: File {args.only_preprocess} tidak ditemukan")
            return 1
    
    # Load environment variables from .env file
    load_dotenv()
    
    START_PAGE = args.start
    END_PAGE = args.end
    
    # Get credentials from environment variables
    EMAIL = os.getenv("SINTA_EMAIL")
    PASSWORD = os.getenv("SINTA_PASSWORD")
    
    if not EMAIL or not PASSWORD:
        print("Error: Email atau password tidak ditemukan di file .env")
        return 1
    
    # Lakukan scraping
    output_file = scrape_articles_with_login(START_PAGE, END_PAGE, EMAIL, PASSWORD)
    
    if not output_file:
        print("Error: Scraping tidak berhasil menghasilkan file output")
        return 1
    
    # Jika opsi preprocessing diaktifkan, lakukan preprocessing pada hasil scraping
    if args.preprocess and output_file and os.path.exists(output_file):
        print(f"\nMelakukan preprocessing pada hasil scraping ({output_file})...")
        preprocessed_file = preprocess_csv(output_file)
        print("Preprocessing selesai!")
        
        # Update output_file to preprocessed file for potential NLP processing
        output_file = preprocessed_file
    
    # Jika opsi NLP diaktifkan, lakukan preprocessing NLP pada hasil
    if args.nlp and output_file and os.path.exists(output_file):
        print(f"\nMelakukan preprocessing NLP pada data ({output_file})...")
        nlp_output = process_nlp(output_file, vectorize=True, translate=args.translate)
        print(f"Preprocessing NLP berhasil! Hasil disimpan di: {nlp_output}")
    
    return 0

if __name__ == "__main__":
    exit(main())
