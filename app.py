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
def default_pedoman():
    return pd.DataFrame({
        "Nama Akun": [
            "Penjualan Produk", "Pendapatan Sewa", "Pendapatan Lainnya",
            "Beban Operasional", "Beban Administrasi", "Gaji & Tunjangan", "Pajak",
            "Kas", "Bank", "Piutang", "Utang", "Modal Awal", "Penambahan Modal", "Prive", "Laba Ditahan", "Laba Tahun Berjalan"
        ],
        "Kategori": [
            "Pendapatan", "Pendapatan", "Pendapatan",
            "Beban Operasional", "Beban Administrasi", "Beban Administrasi", "Beban Administrasi",
            "Aset", "Aset", "Aset", "Kewajiban", "Ekuitas", "Ekuitas", "Ekuitas", "Ekuitas", "Ekuitas"
        ],
        "Tipe": [
            "Kredit", "Kredit", "Kredit",
            "Debit", "Debit", "Debit", "Debit",
            "Debit", "Debit", "Debit", "Kredit", "Kredit", "Kredit", "Debit", "Kredit", "Kredit"
        ]
    })

if "pedoman_akun" not in st.session_state:
    st.session_state["pedoman_akun"] = default_pedoman()

st.markdown("### 📘 Pedoman Daftar Akun")
st.dataframe(st.session_state["pedoman_akun"], use_container_width=True)

# ========= TAMBAH AKUN MANUAL =========
st.markdown("### ➕ Tambah Akun Manual")
with st.form("form_tambah_akun"):
    nama_baru = st.text_input("Nama Akun Baru")
    kategori_baru = st.selectbox("Kategori", ["Pendapatan", "Beban Operasional", "Beban Administrasi", "Aset", "Kewajiban", "Ekuitas"])
    tipe_baru = st.selectbox("Tipe", ["Debit", "Kredit"])
    tambah_akun = st.form_submit_button("Tambah Akun")

    if tambah_akun and nama_baru:
        akun_baru = pd.DataFrame({"Nama Akun": [nama_baru], "Kategori": [kategori_baru], "Tipe": [tipe_baru]})
        st.session_state["pedoman_akun"] = pd.concat([st.session_state["pedoman_akun"], akun_baru], ignore_index=True)
        st.success(f"Akun '{nama_baru}' berhasil ditambahkan.")

# Selanjutnya akan disambung dengan: Input Transaksi, Jurnal, Laporan Keuangan
# Laporan akan menggunakan kategori di atas sebagai struktur dasar
# Ekspansi laporan dan export PDF akan dibuat setelah ini
