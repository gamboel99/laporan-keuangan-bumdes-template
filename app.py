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

tipe = ["Kredit"]*7 + ["Debit"]*6 + ["Debit"]*11 + ["Kredit"]*3 + ["Debit"]*5 + ["Debit"]*9 + ["Kredit"]*5 + ["Kredit"]*3 + ["Kredit"]*5

assert len(kode_akun) == len(nama_akun) == len(posisi) == len(tipe), "Jumlah elemen pada daftar akun tidak sama."

daftar_akun = pd.DataFrame({
    "Kode Akun": kode_akun,
    "Nama Akun": nama_akun,
    "Posisi": posisi,
    "Tipe": tipe
})

with st.expander("📚 Daftar Akun Standar SISKEUDES"):
    st.dataframe(daftar_akun, use_container_width=True)

# === INPUT TRANSAKSI JURNAL HARIAN ===
st.subheader("🧾 Jurnal Harian (General Ledger)")
with st.form("form_gl", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        tanggal = st.date_input("Tanggal Transaksi", value=datetime.today())
    with col2:
        kode = st.selectbox("Kode Akun", daftar_akun["Kode Akun"])
    with col3:
        nama = daftar_akun[daftar_akun["Kode Akun"] == kode]["Nama Akun"].values[0]
    debit = st.number_input("Debit (Rp)", min_value=0.0, value=0.0, step=1000.0)
    kredit = st.number_input("Kredit (Rp)", min_value=0.0, value=0.0, step=1000.0)
    keterangan = st.text_input("Keterangan")
    bukti = st.file_uploader("Upload Bukti Transaksi (Opsional)", type=["jpg", "png", "pdf"])
    if st.form_submit_button("➕ Tambah Transaksi"):
        new_row = {
            "Tanggal": tanggal,
            "Kode Akun": kode,
            "Nama Akun": nama,
            "Debit": debit,
            "Kredit": kredit,
            "Keterangan": keterangan,
            "Bukti": bukti.name if bukti else ""
        }
        st.session_state[key_gl] = pd.concat([st.session_state[key_gl], pd.DataFrame([new_row])], ignore_index=True)
        if bukti:
            os.makedirs("bukti", exist_ok=True)
            with open(os.path.join("bukti", bukti.name), "wb") as f:
                f.write(bukti.getbuffer())
        st.experimental_rerun()

# === TAMPILKAN JURNAL HARIAN ===
st.dataframe(st.session_state[key_gl], use_container_width=True)

# === FITUR HAPUS TIAP BARIS ===
st.subheader("🗑️ Hapus Transaksi")
if not st.session_state[key_gl].empty:
    row_to_delete = st.number_input("Nomor Baris yang Ingin Dihapus (mulai dari 0)", min_value=0, max_value=len(st.session_state[key_gl])-1)
    if st.button("❌ Hapus Baris"):
        st.session_state[key_gl] = st.session_state[key_gl].drop(index=row_to_delete).reset_index(drop=True)
        st.experimental_rerun()

# === LEMBAR PENGESAHAN ===
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

st.success("✅ Struktur akun lengkap, input jurnal harian, dan lembar pengesahan berhasil dimuat. Siap lanjut ke laporan otomatis berikutnya.")
