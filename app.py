import streamlit as st
import pandas as pd
import os

# ============================================================
# 1. KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="Bedah Kasus 3 - Dashboard",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# 2. FUNGSI LOAD DATA (PENCARI OTOMATIS)
# ============================================================
@st.cache_data
def load_data():
    # Script ini akan mencari file .csv apa saja di foldernya
    # Jika Anda punya nama file spesifik, ubah di bawah ini:
    nama_file = "data_kasus_3.csv" # <-- GANTI dengan nama file CSV Anda nanti
    
    kandidat_path = [
        nama_file,
        f"bedah_kasus_3/{nama_file}",
        "data.csv", "dataset.csv", "data_sintesis.csv" # Opsi cadangan
    ]
    
    # Cari file yang benar-benar ada
    for path in kandidat_path:
        if os.path.exists(path):
            return pd.read_csv(path)

    # Jika belum ada file sama sekali
    st.warning("⚠️ File data CSV belum ditemukan di repository.")
    st.info("Silakan klik 'Add file' > 'Upload files' di GitHub untuk mengunggah file CSV Anda, lalu sesuaikan nama filenya di dalam kode `app.py` pada variabel `nama_file`.")
    st.stop()

# Panggil fungsi load data
df = load_data()

# --- OTOMATISASI TANGGAL ---
# Jika ada kolom tanggal, ubah ke format datetime agar bisa dibuat grafik tren
kolom_tanggal = [col for col in df.columns if 'tanggal' in col.lower() or 'date' in col.lower() or 'waktu' in col.lower()]
if kolom_tanggal:
    df[kolom_tanggal[0]] = pd.to_datetime(df[kolom_tanggal[0]], errors='coerce')

# ============================================================
# 3. SIDEBAR - FILTER DATA
# ============================================================
st.sidebar.header("🔎 Filter Data")
filtered_df = df.copy()

# Filter otomatis untuk kolom teks/kategori
for col in df.select_dtypes(include=["object", "category"]).columns:
    unique_vals = df[col].dropna().unique().tolist()
    if 1 < len(unique_vals) <= 30: 
        pilihan = st.sidebar.multiselect(f"Pilih {col}:", options=unique_vals, default=unique_vals)
        filtered_df = filtered_df[filtered_df[col].isin(pilihan)]

# Filter untuk kolom angka
for col in df.select_dtypes(include=["number"]).columns:
    min_val = float(df[col].min())
    max_val = float(df[col].max())
    if min_val < max_val:
        rentang = st.sidebar.slider(
            f"Rentang {col}:",
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val)
        )
        filtered_df = filtered_df[
            (filtered_df[col] >= rentang[0]) & (filtered_df[col] <= rentang[1])
        ]

# ============================================================
# 4. HALAMAN UTAMA - METRIK
# ============================================================
st.title("📊 Dashboard Bedah Kasus 3")
st.markdown("Aplikasi ini menampilkan data untuk Bedah Kasus 3.")

col1, col2 = st.columns(2)
col1.metric("📄 Total Baris Data", f"{len(filtered_df):,}")
col2.metric("📊 Total Kolom", f"{df.shape[1]}")

st.divider()

# ============================================================
# 5. TABEL & VISUALISASI DATA
# ============================================================
st.subheader("📋 Tabel Data")
st.dataframe(filtered_df, use_container_width=True)

st.subheader("📈 Visualisasi Otomatis")

# Visualisasi Time Series jika ada tanggal
if kolom_tanggal:
    st.markdown(f"**Tren Berdasarkan Waktu ({kolom_tanggal[0]})**")
    tren = filtered_df.groupby(filtered_df[kolom_tanggal[0]].dt.date).size().reset_index(name='Jumlah')
    tren.set_index(kolom_tanggal[0], inplace=True)
    st.line_chart(tren)

# Visualisasi Kategori (Bar Chart)
for col in filtered_df.select_dtypes(include=["object", "category"]).columns:
    if 1 < filtered_df[col].nunique() <= 15:
        st.markdown(f"**Distribusi Berdasarkan {col}**")
        st.bar_chart(filtered_df[col].value_counts())

# Visualisasi Angka (Histogram Sederhana)
num_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
if num_cols:
    kolom_grafik = st.selectbox("Pilih kolom angka untuk melihat sebaran:", num_cols)
    st.bar_chart(filtered_df[kolom_grafik].value_counts().sort_index())

# ============================================================
# 6. STATISTIK & DOWNLOAD
# ============================================================
with st.expander("📈 Lihat Statistik Deskriptif"):
    st.write(filtered_df.describe(include="all"))

st.subheader("⬇️ Unduh Data")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Data Terfilter (CSV)",
    data=csv,
    file_name="data_kasus_3_terfilter.csv",
    mime="text/csv",
)
