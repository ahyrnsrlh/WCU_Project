import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import os

# Path file
LABEL_FILE = os.path.join('data', 'label_sdgs.csv')
UNLABELED_FILE = os.path.join('data', 'sinta_articles_2503_to_3336_processed_nlp.csv')
OUTPUT_FILE = os.path.join('data', 'sinta_articles_2503_to_3336_labeled.csv')

# 1. Load data label (data latih)
df_labeled = pd.read_csv(LABEL_FILE)
# 2. Load data artikel yang akan dilabeli
df_unlabeled = pd.read_csv(UNLABELED_FILE)

# 3. Siapkan fitur dan label (gunakan kolom Title)
vectorizer = TfidfVectorizer(max_features=1000)
X_labeled = vectorizer.fit_transform(df_labeled['Title'].astype(str))
y_labeled = df_labeled['label'] if 'label' in df_labeled.columns else df_labeled['annotation_id']

# 4. Latih model
model = RandomForestClassifier(random_state=42)
model.fit(X_labeled, y_labeled)

# 5. Transformasi data yang belum berlabel
X_unlabeled = vectorizer.transform(df_unlabeled['Title'].astype(str))

# 6. Prediksi label SDGs
predicted_labels = model.predict(X_unlabeled)
df_unlabeled['predicted_sdgs'] = predicted_labels

# 7. Simpan hasil ke file baru
df_unlabeled.to_csv(OUTPUT_FILE, index=False)
print(f"Hasil labeling otomatis disimpan di: {OUTPUT_FILE}")

# ======================
# EXPORT UNLABELED DATA
# ======================

import pandas as pd
import os

# File hasil labeling otomatis
LABELED_FILE = os.path.join('data', 'sinta_articles_2503_to_3336_labeled.csv')
OUTPUT_FILE = os.path.join('data', 'unlabeled_for_review.csv')

# Daftar label SDGs yang valid (bisa diupdate sesuai kebutuhan)
VALID_SDGS = [
    'SDG 1: Tanpa Kemiskinan',
    'SDG 2: Tanpa Kelaparan',
    'SDG 3: Kehidupan Sehat dan Sejahtera',
    'SDG 4: Pendidikan Berkualitas',
    'SDG 5: Kesetaraan Gender',
    'SDG 6: Air Bersih dan Sanitasi Layak',
    'SDG 7: Energi Bersih dan Terjangkau',
    'SDG 8: Pekerjaan Layak dan Pertumbuhan Ekonomi',
    'SDG 9: Industri, Inovasi, dan Infrastruktur',
    'SDG 10: Berkurangnya Kesenjangan',
    'SDG 11: Kota dan Permukiman yang Berkelanjutan',
    'SDG 12: Konsumsi dan Produksi yang Bertanggung Jawab',
    'SDG 13: Penanganan Perubahan Iklim',
    'SDG 14: Ekosistem Laut',
    'SDG 15: Ekosistem Daratan',
    'SDG 16: Perdamaian, Keadilan, dan Kelembagaan yang Tangguh',
    'SDG 17: Kemitraan untuk Mencapai Tujuan'
]

def is_valid_label(label):
    if pd.isna(label) or str(label).strip() == '':
        return False
    # Cek jika label adalah salah satu SDG atau string JSON list SDG
    if label in VALID_SDGS:
        return True
    if label.startswith('{"choices"') or label.startswith('["SDG'):
        return True
    return False

# Load data hasil labeling
df = pd.read_csv(LABELED_FILE)

# Filter data yang belum terlabeli SDGs dengan benar
unlabeled = df[~df['predicted_sdgs'].apply(is_valid_label)]

# Simpan ke file baru
unlabeled.to_csv(OUTPUT_FILE, index=False)
print(f"Data yang belum terlabeli SDGs disimpan di: {OUTPUT_FILE}")