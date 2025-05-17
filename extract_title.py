import pandas as pd

# Baca file CSV dari path yang diberikan
df = pd.read_csv("data/sinta_articles_2503_to_3336_processed_nlp.csv")

# Ambil hanya kolom 'Title'
df_title = df[["Title"]].copy()


# Simpan ke file baru
df_title.to_csv("data/judul_saja.csv", index=False)

print("File 'judul_saja.csv' berhasil dibuat di folder 'data/'")
