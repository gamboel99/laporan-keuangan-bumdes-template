import streamlit as st
import pandas as pd
from datetime import datetime
import base64
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

# === PEDOMAN DAFTAR AKUN ===
pedoman_akun = pd.DataFrame({
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
    "Tipe": [
        "Kredit"]*7 + ["Debit"]*6 + ["Debit"]*11 + ["Kredit"]*3 + ["Debit"]*8 + ["Debit"]*9 + ["Kredit"]*5 + ["Kredit"]*3 + ["Kredit"]*5
})

with st.expander("📚 Pedoman Daftar Akun dan Posisi"): 
    st.dataframe(pedoman_akun, use_container_width=True)

# === INISIALISASI ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

df_gl = st.session_state[key_gl]

# === FORM INPUT JURNAL ===
st.subheader("📥 Input Transaksi Jurnal Harian")
with st.form("form_jurnal"):
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        tanggal = st.date_input("Tanggal", value=datetime.now())
    with col2:
        akun_nama = st.selectbox("Pilih Nama Akun", pedoman_akun["Nama Akun"])
        akun_info = pedoman_akun[pedoman_akun["Nama Akun"] == akun_nama].iloc[0]
    with col3:
        jumlah = st.number_input("Jumlah Transaksi", min_value=0.0, step=1000.0)

    keterangan = st.text_input("Keterangan")
    bukti = st.file_uploader("Upload Bukti Transaksi", type=["jpg", "png", "pdf"])

    submitted = st.form_submit_button("Simpan Transaksi")
    if submitted:
        debit, kredit = (jumlah, 0.0) if akun_info["Tipe"] == "Debit" else (0.0, jumlah)
        new_row = {
            "Tanggal": tanggal,
            "Nama Akun": akun_nama,
            "Debit": debit,
            "Kredit": kredit,
            "Keterangan": keterangan,
            "Bukti": bukti.name if bukti else "-"
        }
        df_gl = pd.concat([df_gl, pd.DataFrame([new_row])], ignore_index=True)
        st.session_state[key_gl] = df_gl
        st.success("Transaksi berhasil disimpan.")

# === TABEL GENERAL LEDGER ===
st.subheader("📒 Jurnal Harian / Buku Besar")
if not df_gl.empty:
    for i in range(len(df_gl)):
        col1, col2 = st.columns([10, 1])
        with col1:
            st.write(df_gl.iloc[i:i+1].style.set_table_attributes('style="border:1px solid gray;width:100%"').set_properties(**{'text-align': 'left'}))
        with col2:
            if st.button("🗑️ Hapus", key=f"hapus_{i}"):
                df_gl = df_gl.drop(i).reset_index(drop=True)
                st.session_state[key_gl] = df_gl
                st.experimental_rerun()
else:
    st.info("Belum ada transaksi.")

# Catatan: Laporan Laba Rugi, Neraca, Arus Kas akan ditambahkan selanjutnya
