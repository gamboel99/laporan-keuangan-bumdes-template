import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import os
from io import BytesIO

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

# === KOP LAPORAN ===
st.markdown(f"""
    <h3 style='text-align:center;'>Laporan Keuangan {lembaga} {nama_bumdes} Desa {desa}</h3>
    <h4 style='text-align:center;'>Alamat: Jl. Raya Keling, Bukaan, Keling, Kec. Kepung, Kabupaten Kediri, Jawa Timur 64293</h4>
    <hr>
""", unsafe_allow_html=True)

# === LOGO ===
col_logo1, col_logo2 = st.columns([1, 6])
with col_logo1:
    if os.path.exists("logo_pemdes.png"):
        st.image("logo_pemdes.png", width=80)
with col_logo2:
    if os.path.exists("logo_bumdes.png"):
        st.image("logo_bumdes.png", width=80)

st.title(f"📘 Buku Besar ({lembaga})")

# === INISIALISASI ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

# === DAFTAR AKUN ===
daftar_akun = pd.DataFrame({
    "Kode Akun": [
        "4.1.1", "4.1.2", "4.1.3", "4.1.4", "4.1.5", "4.1.6", "4.1.7",
        "5.1.1", "5.1.2", "5.1.3", "5.1.4", "5.1.5",
        "5.2.1", "5.2.2", "5.2.3", "5.2.4", "5.2.5", "5.2.6", "5.2.7", "5.2.8", "5.2.9", "5.2.10", "5.2.11",
        "4.2.1", "4.2.2", "4.2.3", "5.3.1", "5.3.2",
        "5.4.1", "5.4.2",
        "1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.5", "1.1.6", "1.1.7", "1.1.8",
        "1.2.1", "1.2.2", "1.2.3", "1.2.4", "1.2.5", "1.2.6", "1.2.7", "1.2.8", "1.2.9",
        "2.1.1", "2.1.2", "2.1.3", "2.1.4", "2.1.5", "2.2.1", "2.2.2", "2.2.3",
        "3.1.1", "3.1.2", "3.1.3", "3.1.4", "3.1.5"
    ],
    "Nama Akun": [
        "Penjualan Barang Dagang", "Pendapatan Jasa", "Pendapatan Sewa Aset", "Pendapatan Simpan Pinjam",
        "Pendapatan Usaha Tani", "Pendapatan Wisata", "Pendapatan Lainnya",
        "Pembelian Barang Dagang", "Beban Produksi", "Beban Pemeliharaan", "Beban Penyusutan Aset Usaha", "Beban Operasional Unit Usaha",
        "Gaji dan Tunjangan", "Beban Listrik", "Beban Transportasi", "Beban Administrasi", "Beban Sewa Tempat",
        "Beban Perlengkapan", "Beban Penyusutan Tetap", "Beban Pelatihan", "Beban Promosi", "Beban Wisata", "Beban Sosial",
        "Pendapatan Bunga", "Pendapatan Investasi", "Pendapatan Lain-lain", "Beban Bunga", "Kerugian Aset",
        "Pajak Penghasilan", "Pajak Final",
        "Kas", "Bank", "Piutang Usaha", "Persediaan Barang", "Persediaan Bahan Baku", "Uang Muka", "Investasi Pendek", "Pendapatan Belum Diterima",
        "Tanah", "Bangunan", "Peralatan Usaha", "Kendaraan", "Inventaris", "Aset Tetap Lainnya", "Akumulasi Penyusutan", "Investasi Panjang", "Aset Lain-lain",
        "Utang Usaha", "Utang Gaji", "Utang Pajak", "Pendapatan Diterima Dimuka", "Utang Lain-lain", "Pinjaman Bank", "Pinjaman Program", "Utang ke Pihak Ketiga",
        "Modal Desa", "Modal Pihak Ketiga", "Saldo Laba", "Laba Tahun Berjalan", "Cadangan Dana"
    ],
    "Posisi": (
        ["Laba Rugi"] * 30 +
        ["Neraca"] * 25 +
        ["Ekuitas"] * 5
    ),
    "Tipe": (
        ["Kredit"] * 7 + ["Debit"] * 5 + ["Debit"] * 11 + ["Kredit"] * 3 + ["Debit"] * 2 + ["Debit"] * 2 +
        ["Debit"] * 8 + ["Debit"] * 9 + ["Kredit"] * 8 + ["Kredit"] * 5
    )
})

with st.expander("📚 Daftar Akun Standar (PSAK Rinci)"):
    st.dataframe(daftar_akun, use_container_width=True)

# TODO: Lanjutkan Laba Rugi Rinci, Arus Kas Otomatis, Neraca Rinci, Download PDF & Excel
