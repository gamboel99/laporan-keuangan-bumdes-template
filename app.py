import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import os
from io import BytesIO

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

st.title(f"📘 Buku Besar ({lembaga})")

# === INISIALISASI ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

# === DAFTAR AKUN STANDAR SISKEUDES ===
daftar_akun_data = [
    # Pendapatan
    ("4.1.1", "Penjualan Barang Dagang", "Pendapatan", "Kredit"),
    ("4.1.2", "Pendapatan Jasa", "Pendapatan", "Kredit"),
    ("4.1.3", "Pendapatan Sewa Aset", "Pendapatan", "Kredit"),
    ("4.1.4", "Pendapatan Simpan Pinjam", "Pendapatan", "Kredit"),
    ("4.1.5", "Pendapatan Usaha Tani", "Pendapatan", "Kredit"),
    ("4.1.6", "Pendapatan Wisata", "Pendapatan", "Kredit"),
    ("4.1.7", "Pendapatan Lainnya", "Pendapatan", "Kredit"),
    
    # HPP / Beban Pokok
    ("5.1.1", "Pembelian Barang Dagang", "HPP", "Debit"),
    ("5.1.2", "Beban Produksi", "HPP", "Debit"),
    ("5.1.3", "Beban Pemeliharaan Usaha", "HPP", "Debit"),
    ("5.1.4", "Beban Penyusutan Aset Usaha", "HPP", "Debit"),
    ("5.1.5", "Bahan Baku / Operasional", "HPP", "Debit"),
    ("5.1.6", "Beban Lainnya", "HPP", "Debit"),

    # Beban Operasional
    ("5.2.1", "Gaji dan Tunjangan", "Beban Usaha", "Debit"),
    ("5.2.2", "Listrik, Air, Komunikasi", "Beban Usaha", "Debit"),
    ("5.2.3", "Transportasi", "Beban Usaha", "Debit"),
    ("5.2.4", "Administrasi & Umum", "Beban Usaha", "Debit"),
    ("5.2.5", "Sewa Tempat", "Beban Usaha", "Debit"),
    ("5.2.6", "Perlengkapan", "Beban Usaha", "Debit"),
    ("5.2.7", "Penyusutan Aset Tetap", "Beban Usaha", "Debit"),
    ("5.2.8", "Penyuluhan", "Beban Usaha", "Debit"),
    ("5.2.9", "Promosi & Publikasi", "Beban Usaha", "Debit"),
    ("5.2.10", "Operasional Wisata", "Beban Usaha", "Debit"),
    ("5.2.11", "CSR / Kegiatan Desa", "Beban Usaha", "Debit"),

    # Non Usaha
    ("6.1", "Pendapatan Bunga", "Non-Usaha", "Kredit"),
    ("6.2", "Pendapatan Investasi", "Non-Usaha", "Kredit"),
    ("6.3", "Pendapatan Lain-lain", "Non-Usaha", "Kredit"),
    ("6.4", "Beban Bunga", "Non-Usaha", "Debit"),
    ("6.5", "Kerugian Penjualan Aset", "Non-Usaha", "Debit"),
    ("6.6", "Pajak", "Non-Usaha", "Debit"),

    # Aset Lancar
    ("1.1.1", "Kas", "Aset Lancar", "Debit"),
    ("1.1.2", "Bank", "Aset Lancar", "Debit"),
    ("1.1.3", "Piutang Usaha", "Aset Lancar", "Debit"),
    ("1.1.4", "Persediaan Dagang", "Aset Lancar", "Debit"),
    ("1.1.5", "Persediaan Bahan Baku", "Aset Lancar", "Debit"),
    ("1.1.6", "Uang Muka", "Aset Lancar", "Debit"),
    ("1.1.7", "Investasi Pendek", "Aset Lancar", "Debit"),
    ("1.1.8", "Pendapatan Diterima Di Muka", "Aset Lancar", "Kredit"),

    # Aset Tetap
    ("1.2.1", "Tanah", "Aset Tetap", "Debit"),
    ("1.2.2", "Bangunan", "Aset Tetap", "Debit"),
    ("1.2.3", "Peralatan", "Aset Tetap", "Debit"),
    ("1.2.4", "Kendaraan", "Aset Tetap", "Debit"),
    ("1.2.5", "Inventaris", "Aset Tetap", "Debit"),
    ("1.2.6", "Aset Tetap Lainnya", "Aset Tetap", "Debit"),
    ("1.2.7", "Akumulasi Penyusutan", "Aset Tetap", "Kredit"),
    ("1.2.8", "Investasi Panjang", "Aset Tetap", "Debit"),
    ("1.2.9", "Aset Lain-lain", "Aset Tetap", "Debit"),

    # Kewajiban
    ("2.1.1", "Utang Usaha", "Kewajiban Pendek", "Kredit"),
    ("2.1.2", "Utang Gaji", "Kewajiban Pendek", "Kredit"),
    ("2.1.3", "Utang Pajak", "Kewajiban Pendek", "Kredit"),
    ("2.1.4", "Pendapatan Diterima Di Muka", "Kewajiban Pendek", "Kredit"),
    ("2.1.5", "Utang Lain-lain", "Kewajiban Pendek", "Kredit"),
    ("2.2.1", "Pinjaman Bank", "Kewajiban Panjang", "Kredit"),
    ("2.2.2", "Pinjaman Pemerintah", "Kewajiban Panjang", "Kredit"),
    ("2.2.3", "Utang Pihak Ketiga", "Kewajiban Panjang", "Kredit"),

    # Ekuitas
    ("3.1.1", "Modal Desa", "Ekuitas", "Kredit"),
    ("3.1.2", "Modal Pihak Ketiga", "Ekuitas", "Kredit"),
    ("3.1.3", "Saldo Laba Ditahan", "Ekuitas", "Kredit"),
    ("3.1.4", "Laba Tahun Berjalan", "Ekuitas", "Kredit"),
    ("3.1.5", "Cadangan Sosial / Investasi", "Ekuitas", "Kredit")
]
# Konversi ke DataFrame
daftar_akun = pd.DataFrame(daftar_akun_data, columns=["Kode Akun", "Nama Akun", "Posisi", "Tipe"])

# LEMBAR PENGESAHAN
st.markdown("""
    <br><br><br>
    <table width='100%' style='text-align:center;'>
        <tr><td><b>Disusun oleh</b></td><td><b>Disetujui oleh</b></td></tr>
        <tr><td><br><br><br></td><td><br><br><br></td></tr>
        <tr><td><u>{}</u><br>Bendahara</td><td><u>{}</u><br>Direktur/Pimpinan</td></tr>
        <tr><td colspan='2'><br><br></td></tr>
        <tr><td><b>Mengetahui</b></td><td><b>Mengetahui</b></td></tr>
        <tr><td><br><br><br></td><td><br><br><br></td></tr>
        <tr><td><u>{}</u><br>Kepala Desa</td><td><u>{}</u><br>Ketua BPD</td></tr>
    </table>
    <br><br>
""".format(bendahara, direktur, kepala_desa, ketua_bpd), unsafe_allow_html=True)

# Catatan: Laporan otomatis Laba Rugi, Neraca, Arus Kas akan dilanjutkan di bagian berikutnya
st.success("✅ Struktur akun lengkap dan lembar pengesahan otomatis berhasil dimuat. Siap lanjut ke Laba Rugi, Neraca, dan Arus Kas otomatis.")
