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

# ========= PEDOMAN AKUN TERSTRUKTUR =========
pedoman_data = {
    "Nama Akun": [
        # Pendapatan Usaha
        "Penjualan Barang Dagang", "Pendapatan Sewa", "Pendapatan Jasa", 
        # Beban Operasional
        "Pembelian Barang Dagang", "Gaji & Tunjangan", "Penyusutan", 
        # Beban Administrasi
        "Beban ATK", "Beban Listrik", "Beban Lainnya", 
        # Ekuitas
        "Modal Awal", "Laba Ditahan", "Laba Tahun Berjalan", "Prive", 
        # Aset
        "Kas", "Bank", "Piutang", 
        # Kewajiban
        "Utang",
    ],
    "Posisi": [
        "Pendapatan Usaha", "Pendapatan Usaha", "Pendapatan Usaha",
        "Beban Operasional", "Beban Operasional", "Beban Operasional",
        "Beban Administrasi", "Beban Administrasi", "Beban Administrasi",
        "Ekuitas", "Ekuitas", "Ekuitas", "Ekuitas",
        "Aset", "Aset", "Aset",
        "Kewajiban"
    ],
    "Tipe": [
        "Kredit", "Kredit", "Kredit",
        "Debit", "Debit", "Debit",
        "Debit", "Debit", "Debit",
        "Kredit", "Kredit", "Kredit", "Debit",
        "Debit", "Debit", "Debit",
        "Kredit"
    ]
}
pedoman_akun = pd.DataFrame(pedoman_data)

with st.expander("📚 Pedoman Akun Terstruktur (Laporan Laba Rugi, Neraca, Ekuitas)"):
    st.dataframe(pedoman_akun, use_container_width=True)

# ========== LANGKAH SELANJUTNYA ==========
st.success("✅ Struktur akun standar laporan keuangan telah diterapkan.")
st.info("Langkah berikutnya: integrasikan perhitungan & tampilan laporan Laba Rugi, Neraca, Arus Kas, dan Ekuitas secara otomatis berdasarkan struktur akun ini.")
