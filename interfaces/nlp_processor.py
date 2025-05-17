import re
import string
import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from langdetect import detect, LangDetectException
from googletrans import Translator
import nltk
import joblib
import os
import time
from tqdm import tqdm
import concurrent.futures
import logging
from functools import lru_cache
import multiprocessing

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Batas jumlah proses dan thread
NUM_PROCESSES = max(1, multiprocessing.cpu_count() - 1)
NUM_THREADS = min(multiprocessing.cpu_count() * 2, 16)
logger.info(f"Menggunakan {NUM_PROCESSES} proses dan {NUM_THREADS} thread untuk paralelisasi")

# Flag untuk menghindari pesan warning berulang
shown_tokenize_warning = False

# Cache untuk stopwords
stopwords_cache = {}

# Stopwords Indonesia manual untuk fallback
INDONESIAN_STOPWORDS = {
    'ada', 'adalah', 'adanya', 'adapun', 'agak', 'agaknya', 'agar', 'akan', 'akankah', 'akhir',
    'akhiri', 'akhirnya', 'aku', 'akulah', 'amat', 'amatlah', 'anda', 'andalah', 'antar', 'antara',
    'antaranya', 'apa', 'apaan', 'apabila', 'apakah', 'apalagi', 'apatah', 'artinya', 'asal',
    'asalkan', 'atas', 'atau', 'ataukah', 'ataupun', 'awal', 'awalnya', 'bagai', 'bagaikan',
    'bagaimana', 'bagaimanakah', 'bagaimanapun', 'bagi', 'bagian', 'bahkan', 'bahwa', 'bahwasanya',
    'baik', 'bakal', 'bakalan', 'balik', 'banyak', 'bapak', 'baru', 'bawah', 'beberapa', 'begini',
    'beginian', 'beginikah', 'beginilah', 'begitu', 'begitukah', 'begitulah', 'begitupun', 'bekerja',
    'belakang', 'belakangan', 'belum', 'belumlah', 'benar', 'benarkah', 'benarlah', 'berada',
    'berakhir', 'berakhirlah', 'berakhirnya', 'berapa', 'berapakah', 'berapalah', 'berapapun',
    'berarti', 'berawal', 'berbagai', 'berdatangan', 'beri', 'berikan', 'berikut', 'berikutnya',
    'berjumlah', 'berkali-kali', 'berkata', 'berkehendak', 'berkeinginan', 'berkenaan', 'berlainan',
    'berlalu', 'berlangsung', 'berlebihan', 'bermacam', 'bermacam-macam', 'bermaksud', 'bermula',
    'bersama', 'bersama-sama', 'bersiap', 'bersiap-siap', 'bertanya', 'bertanya-tanya', 'berturut',
    'berturut-turut', 'bertutur', 'berujar', 'berupa', 'besar', 'betul', 'betulkah', 'biasa',
    'biasanya', 'bila', 'bilakah', 'bisa', 'bisakah', 'boleh', 'bolehkah', 'bolehlah', 'buat',
    'bukan', 'bukankah', 'bukanlah', 'bukannya', 'bulan', 'bung', 'cara', 'caranya', 'cukup',
    'cukupkah', 'cukuplah', 'cuma', 'dahulu', 'dalam', 'dan', 'dapat', 'dari', 'daripada', 'datang',
    'dekat', 'demi', 'demikian', 'demikianlah', 'dengan', 'depan', 'di', 'dia', 'diakhiri',
    'diakhirinya', 'dialah', 'diantara', 'diantaranya', 'diberi', 'diberikan', 'diberikannya',
    'dibuat', 'dibuatnya', 'didapat', 'didatangkan', 'digunakan', 'diibaratkan', 'diibaratkannya',
    'diingat', 'diingatkan', 'diinginkan', 'dijawab', 'dijelaskan', 'dijelaskannya', 'dikarenakan',
    'dikatakan', 'dikatakannya', 'dikerjakan', 'diketahui', 'diketahuinya', 'dikira', 'dilakukan',
    'dilalui', 'dilihat', 'dimaksud', 'dimaksudkan', 'dimaksudkannya', 'dimaksudnya', 'diminta',
    'dimintai', 'dimisalkan', 'dimulai', 'dimulailah', 'dimulainya', 'dimungkinkan', 'dini',
    'dipastikan', 'diperbuat', 'diperbuatnya', 'dipergunakan', 'diperkirakan', 'diperlihatkan',
    'diperlukan', 'diperlukannya', 'dipersoalkan', 'dipertanyakan', 'dipunyai', 'diri', 'dirinya',
    'disampaikan', 'disebut', 'disebutkan', 'disebutkannya', 'disini', 'disinilah', 'ditambahkan',
    'ditandaskan', 'ditanya', 'ditanyai', 'ditanyakan', 'ditegaskan', 'ditujukan', 'ditunjuk',
    'ditunjuki', 'ditunjukkan', 'ditunjukkannya', 'ditunjuknya', 'dituturkan', 'dituturkannya',
    'diucapkan', 'diucapkannya', 'diungkapkan', 'dong', 'dua', 'dulu', 'empat', 'enggak', 'enggaknya',
    'entah', 'entahlah', 'guna', 'gunakan', 'hal', 'hampir', 'hanya', 'hanyalah', 'hari', 'harus',
    'haruslah', 'harusnya', 'hendak', 'hendaklah', 'hendaknya', 'hingga', 'ia', 'ialah', 'ibarat',
    'ibaratkan', 'ibaratnya', 'ibu', 'ikut', 'ingat', 'ingat-ingat', 'ingin', 'inginkah', 'inginkan',
    'ini', 'inikah', 'inilah', 'itu', 'itukah', 'itulah', 'jadi', 'jadilah', 'jadinya', 'jangan',
    'jangankan', 'janganlah', 'jauh', 'jawab', 'jawaban', 'jawabnya', 'jelas', 'jelaskan',
    'jelaslah', 'jelasnya', 'jika', 'jikalau', 'juga', 'jumlah', 'jumlahnya', 'justru', 'kala',
    'kalau', 'kalaulah', 'kalaupun', 'kalian', 'kami', 'kamilah', 'kamu', 'kamulah', 'kan', 'kapan',
    'kapankah', 'kapanpun', 'karena', 'karenanya', 'kasus', 'kata', 'katakan', 'katakanlah',
    'katanya', 'ke', 'keadaan', 'kebetulan', 'kecil', 'kedua', 'keduanya', 'keinginan', 'kelamaan',
    'kelihatan', 'kelihatannya', 'kelima', 'keluar', 'kembali', 'kemudian', 'kemungkinan',
    'kemungkinannya', 'kenapa', 'kepada', 'kepadanya', 'kesamaan', 'keseluruhan', 'keseluruhannya',
    'keterlaluan', 'ketika', 'khususnya', 'kini', 'kinilah', 'kira', 'kira-kira', 'kiranya',
    'kita', 'kitalah', 'kok', 'kurang', 'lagi', 'lagian', 'lah', 'lain', 'lainnya', 'lalu',
    'lama', 'lamanya', 'lanjut', 'lanjutnya', 'lebih', 'lewat', 'lima', 'luar', 'macam', 'maka',
    'makanya', 'makin', 'malah', 'malahan', 'mampu', 'mampukah', 'mana', 'manakala', 'manalagi',
    'masa', 'masalah', 'masalahnya', 'masih', 'masihkah', 'masing', 'masing-masing', 'mau',
    'maupun', 'melainkan', 'melakukan', 'melalui', 'melihat', 'melihatnya', 'memang', 'memastikan',
    'memberi', 'memberikan', 'membuat', 'memerlukan', 'memihak', 'meminta', 'memintakan',
    'memisalkan', 'memperbuat', 'mempergunakan', 'memperkirakan', 'memperlihatkan', 'mempersiapkan',
    'mempersoalkan', 'mempertanyakan', 'mempunyai', 'memulai', 'memungkinkan', 'menaiki',
    'menambahkan', 'menandaskan', 'menanti', 'menanti-nanti', 'menantikan', 'menanya', 'menanyai',
    'menanyakan', 'mendapat', 'mendapatkan', 'mendatang', 'mendatangi', 'mendatangkan', 'menegaskan',
    'mengakhiri', 'mengapa', 'mengatakan', 'mengatakannya', 'mengenai', 'mengerjakan', 'mengetahui',
    'menggunakan', 'menghendaki', 'mengibaratkan', 'mengibaratkannya', 'mengingat', 'mengingatkan',
    'menginginkan', 'mengira', 'mengucapkan', 'mengucapkannya', 'mengungkapkan', 'menjadi',
    'menjawab', 'menjelaskan', 'menuju', 'menunjuk', 'menunjuki', 'menunjukkan', 'menunjuknya',
    'menurut', 'menuturkan', 'menyampaikan', 'menyangkut', 'menyatakan', 'menyebutkan', 'menyeluruh',
    'menyiapkan', 'merasa', 'mereka', 'merekalah', 'merupakan', 'meski', 'meskipun', 'meyakini',
    'meyakinkan', 'minta', 'mirip', 'misal', 'misalkan', 'misalnya', 'mula', 'mulai', 'mulailah',
    'mulanya', 'mungkin', 'mungkinkah', 'nah', 'naik', 'namun', 'nanti', 'nantinya', 'nyaris',
    'nyatanya', 'oleh', 'olehnya', 'pada', 'padahal', 'padanya', 'pak', 'paling', 'panjang',
    'pantas', 'para', 'pasti', 'pastilah', 'penting', 'pentingnya', 'per', 'percuma', 'perlu',
    'perlukah', 'perlunya', 'pernah', 'persoalan', 'pertama', 'pertama-tama', 'pertanyaan',
    'pertanyakan', 'pihak', 'pihaknya', 'pukul', 'pula', 'pun', 'punya', 'rasa', 'rasanya',
    'rata', 'rupanya', 'saat', 'saatnya', 'saja', 'sajalah', 'saling', 'sama', 'sama-sama',
    'sambil', 'sampai', 'sampai-sampai', 'sampaikan', 'sana', 'sangat', 'sangatlah', 'satu',
    'saya', 'sayalah', 'se', 'sebab', 'sebabnya', 'sebagai', 'sebagaimana', 'sebagainya',
    'sebagian', 'sebaik', 'sebaik-baiknya', 'sebaiknya', 'sebaliknya', 'sebanyak', 'sebegini',
    'sebegitu', 'sebelum', 'sebelumnya', 'sebenarnya', 'seberapa', 'sebesar', 'sebetulnya',
    'sebisanya', 'sebuah', 'sebut', 'sebutlah', 'sebutnya', 'secara', 'secukupnya', 'sedang',
    'sedangkan', 'sedemikian', 'sedikit', 'sedikitnya', 'seenaknya', 'segala', 'segalanya',
    'segera', 'seharusnya', 'sehingga', 'seingat', 'sejak', 'sejauh', 'sejenak', 'sejumlah',
    'sekadar', 'sekadarnya', 'sekali', 'sekali-kali', 'sekalian', 'sekaligus', 'sekalipun',
    'sekarang', 'sekarang', 'sekecil', 'seketika', 'sekiranya', 'sekitar', 'sekitarnya',
    'sekurang-kurangnya', 'sekurangnya', 'sela', 'selain', 'selaku', 'selalu', 'selama',
    'selama-lamanya', 'selamanya', 'selanjutnya', 'seluruh', 'seluruhnya', 'semacam', 'semakin',
    'semampu', 'semampunya', 'semasa', 'semasih', 'semata', 'semata-mata', 'semaunya', 'sementara',
    'semisal', 'semisalnya', 'sempat', 'semua', 'semuanya', 'semula', 'sendiri', 'sendirian',
    'sendirinya', 'seolah', 'seolah-olah', 'seorang', 'sepanjang', 'sepantasnya', 'sepantasnyalah',
    'seperlunya', 'seperti', 'sepertinya', 'sepihak', 'sering', 'seringnya', 'serta', 'serupa',
    'sesaat', 'sesama', 'sesampai', 'sesegera', 'sesekali', 'seseorang', 'sesuatu', 'sesuatunya',
    'sesudah', 'sesudahnya', 'setelah', 'setempat', 'setengah', 'seterusnya', 'setiap', 'setiba',
    'setibanya', 'setidak-tidaknya', 'setidaknya', 'setinggi', 'seusai', 'sewaktu', 'siap',
    'siapa', 'siapakah', 'siapapun', 'sini', 'sinilah', 'soal', 'soalnya', 'suatu', 'sudah',
    'sudahkah', 'sudahlah', 'supaya', 'tadi', 'tadinya', 'tahu', 'tahun', 'tak', 'tambah',
    'tambahnya', 'tampak', 'tampaknya', 'tandas', 'tandasnya', 'tanpa', 'tanya', 'tanyakan',
    'tanyanya', 'tapi', 'tegas', 'tegasnya', 'telah', 'tempat', 'tengah', 'tentang', 'tentu',
    'tentulah', 'tentunya', 'tepat', 'terakhir', 'terasa', 'terbanyak', 'terdahulu', 'terdapat',
    'terdiri', 'terhadap', 'terhadapnya', 'teringat', 'teringat-ingat', 'terjadi', 'terjadilah',
    'terjadinya', 'terkira', 'terlalu', 'terlebih', 'terlihat', 'termasuk', 'ternyata', 'tersampaikan',
    'tersebut', 'tersebutlah', 'tertentu', 'tertuju', 'terus', 'terutama', 'tetap', 'tetapi',
    'tiap', 'tiba', 'tiba-tiba', 'tidak', 'tidakkah', 'tidaklah', 'tiga', 'tinggi', 'toh',
    'tunjuk', 'turut', 'tutur', 'tuturnya', 'ucap', 'ucapnya', 'ujar', 'ujarnya', 'umum',
    'umumnya', 'ungkap', 'ungkapnya', 'untuk', 'usah', 'usai', 'waduh', 'wah', 'wahai', 'waktu',
    'waktunya', 'walau', 'walaupun', 'wong', 'yaitu', 'yakin', 'yakni', 'yang'
}

# Flag untuk menandai status download resources
nltk_resources_downloaded = False

def download_nltk_resources():
    """Download NLTK resources jika belum didownload."""
    global nltk_resources_downloaded
    
    if nltk_resources_downloaded:
        return
    
    try:
        nltk.data.find('corpora/stopwords')
        nltk_resources_downloaded = True
    except LookupError:
        logger.info("Downloading NLTK resources...")
        nltk.download('stopwords', quiet=True)
        nltk_resources_downloaded = True
        logger.info("NLTK resources downloaded.")

# Tabel translasi untuk menghapus tanda baca (lebih cepat)
PUNCT_TABLE = str.maketrans('', '', string.punctuation)

# Fungsi normalisasi teks dengan caching
@lru_cache(maxsize=50000)
def normalize_text(text):
    """Mengubah teks menjadi huruf kecil dan menghapus tanda baca."""
    if not isinstance(text, str) or not text.strip():
        return ""
    
    # Lakukan case folding dan punctuation removal sekaligus
    # Menggunakan tabel translasi yang sudah dibuat untuk kinerja lebih cepat
    return text.lower().translate(PUNCT_TABLE)

# Fungsi tokenisasi cepat
def tokenize_text(text):
    """Tokenisasi cepat menggunakan split()."""
    if not isinstance(text, str) or not text.strip():
        return []
    
    # Gunakan split() standar - jauh lebih cepat daripada word_tokenize
    return text.split()

# Cache stopwords untuk performa
@lru_cache(maxsize=10)
def get_stopwords(language='indonesian'):
    """Mendapatkan stopwords dengan caching."""
    # Untuk bahasa Indonesia, selalu gunakan daftar kustom
    if language == 'indonesian' or language == 'id':
        return INDONESIAN_STOPWORDS
    
    try:
        # Untuk bahasa lain, coba gunakan NLTK
        stop_words = set(stopwords.words(language))
        return stop_words
    except Exception as e:
        logger.warning(f"Stopwords error untuk bahasa {language}: {e}, menggunakan daftar Indonesia")
        return INDONESIAN_STOPWORDS

# Fungsi untuk menghapus stopwords
def remove_stopwords(tokens, language='indonesian'):
    """Menghapus stopwords dari daftar token."""
    if not tokens:
        return []
    
    stop_words = get_stopwords(language)
    return [word for word in tokens if word.lower() not in stop_words]

# Inisialisasi variabel untuk stemmer
sastrawi_stemmer = None
porter_stemmer = None

# Fungsi untuk mendapatkan stemmer dengan caching
def get_stemmer(language='id'):
    """Mendapatkan stemmer dengan caching."""
    global sastrawi_stemmer, porter_stemmer
    
    if language == 'id':
        if sastrawi_stemmer is not None:
            return sastrawi_stemmer
        
        try:
            from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
            factory = StemmerFactory()
            sastrawi_stemmer = factory.create_stemmer()
            return sastrawi_stemmer
        except ImportError:
            logger.warning("Sastrawi tidak tersedia. Menggunakan PorterStemmer sebagai fallback")
            if porter_stemmer is None:
                porter_stemmer = PorterStemmer()
            return porter_stemmer
    
    # Untuk bahasa lain atau fallback, gunakan Porter stemmer
    if porter_stemmer is None:
        porter_stemmer = PorterStemmer()
    return porter_stemmer

# Kamus untuk menyimpan hasil stemming
stem_cache = {}

# Fungsi stemming dengan caching untuk kinerja lebih baik
@lru_cache(maxsize=100000)
def stem_word(word, language='id'):
    """Melakukan stemming pada sebuah kata dengan caching."""
    # Skip kata pendek (≤ 3 karakter) untuk kinerja yang lebih baik
    if not word or len(word) <= 3:
        return word
    
    # Cek cache untuk kata ini
    cache_key = f"{word}_{language}"
    if cache_key in stem_cache:
        return stem_cache[cache_key]
    
    # Jika tidak ada di cache, lakukan stemming
    stemmer = get_stemmer(language)
    if stemmer is not None:
        try:
            stemmed = stemmer.stem(word)
            stem_cache[cache_key] = stemmed
            return stemmed
        except Exception:
            # Fallback ke kata asli jika stemming gagal
            stem_cache[cache_key] = word
            return word
    
    # Jika tidak ada stemmer tersedia, kembalikan kata asli
    stem_cache[cache_key] = word
    return word

# Fungsi untuk melakukan stemming pada daftar token
def stem_tokens(tokens, language='id'):
    """Melakukan stemming pada daftar token."""
    if not tokens:
        return []
    
    return [stem_word(token, language) for token in tokens]

# Fungsi utama untuk NLP preprocessing
def nlp_preprocess(text):
    """Melakukan serangkaian preprocessing NLP pada teks."""
    if not isinstance(text, str) or not text.strip():
        return ""
    
    # 1-2. Normalisasi (case folding & punctuation removal)
    normalized = normalize_text(text)
    
    # 3. Tokenisasi
    tokens = tokenize_text(normalized)
    
    # 4. Stopword removal
    filtered = remove_stopwords(tokens, 'indonesian')
    
    # 5. Stemming (hanya jika ada token setelah stopword removal)
    if filtered:
        stemmed = stem_tokens(filtered, 'id')
        return ' '.join(stemmed)
    else:
        return ""

# Fungsi untuk memproses satu batch
def process_chunk(texts_chunk):
    """Memproses satu batch/chunk teks."""
    return [nlp_preprocess(text) for text in texts_chunk]

# Versi multiprocessing untuk memproses batch teks
def process_batch(texts, batch_size=500):
    """Memproses batch teks secara paralel menggunakan multiprocessing."""
    if not texts:
        return []
    
    # Pastikan resources telah didownload
    download_nltk_resources()
    
    # Batasi jumlah item yang diproses untuk menghindari memory overload
    texts = [t if isinstance(t, str) else "" for t in texts]
    
    # Jika dataset kecil, proses langsung tanpa multiprocessing
    if len(texts) < 1000:
        logger.info(f"Dataset kecil ({len(texts)} item), memproses secara sekuensial")
        return [nlp_preprocess(text) for text in texts]
    
    # Bagi data menjadi beberapa chunk untuk multiprocessing
    chunks = []
    for i in range(0, len(texts), batch_size):
        chunks.append(texts[i:i+batch_size])
    
    logger.info(f"Memproses {len(texts)} item dalam {len(chunks)} chunk menggunakan {NUM_PROCESSES} proses")
    
    # Gunakan multiprocessing untuk pemrosesan paralel
    results = []
    start_time = time.time()
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_PROCESSES) as executor:
        chunk_results = list(executor.map(process_chunk, chunks))
    
    # Gabungkan hasil dari semua chunks
    for chunk_result in chunk_results:
        results.extend(chunk_result)
    
    elapsed = time.time() - start_time
    logger.info(f"Selesai memproses {len(texts)} item dalam {elapsed:.2f} detik ({len(texts)/elapsed:.1f} item/detik)")
    
    return results

def preprocess_dataframe(df, output_file=None, vectorize=False, batch_size=500):
    """
    Melakukan preprocessing NLP pada DataFrame untuk semua kolom (Title, Link, Authors, Year, Cited).
    """
    logger.info("Memulai preprocessing NLP...")
    start_time = time.time()
    
    # Pastikan NLTK resources tersedia
    download_nltk_resources()
    
    # Copy DataFrame untuk menghindari perubahan pada original
    result_df = df.copy()
    
    # Periksa apakah kolom yang dibutuhkan ada di DataFrame
    required_columns = ['Title', 'Link', 'Authors', 'Year', 'Cited']
    missing_columns = [col for col in required_columns if col not in result_df.columns]
    
    if missing_columns:
        logger.warning(f"Kolom berikut tidak ditemukan: {', '.join(missing_columns)}")
        # Tambahkan kolom kosong untuk yang hilang
        for col in missing_columns:
            result_df[col] = ""
    
    # DataFrame untuk hasil preprocessing
    processed_df = pd.DataFrame(index=result_df.index)
    
    # 1. Preprocessing Title - paling penting
    logger.info("Preprocessing kolom Title...")
    title_texts = result_df['Title'].fillna('').astype(str).tolist()
    processed_df['Title'] = process_batch(title_texts, batch_size)
    
    # 2. Preprocessing Link (normalisasi saja karena ini URL)
    logger.info("Preprocessing kolom Link...")
    processed_df['Link'] = result_df['Link'].fillna('').apply(lambda x: x.lower().strip() if isinstance(x, str) else "")
    
    # 3. Preprocessing Authors
    logger.info("Preprocessing kolom Authors...")
    author_texts = result_df['Authors'].fillna('').astype(str).tolist()
    processed_df['Authors'] = process_batch(author_texts, batch_size)
    
    # 4. Preprocessing Year (ekstrak dan bersihkan)
    logger.info("Preprocessing kolom Year...")
    processed_df['Year'] = result_df['Year'].fillna('').astype(str).apply(lambda x: 
        re.search(r'(19|20)\d{2}', str(x)).group(0) if re.search(r'(19|20)\d{2}', str(x)) else "Unknown")
    
    # 5. Preprocessing Cited (konversi ke numerik)
    logger.info("Preprocessing kolom Cited...")
    processed_df['Cited'] = result_df['Cited'].fillna('0').astype(str).apply(lambda x: 
        re.sub(r'[^\d]', '', str(x)) if str(x).strip() else "0")
    processed_df['Cited'] = pd.to_numeric(processed_df['Cited'], errors='coerce').fillna(0).astype(int)
    
    # Vektorisasi Title (opsional)
    if vectorize:
        logger.info("Melakukan vektorisasi teks judul...")
        # Filter teks kosong
        mask = processed_df['Title'].astype(str).str.strip() != ''
        texts_to_vectorize = processed_df.loc[mask, 'Title'].tolist()
        
        if texts_to_vectorize:
            try:
                # TF-IDF Vectorization
                vectorizer = TfidfVectorizer(max_features=1000)
                tfidf_matrix = vectorizer.fit_transform(texts_to_vectorize)
                
                # Simpan vectorizer dan matriks fitur
                if output_file:
                    vectorizer_file = f"{os.path.splitext(output_file)[0]}_tfidf_vectorizer.pkl"
                    joblib.dump(vectorizer, vectorizer_file)
                    logger.info(f"Vectorizer disimpan ke {vectorizer_file}")
                    
                    # Simpan matriks fitur
                    feature_file = f"{os.path.splitext(output_file)[0]}_tfidf_features.pkl"
                    joblib.dump(tfidf_matrix, feature_file)
                    logger.info(f"Feature matrix disimpan ke {feature_file}")
            except Exception as e:
                logger.error(f"Error dalam vektorisasi: {e}")
        else:
            logger.warning("Tidak ada teks yang dapat divektorisasi setelah preprocessing")
    
    # Simpan hasil ke file
    if output_file:
        try:
            processed_df.to_csv(output_file, index=False)
            logger.info(f"Hasil preprocessing NLP disimpan ke {output_file}")
        except Exception as e:
            logger.error(f"Gagal menyimpan hasil ke file: {e}")
    
    total_time = time.time() - start_time
    logger.info(f"Preprocessing NLP selesai dalam {total_time:.2f} detik!")
    return processed_df

# Main function untuk memproses file CSV
def process_nlp(input_file, output_file=None, vectorize=True, translate=False):
    """
    Memproses file CSV dan melakukan preprocessing NLP pada semua kolom.
    
    Args:
        input_file: Path ke file CSV
        output_file: Path untuk menyimpan hasil (jika None, akan menggunakan nama input + '_nlp')
        vectorize: Flag untuk melakukan vektorisasi pada teks
        translate: Flag untuk menerjemahkan (tidak berpengaruh, karena fitur ini tidak diimplementasikan)
    
    Returns:
        Path ke file hasil preprocessing
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File {input_file} tidak ditemukan")
    
    # Buat nama file output jika tidak disediakan
    if output_file is None:
        filename, ext = os.path.splitext(input_file)
        output_file = f"{filename}_nlp{ext}"
    
    logger.info(f"=== Memulai preprocessing NLP untuk file {input_file} ===")
    start_time = time.time()
    
    try:
        # Baca file CSV dengan opsi toleran
        logger.info(f"Membaca file {input_file}...")
        try:
            # Gunakan engine Python yang lebih toleran
            df = pd.read_csv(input_file, on_bad_lines='warn', engine='python')
        except Exception as e:
            logger.warning(f"Error membaca CSV dengan pandas default: {e}")
            logger.info("Mencoba metode alternatif...")
            df = pd.read_csv(input_file, on_bad_lines='skip', encoding='utf-8', engine='python')
        
        # Periksa apakah kolom yang diperlukan ada
        required_columns = ['Title', 'Link', 'Authors', 'Year', 'Cited']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"Kolom tidak lengkap: {', '.join(missing_columns)} tidak ditemukan.")
            # Tambahkan kolom kosong jika tidak ada
            for col in missing_columns:
                df[col] = ""
        
        # Deteksi ukuran dataset
        num_rows = len(df)
        logger.info(f"Dataset berisi {num_rows} baris")
        
        # Ukuran batch: sesuaikan berdasarkan jumlah baris
        if num_rows <= 1000:
            batch_size = 200
        elif num_rows <= 5000:
            batch_size = 500
        else:
            batch_size = 1000
            
        # Bagi dataset untuk dataset besar
        if num_rows > 10000:
            logger.info(f"Dataset besar terdeteksi ({num_rows} baris). Memproses dalam beberapa bagian...")
            
            # Berapa bagian yang dibutuhkan 
            chunk_size = 5000 # Proses 5000 baris sekaligus
            num_chunks = (num_rows // chunk_size) + (1 if num_rows % chunk_size > 0 else 0)
            logger.info(f"Akan memproses dalam {num_chunks} bagian...")
            
            # Siapkan untuk hasil gabungan
            all_processed = []
            
            for i in range(0, num_rows, chunk_size):
                chunk_end = min(i + chunk_size, num_rows)
                logger.info(f"Memproses bagian {i//chunk_size + 1}/{num_chunks} (baris {i+1}-{chunk_end})...")
                
                # Proses chunk
                chunk_df = df.iloc[i:chunk_end].copy()
                processed_chunk = preprocess_dataframe(
                    chunk_df,
                    output_file=None,
                    vectorize=False,
                    batch_size=batch_size
                )
                
                all_processed.append(processed_chunk)
                
                # Bebaskan memori
                del chunk_df
                import gc; gc.collect()
            
            # Gabungkan hasil
            logger.info("Menggabungkan hasil semua bagian...")
            final_df = pd.concat(all_processed, ignore_index=True)
            
            # Simpan hasil
            final_df.to_csv(output_file, index=False)
            logger.info(f"Hasil NLP preprocessing disimpan ke {output_file}")
            
            # Vektorisasi
            if vectorize:
                try:
                    logger.info("Melakukan vektorisasi pada hasil gabungan...")
                    # Filter teks kosong
                    mask = final_df['Title'].str.strip() != ''
                    texts = final_df.loc[mask, 'Title'].tolist()
                    
                    if texts:
                        # TF-IDF Vectorization
                        vectorizer = TfidfVectorizer(max_features=1000)
                        tfidf_matrix = vectorizer.fit_transform(texts)
                        
                        # Simpan vectorizer dan feature matrix
                        vectorizer_file = f"{os.path.splitext(output_file)[0]}_tfidf_vectorizer.pkl"
                        joblib.dump(vectorizer, vectorizer_file)
                        logger.info(f"Vectorizer disimpan ke {vectorizer_file}")
                        
                        feature_file = f"{os.path.splitext(output_file)[0]}_tfidf_features.pkl"
                        joblib.dump(tfidf_matrix, feature_file)
                        logger.info(f"Feature matrix disimpan ke {feature_file}")
                except Exception as e:
                    logger.error(f"Error dalam vektorisasi: {e}")
        else:
            # Jika dataset relatif kecil, proses sekaligus
            logger.info(f"Memproses {num_rows} baris data sekaligus...")
            processed_df = preprocess_dataframe(
                df,
                output_file=output_file,
                vectorize=vectorize,
                batch_size=batch_size
            )
        
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        
        if minutes > 0:
            time_msg = f"{minutes} menit {seconds:.1f} detik"
        else:
            time_msg = f"{seconds:.1f} detik"
            
        logger.info(f"=== Preprocessing NLP selesai dalam {time_msg} ({elapsed_time/num_rows:.4f} detik/baris) ===")
        
        return output_file
        
    except Exception as e:
        logger.error(f"Error dalam preprocessing NLP: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise 