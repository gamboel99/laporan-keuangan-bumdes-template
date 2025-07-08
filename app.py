# ================================================
#  APLIKASI ACCOUNTING: LAPORAN KEUANGAN BUMDes BUWANA RAHARJA
# ================================================

import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# ======== SIDEBAR IDENTITAS DESA/LEMBAGA ========
st.sidebar.title("🧾 Identitas Lembaga")
desa = st.sidebar.text_input("Nama Desa", "Keling")
lembaga = st.sidebar.selectbox("Nama Lembaga", ["BUMDes", "TPK", "LPMD", "Karang Taruna", "Posyandu", "TSBD", "Pokmas"])
nama_bumdes = st.sidebar.text_input("Nama Unit", "Buwana Raharja")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

# === PEJABAT UNTUK PENGESAHAN ===
st.sidebar.markdown("---")
st.sidebar.subheader("Pejabat Tanda Tangan")
bendahara = st.sidebar.text_input("Bendahara", "Siti Aminah")
direktur = st.sidebar.text_input("Pimpinan", "Bambang Setiawan")
kepala_desa = st.sidebar.text_input("Kepala Desa", "Sugeng Riyadi")
ketua_bpd = st.sidebar.text_input("Ketua BPD", "Dwi Purnomo")

# ========= HEADER & LOGO =========
col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    if os.path.exists("logo_pemdes.png"):
        st.image("logo_pemdes.png", width=80)
with col2:
    st.markdown(f"""
        <h3 style='text-align:center;'>Laporan Keuangan {lembaga} {nama_bumdes} Desa {desa}</h3>
        <h5 style='text-align:center;'>Alamat: Jl. Raya Keling, Bukaan, Keling, Kec. Kepung, Kabupaten Kediri, Jawa Timur 64293</h5>
        <hr>
    """, unsafe_allow_html=True)
with col3:
    if os.path.exists("logo_bumdes.png"):
        st.image("logo_bumdes.png", width=80)

# ========= PEDOMAN AKUN =========
if "pedoman_akun" not in st.session_state:
    st.session_state["pedoman_akun"] = pd.DataFrame({
        "Nama Akun": [
            "Penjualan Barang Dagang", "Pendapatan Sewa", "Pendapatan Jasa", "Pendapatan Lainnya",
            "Pembelian Barang Dagang", "Beban Produksi", "Gaji & Tunjangan", "ATK", "Transportasi", "Penyusutan",
            "Kas", "Bank", "Piutang Dagang", "Utang Usaha", "Modal Awal", "Laba Ditahan", "Prive", "Laba Tahun Berjalan"
        ],
        "Kategori": [
            "Pendapatan Usaha", "Pendapatan Usaha", "Pendapatan Usaha", "Pendapatan Usaha",
            "Beban Operasional", "Beban Operasional", "Beban Operasional", "Beban Administrasi", "Beban Operasional", "Beban Administrasi",
            "Kas dari Aktivitas Operasi", "Kas dari Aktivitas Operasi", "Kas dari Aktivitas Operasi", "Kas dari Aktivitas Pendanaan",
            "Modal Awal", "Laba Tahun Berjalan", "Prive/Penambahan Modal", "Laba Tahun Berjalan"
        ],
        "Posisi": [
            "Pendapatan"]*4 + ["Beban"]*6 + ["Aset"]*3 + ["Kewajiban"] + ["Ekuitas"]*4,
        "Tipe": [
            "Kredit"]*4 + ["Debit"]*6 + ["Debit"]*3 + ["Kredit"] + ["Kredit"]*2 + ["Debit"] + ["Kredit"]
    })

pedoman_akun = st.session_state["pedoman_akun"]

with st.expander("📚 Pedoman Akun (Panduan Posisi Debit/Kredit)"):
    st.dataframe(pedoman_akun, use_container_width=True)

with st.expander("➕ Tambah Akun Baru"):
    nama_baru = st.text_input("Nama Akun Baru")
    kategori_baru = st.selectbox("Kategori", sorted(pedoman_akun["Kategori"].unique().tolist() + ["(Kategori Baru)"]))
    posisi_baru = st.selectbox("Posisi", ["Pendapatan", "Beban", "Aset", "Kewajiban", "Ekuitas"])
    tipe_baru = st.selectbox("Tipe", ["Debit", "Kredit"])
    if st.button("Tambah Akun"):
        st.session_state["pedoman_akun"] = pd.concat([pedoman_akun, pd.DataFrame([{
            "Nama Akun": nama_baru,
            "Kategori": kategori_baru,
            "Posisi": posisi_baru,
            "Tipe": tipe_baru
        }])], ignore_index=True)
        st.success("Akun berhasil ditambahkan.")

# ======= SISANYA TETAP DILANJUTKAN DI BAWAH =========
# (lanjutan script jurnal transaksi, laporan keuangan, ekspor, dan pengesahan)

# Silakan lanjutkan dari baris transaksi dan laporan sesuai struktur baru di atas
