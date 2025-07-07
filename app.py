import streamlit as st
import pandas as pd
from io import BytesIO
import base64
import os

st.set_page_config(page_title="Laporan Keuangan Desa", layout="wide")

# ====== IDENTITAS & TANDA TANGAN ======
st.sidebar.title("🔰 Identitas Lembaga")
lembaga = st.sidebar.selectbox("Lembaga", ["BUMDes", "TPK", "LPMD", "Karang Taruna", "Posyandu", "TSBD", "Pokmas"])
desa = st.sidebar.text_input("Nama Desa", "Keling")
nama_bumdes = st.sidebar.text_input("Nama Lembaga", "Buwana Raharja")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

st.sidebar.subheader("🖊️ Pejabat Penandatangan")
bendahara = st.sidebar.text_input("Bendahara", "Siti Aminah")
direktur = st.sidebar.text_input("Direktur/Pimpinan", "Bambang Setiawan")
kepala_desa = st.sidebar.text_input("Kepala Desa", "Sugeng Riyadi")
ketua_bpd = st.sidebar.text_input("Ketua BPD", "Dwi Purnomo")

# ====== HEADER LAPORAN ======
st.markdown(f"""
<h3 style='text-align:center;'>Laporan Keuangan {lembaga} {nama_bumdes} Desa {desa}</h3>
<h4 style='text-align:center;'>Alamat: Jl. Raya Keling, Bukaan, Keling, Kec. Kepung, Kabupaten Kediri, Jawa Timur 64293</h4>
<hr>
""", unsafe_allow_html=True)

# ====== INISIALISASI JURNAL ======
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

# ====== DAFTAR AKUN (SESUAI SISKEUDES) ======
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

posisi = (
    ["Pendapatan"] * 7 + ["HPP"] * 6 + ["Beban Usaha"] * 11 + ["Non-Usaha"] * 6 +
    ["Aset Lancar"] * 8 + ["Aset Tetap"] * 9 + ["Kewajiban Pendek"] * 5 + ["Kewajiban Panjang"] * 3 + ["Ekuitas"] * 5
)

tipe = (
    ["Kredit"] * 7 + ["Debit"] * 6 + ["Debit"] * 11 + ["Kredit"] * 3 + ["Debit"] * 2 + ["Kredit"] * 1 +
    ["Debit"] * 5 + ["Debit"] * 9 + ["Kredit"] * 5 + ["Kredit"] * 3 + ["Kredit"] * 5
)

# Cek ulang total
assert len(kode_akun) == len(nama_akun) == len(posisi) == len(tipe), \
    f"Mismatch panjang list: kode={len(kode_akun)}, nama={len(nama_akun)}, posisi={len(posisi)}, tipe={len(tipe)}"

# Buat dataframe
daftar_akun = pd.DataFrame({
    "Kode Akun": kode_akun,
    "Nama Akun": nama_akun,
    "Posisi": posisi,
    "Tipe": tipe
})

# === PASTIKAN SAMA PANJANG ===
assert len(kode_akun) == len(nama_akun) == len(posisi) == len(tipe), "Jumlah elemen pada daftar akun tidak sama."

# === BENTUK DATAFRAME AKUN ===
daftar_akun = pd.DataFrame({
    "Kode Akun": kode_akun,
    "Nama Akun": nama_akun,
    "Posisi": posisi,
    "Tipe": tipe
})

with st.expander("📘 Daftar Akun Standar"):
    st.dataframe(daftar_akun, use_container_width=True)

# === NOTIFIKASI SIAP LANJUT ===
st.success("✅ Struktur akun siap dan tidak error. Silakan lanjut ke bagian Jurnal, Laba Rugi, Neraca & Arus Kas otomatis.")

