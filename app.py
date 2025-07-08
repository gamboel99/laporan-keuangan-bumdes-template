import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Laporan Keuangan Lembaga Desa", layout="wide")

# === PILIHAN MULTI LEMBAGA DAN DESA ===
st.sidebar.title("🔰 Pilih Unit Lembaga")
lembaga = st.sidebar.selectbox("Lembaga", ["BUMDes", "TPK", "LPMD", "Karang Taruna", "Posyandu", "TSBD", "Pokmas"])
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

# === PEDOMAN AKUN (REFERENSI MANUAL) ===
akun_data = [
    ("Penjualan Barang Dagang", "Pendapatan", "Kredit"),
    ("Pendapatan Jasa", "Pendapatan", "Kredit"),
    ("Pendapatan Sewa Aset", "Pendapatan", "Kredit"),
    ("Pendapatan Simpan Pinjam", "Pendapatan", "Kredit"),
    ("Pendapatan Usaha Tani", "Pendapatan", "Kredit"),
    ("Pendapatan Wisata", "Pendapatan", "Kredit"),
    ("Pendapatan Lainnya", "Pendapatan", "Kredit"),
    ("Pembelian Barang Dagang", "HPP", "Debit"),
    ("Beban Produksi", "HPP", "Debit"),
    ("Beban Pemeliharaan Usaha", "HPP", "Debit"),
    ("Beban Penyusutan Aset Usaha", "HPP", "Debit"),
    ("Bahan Baku / Operasional", "HPP", "Debit"),
    ("Beban Lainnya", "HPP", "Debit"),
    ("Gaji dan Tunjangan", "Beban Usaha", "Debit"),
    ("Listrik, Air, Komunikasi", "Beban Usaha", "Debit"),
    ("Transportasi", "Beban Usaha", "Debit"),
    ("Administrasi & Umum", "Beban Usaha", "Debit"),
    ("Sewa Tempat", "Beban Usaha", "Debit"),
    ("Perlengkapan", "Beban Usaha", "Debit"),
    ("Penyusutan Aset Tetap", "Beban Usaha", "Debit"),
    ("Penyuluhan", "Beban Usaha", "Debit"),
    ("Promosi & Publikasi", "Beban Usaha", "Debit"),
    ("Operasional Wisata", "Beban Usaha", "Debit"),
    ("CSR / Kegiatan Desa", "Beban Usaha", "Debit"),
    ("Pendapatan Bunga", "Non-Usaha", "Kredit"),
    ("Pendapatan Investasi", "Non-Usaha", "Kredit"),
    ("Pendapatan Lain-lain", "Non-Usaha", "Kredit"),
    ("Beban Bunga", "Non-Usaha", "Debit"),
    ("Kerugian Penjualan Aset", "Non-Usaha", "Debit"),
    ("Pajak", "Non-Usaha", "Debit"),
    ("Kas", "Aset Lancar", "Debit"),
    ("Bank", "Aset Lancar", "Debit"),
    ("Piutang Usaha", "Aset Lancar", "Debit"),
    ("Persediaan Dagang", "Aset Lancar", "Debit"),
    ("Persediaan Bahan Baku", "Aset Lancar", "Debit"),
    ("Uang Muka", "Aset Lancar", "Debit"),
    ("Investasi Pendek", "Aset Lancar", "Debit"),
    ("Pendapatan Diterima di Muka", "Aset Lancar", "Kredit"),
    ("Tanah", "Aset Tetap", "Debit"),
    ("Bangunan", "Aset Tetap", "Debit"),
    ("Peralatan", "Aset Tetap", "Debit"),
    ("Kendaraan", "Aset Tetap", "Debit"),
    ("Inventaris", "Aset Tetap", "Debit"),
    ("Aset Tetap Lainnya", "Aset Tetap", "Debit"),
    ("Akumulasi Penyusutan", "Aset Tetap", "Kredit"),
    ("Investasi Panjang", "Aset Tetap", "Debit"),
    ("Aset Lain-lain", "Aset Tetap", "Debit"),
    ("Utang Usaha", "Kewajiban Pendek", "Kredit"),
    ("Utang Gaji", "Kewajiban Pendek", "Kredit"),
    ("Utang Pajak", "Kewajiban Pendek", "Kredit"),
    ("Pendapatan Diterima Di Muka", "Kewajiban Pendek", "Kredit"),
    ("Utang Lain-lain", "Kewajiban Pendek", "Kredit"),
    ("Pinjaman Bank", "Kewajiban Panjang", "Kredit"),
    ("Pinjaman Pemerintah", "Kewajiban Panjang", "Kredit"),
    ("Utang Pihak Ketiga", "Kewajiban Panjang", "Kredit"),
    ("Modal Desa", "Ekuitas", "Kredit"),
    ("Modal Pihak Ketiga", "Ekuitas", "Kredit"),
    ("Saldo Laba Ditahan", "Ekuitas", "Kredit"),
    ("Laba Tahun Berjalan", "Ekuitas", "Kredit"),
    ("Cadangan Sosial / Investasi", "Ekuitas", "Kredit"),
]
pedoman_akun = pd.DataFrame(akun_data, columns=["Nama Akun", "Posisi", "Tipe"])

with st.expander("📚 Pedoman Daftar Akun (Manual)"):
    st.dataframe(pedoman_akun, use_container_width=True)

# Lanjutkan di blok selanjutnya: input transaksi, GL tabel, dan laporan otomatis
