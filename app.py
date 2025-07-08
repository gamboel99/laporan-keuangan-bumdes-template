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

# === PEDOMAN AKUN (MANUAL) ===
pedoman_data = {
    "Nama Akun": [
        "Penjualan Barang Dagang", "Pendapatan Jasa", "Pendapatan Sewa Aset", "Pendapatan Simpan Pinjam", "Pendapatan Usaha Tani", "Pendapatan Wisata", "Pendapatan Lainnya",
        "Pembelian Barang Dagang", "Beban Produksi", "Beban Pemeliharaan Usaha", "Beban Penyusutan Aset Usaha", "Bahan Baku / Operasional", "Beban Lainnya",
        "Gaji dan Tunjangan", "Listrik, Air, Komunikasi", "Transportasi", "Administrasi & Umum", "Sewa Tempat", "Perlengkapan", "Penyusutan Aset Tetap", "Penyuluhan", "Promosi & Publikasi", "Operasional Wisata", "CSR / Kegiatan Desa",
        "Pendapatan Bunga", "Pendapatan Investasi", "Pendapatan Lain-lain", "Beban Bunga", "Kerugian Penjualan Aset", "Pajak",
        "Kas", "Bank", "Piutang Usaha", "Persediaan Dagang", "Persediaan Bahan Baku", "Uang Muka", "Investasi Pendek", "Pendapatan Diterima Di Muka",
        "Tanah", "Bangunan", "Peralatan", "Kendaraan", "Inventaris", "Aset Tetap Lainnya", "Akumulasi Penyusutan", "Investasi Panjang", "Aset Lain-lain",
        "Utang Usaha", "Utang Gaji", "Utang Pajak", "Pendapatan Diterima Di Muka", "Utang Lain-lain",
        "Pinjaman Bank", "Pinjaman Pemerintah", "Utang Pihak Ketiga",
        "Modal Desa", "Modal Pihak Ketiga", "Saldo Laba Ditahan", "Laba Tahun Berjalan", "Cadangan Sosial / Investasi"
    ],
    "Posisi": [
        "Pendapatan"]*7 + ["HPP"]*6 + ["Beban Usaha"]*11 + ["Non-Usaha"]*6 + ["Aset Lancar"]*8 + ["Aset Tetap"]*9 + ["Kewajiban Pendek"]*5 + ["Kewajiban Panjang"]*3 + ["Ekuitas"]*5,
    "Tipe": ["Kredit"]*7 + ["Debit"]*6 + ["Debit"]*11 + ["Kredit"]*3 + ["Debit"]*8 + ["Debit"]*9 + ["Kredit"]*5 + ["Kredit"]*3 + ["Kredit"]*5
}

pedoman_akun = pd.DataFrame(pedoman_data)
with st.expander("📘 Pedoman Daftar Akun (Manual)"):
    st.dataframe(pedoman_akun, use_container_width=True)

# === TAB UNTUK LAPORAN ===
tab1, tab2, tab3, tab4 = st.tabs(["📒 Jurnal Harian", "📈 Laba Rugi", "📊 Neraca", "💸 Arus Kas"])

with tab1:
    st.write("Belum ada implementasi Jurnal Harian. Akan ditambahkan di bagian berikutnya.")

with tab2:
    st.write("Laporan Laba Rugi akan muncul otomatis setelah input transaksi dilakukan.")

with tab3:
    st.write("Laporan Neraca akan muncul otomatis setelah input transaksi dilakukan.")

with tab4:
    st.write("Laporan Arus Kas akan muncul otomatis setelah input transaksi dilakukan.")

# === LEMBAR PENGESAHAN ===
st.markdown(f"""
    <br><br><br>
    <table width='100%' style='text-align:center;'>
        <tr><td><b>Disusun oleh</b></td><td><b>Disetujui oleh</b></td></tr>
        <tr><td><br><br><br></td><td><br><br><br></td></tr>
        <tr><td><u>{bendahara}</u><br>Bendahara</td><td><u>{direktur}</u><br>Direktur/Pimpinan</td></tr>
        <tr><td colspan='2'><br><br></td></tr>
        <tr><td><b>Mengetahui</b></td><td><b>Mengetahui</b></td></tr>
        <tr><td><br><br><br></td><td><br><br><br></td></tr>
        <tr><td><u>{kepala_desa}</u><br>Kepala Desa</td><td><u>{ketua_bpd}</u><br>Ketua BPD</td></tr>
    </table>
    <br><br>
""", unsafe_allow_html=True)

st.success("✅ Struktur awal, tab laporan, dan pedoman akun berhasil dimuat. Siap lanjut input transaksi dan laporan otomatis.")
