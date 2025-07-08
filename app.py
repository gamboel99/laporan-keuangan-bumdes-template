import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Laporan Keuangan Lembaga Desa", layout="wide")

# === INISIALISASI ===
if "buku_besar" not in st.session_state:
    st.session_state.buku_besar = pd.DataFrame(columns=[
        "Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

# === DAFTAR AKUN ===
kode_akun = [
    "4.1.1", "4.1.2", "4.1.3", "4.1.4", "4.1.5", "4.1.6", "4.1.7",
    "5.1.1", "5.1.2", "5.1.3", "5.1.4", "5.1.5", "5.1.6",
    "5.2.1", "5.2.2", "5.2.3", "5.2.4", "5.2.5", "5.2.6", "5.2.7", "5.2.8", "5.2.9", "5.2.10", "5.2.11",
    "6.1", "6.2", "6.3", "6.4", "6.5", "6.6",
    "1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.5", "1.1.6", "1.1.7", "1.1.8",
    "1.2.1", "1.2.2", "1.2.3", "1.2.4", "1.2.5", "1.2.6", "1.2.7", "1.2.8", "1.2.9",
    "2.1.1", "2.1.2", "2.1.3", "2.1.4", "2.1.5",
    "2.2.1", "2.2.2", "2.2.3",
    "3.1.1", "3.1.2", "3.1.3", "3.1.4", "3.1.5"
]

nama_akun = [
    "Penjualan Barang Dagang", "Pendapatan Jasa", "Pendapatan Sewa Aset", "Pendapatan Simpan Pinjam", "Pendapatan Usaha Tani", "Pendapatan Wisata", "Pendapatan Lainnya",
    "Pembelian Barang Dagang", "Beban Produksi", "Beban Pemeliharaan Usaha", "Beban Penyusutan Aset Usaha", "Bahan Baku / Operasional", "Beban Lainnya",
    "Gaji dan Tunjangan", "Listrik, Air, Komunikasi", "Transportasi", "Administrasi & Umum", "Sewa Tempat", "Perlengkapan", "Penyusutan Aset Tetap", "Penyuluhan", "Promosi & Publikasi", "Operasional Wisata", "CSR / Kegiatan Desa",
    "Pendapatan Bunga", "Pendapatan Investasi", "Pendapatan Lain-lain", "Beban Bunga", "Kerugian Penjualan Aset", "Pajak",
    "Kas", "Bank", "Piutang Usaha", "Persediaan Dagang", "Persediaan Bahan Baku", "Uang Muka", "Investasi Pendek", "Pendapatan Diterima Di Muka",
    "Tanah", "Bangunan", "Peralatan", "Kendaraan", "Inventaris", "Aset Tetap Lainnya", "Akumulasi Penyusutan", "Investasi Panjang", "Aset Lain-lain",
    "Utang Usaha", "Utang Gaji", "Utang Pajak", "Pendapatan Diterima Di Muka", "Utang Lain-lain",
    "Pinjaman Bank", "Pinjaman Pemerintah", "Utang Pihak Ketiga",
    "Modal Desa", "Modal Pihak Ketiga", "Saldo Laba Ditahan", "Laba Tahun Berjalan", "Cadangan Sosial / Investasi"
]

posisi = [
    "Pendapatan"]*7 + ["HPP"]*6 + ["Beban Usaha"]*11 + ["Non-Usaha"]*6 + ["Aset Lancar"]*8 + ["Aset Tetap"]*9 + ["Kewajiban Pendek"]*5 + ["Kewajiban Panjang"]*3 + ["Ekuitas"]*5

tipe = ["Kredit"]*7 + ["Debit"]*6 + ["Debit"]*11 + ["Kredit"]*3 + ["Debit"]*8 + ["Debit"]*9 + ["Kredit"]*5 + ["Kredit"]*3 + ["Kredit"]*5

assert len(kode_akun) == len(nama_akun) == len(posisi) == len(tipe), "Jumlah elemen pada daftar akun tidak sama."

daftar_akun = pd.DataFrame({
    "Kode Akun": kode_akun,
    "Nama Akun": nama_akun,
    "Posisi": posisi,
    "Tipe": tipe
})

st.title("📌 Input Jurnal Harian")

with st.form("form_input_transaksi"):
    tanggal = st.date_input("Tanggal Transaksi", value=datetime.today())
    akun_nama = st.selectbox("Pilih Nama Akun", daftar_akun["Nama Akun"])
    akun_data = daftar_akun[daftar_akun["Nama Akun"] == akun_nama].iloc[0]
    akun_kode = akun_data["Kode Akun"]
    akun_tipe = akun_data["Tipe"]

    nominal = st.number_input(f"Nominal ({akun_tipe})", min_value=0.0)
    keterangan = st.text_input("Keterangan")
    bukti = st.file_uploader("Upload Bukti Transaksi", type=["jpg", "png", "pdf"])

    submitted = st.form_submit_button("Tambah Transaksi")
    if submitted:
        new_row = {
            "Tanggal": tanggal,
            "Kode Akun": akun_kode,
            "Nama Akun": akun_nama,
            "Debit": nominal if akun_tipe == "Debit" else 0,
            "Kredit": nominal if akun_tipe == "Kredit" else 0,
            "Keterangan": keterangan,
            "Bukti": bukti.name if bukti else ""
        }
        st.session_state.buku_besar = pd.concat([
            st.session_state.buku_besar,
            pd.DataFrame([new_row])
        ], ignore_index=True)
        st.success("✅ Transaksi berhasil ditambahkan!")

# === TAMPILKAN BUKU BESAR ===
st.subheader("📒 Buku Besar")
st.dataframe(st.session_state.buku_besar, use_container_width=True)

# === FITUR HAPUS PER TRANSAKSI ===
if not st.session_state.buku_besar.empty:
    st.subheader("🗑️ Hapus Transaksi")
    hapus_index = st.number_input("Masukkan nomor indeks transaksi yang ingin dihapus (mulai dari 0)", min_value=0, max_value=len(st.session_state.buku_besar)-1, step=1)
    if st.button("Hapus Transaksi"):
        st.session_state.buku_besar.drop(index=hapus_index, inplace=True)
        st.session_state.buku_besar.reset_index(drop=True, inplace=True)
        st.success("✅ Transaksi berhasil dihapus.")
