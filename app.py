import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import os

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# === PILIHAN MULTI LEMBAGA DAN DESA ===
st.sidebar.title("🔰 Pilih Unit Lembaga")
lembaga = st.sidebar.selectbox("Lembaga", ["BUMDes", "PKK", "Karang Taruna", "LPMD", "BPD"])
desa = st.sidebar.text_input("Nama Desa", "Keling")
nama_bumdes = st.sidebar.text_input("Nama Lembaga", "Buwana Raharja")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

# === PEJABAT UNTUK PENGESAHAN ===
st.sidebar.markdown("---")
st.sidebar.subheader("Pejabat Tanda Tangan")
bendahara = st.sidebar.text_input("Nama Bendahara", "Siti Aminah")
direktur = st.sidebar.text_input("Nama Ketua/Pimpinan", "Bambang Setiawan")
kepala_desa = st.sidebar.text_input("Nama Kepala Desa", "Sugeng Riyadi")
ketua_bpd = st.sidebar.text_input("Nama Ketua BPD", "Dwi Purnomo")

# === LOGO ===
col_logo1, col_logo2 = st.columns([1, 6])
with col_logo1:
    if os.path.exists("logo_pemdes.png"):
        st.image("logo_pemdes.png", width=80)
with col_logo2:
    if os.path.exists("logo_bumdes.png"):
        st.image("logo_bumdes.png", width=80)

# === KOP LAPORAN ===
st.markdown("""
<h3 style='text-align:center;'>Laporan Keuangan BUMDes Buwana Raharja Desa Keling</h3>
<p style='text-align:center;'>Alamat: Jl. Raya Keling, Bukaan, Keling, Kec. Kepung, Kabupaten Kediri, Jawa Timur 64293</p>
<hr>
""", unsafe_allow_html=True)

# === CHART OF ACCOUNTS ===
daftar_akun = {
    "1-100 - Kas": "Kas",
    "1-110 - Piutang Usaha": "Piutang",
    "1-120 - Peralatan": "Peralatan",
    "2-100 - Utang Usaha": "Utang",
    "3-100 - Modal Awal": "Modal",
    "3-200 - Penambahan Modal": "Penambahan Modal",
    "3-300 - Prive": "Prive",
    "4-100 - Pendapatan Jasa": "Pendapatan",
    "4-200 - Pendapatan Produk": "Pendapatan",
    "5-100 - Beban Operasional": "Beban",
    "5-200 - Beban Penyusutan": "Beban"
}

# === INISIALISASI ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Kategori", "Debit", "Kredit", "Keterangan"])

# === FORM TAMBAH TRANSAKSI ===
with st.expander("➕ Tambah Transaksi"):
    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal", datetime.today())
    with col2:
        pilihan_akun = st.selectbox("Pilih Akun", list(daftar_akun.keys()))

    col3, col4 = st.columns(2)
    with col3:
        debit = st.number_input("Debit", min_value=0.0, format="%.2f")
    with col4:
        kredit = st.number_input("Kredit", min_value=0.0, format="%.2f")

    keterangan = st.text_input("Keterangan")

    if st.button("💾 Simpan Transaksi"):
        kode, nama = pilihan_akun.split(" - ")
        kategori = daftar_akun[pilihan_akun]
        new_row = pd.DataFrame([{
            "Tanggal": tanggal.strftime("%Y-%m-%d"),
            "Kode Akun": kode,
            "Nama Akun": nama,
            "Kategori": kategori,
            "Debit": debit,
            "Kredit": kredit,
            "Keterangan": keterangan
        }])
        st.session_state[key_gl] = pd.concat([st.session_state[key_gl], new_row], ignore_index=True)
        st.success("✅ Transaksi berhasil disimpan.")

# === TAMPILKAN GL ===
st.subheader("📋 General Ledger")
df_gl = st.session_state[key_gl]
st.dataframe(df_gl, use_container_width=True)

# === CATATAN ===
st.info("Kode akun akan digunakan sistem untuk mengelompokkan data ke dalam Laporan Laba Rugi, Neraca, dan Arus Kas secara otomatis.")
