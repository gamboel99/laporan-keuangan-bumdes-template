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

st.title(f"📘 Buku Besar ({lembaga})")

# === LOGO ===
col_logo1, col_logo2 = st.columns([1, 6])
with col_logo1:
    if os.path.exists("logo_pemdes.png"):
        st.image("logo_pemdes.png", width=80)
with col_logo2:
    if os.path.exists("logo_bumdes.png"):
        st.image("logo_bumdes.png", width=80)

# === TEMPLATE AKUN STANDAR ===
akun_template = pd.DataFrame([
    {"Kode": "4-100", "Akun": "Pendapatan Usaha", "Kategori": "Pendapatan", "Pos": "Kredit"},
    {"Kode": "5-100", "Akun": "Beban Operasional", "Kategori": "Beban", "Pos": "Debit"},
    {"Kode": "1-100", "Akun": "Kas", "Kategori": "Aset", "Pos": "Debit"},
    {"Kode": "1-200", "Akun": "Piutang Usaha", "Kategori": "Aset", "Pos": "Debit"},
    {"Kode": "1-300", "Akun": "Peralatan", "Kategori": "Aset", "Pos": "Debit"},
    {"Kode": "2-100", "Akun": "Utang Usaha", "Kategori": "Kewajiban", "Pos": "Kredit"},
    {"Kode": "3-100", "Akun": "Modal Awal", "Kategori": "Ekuitas", "Pos": "Kredit"},
    {"Kode": "3-200", "Akun": "Penambahan Modal", "Kategori": "Ekuitas", "Pos": "Kredit"},
    {"Kode": "3-300", "Akun": "Prive", "Kategori": "Ekuitas", "Pos": "Debit"},
])

st.markdown("### 🧾 Template Akun Standar")
st.dataframe(akun_template, use_container_width=True)

# === INISIALISASI ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode", "Akun", "Kategori", "Debit", "Kredit", "Keterangan", "Bukti"])

# === FORM TAMBAH TRANSAKSI ===
with st.expander("➕ Tambah Transaksi"):
    col1, col2, col3 = st.columns(3)
    with col1:
        tanggal = st.date_input("Tanggal", datetime.today())
    with col2:
        kode_pilihan = st.selectbox("Kode Akun", akun_template["Kode"])
    with col3:
        akun_row = akun_template[akun_template["Kode"] == kode_pilihan].iloc[0]
        akun = akun_row["Akun"]
        kategori = akun_row["Kategori"]

    col4, col5, col6 = st.columns(3)
    with col4:
        keterangan = st.text_input("Keterangan")
    with col5:
        debit = st.number_input("Debit", min_value=0.0, format="%.2f") if akun_row["Pos"] == "Debit" else 0.0
    with col6:
        kredit = st.number_input("Kredit", min_value=0.0, format="%.2f") if akun_row["Pos"] == "Kredit" else 0.0

    bukti_file = st.file_uploader("Upload Nota/Bukti", type=["png", "jpg", "jpeg", "pdf"])

    if st.button("💾 Simpan Transaksi"):
        if akun and (debit > 0 or kredit > 0):
            if bukti_file:
                bukti_path = f"bukti_{datetime.now().strftime('%Y%m%d%H%M%S')}_{bukti_file.name}"
                with open(bukti_path, "wb") as f:
                    f.write(bukti_file.read())
            else:
                bukti_path = ""
            new_row = pd.DataFrame([{
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Kode": kode_pilihan,
                "Akun": akun,
                "Kategori": kategori,
                "Debit": debit,
                "Kredit": kredit,
                "Keterangan": keterangan,
                "Bukti": bukti_path
            }])
            st.session_state[key_gl] = pd.concat([st.session_state[key_gl], new_row], ignore_index=True)
            st.success("✅ Transaksi berhasil disimpan.")
        else:
            st.warning("⚠️ Lengkapi akun dan nilai debit/kredit.")

# Tampilkan buku besar meski belum ada data
st.markdown("### 📋 Daftar Transaksi")
gl_df = st.session_state[key_gl]
if not gl_df.empty:
    st.dataframe(gl_df, use_container_width=True)
else:
    st.info("Belum ada transaksi. Silakan isi dari form di atas.")
