import streamlit as st
import pandas as pd
from datetime import datetime
import os
from io import BytesIO

st.set_page_config(page_title="Laporan Keuangan Lembaga Desa", layout="wide")

# === IDENTITAS DESA DAN PEJABAT ===
st.sidebar.title("🔰 Pilih Unit Lembaga")
lembaga = st.sidebar.selectbox("Lembaga", ["BUMDes", "TPK", "LPMD", "Karang Taruna", "Posyandu", "TSBD", "Pokmas"])
desa = st.sidebar.text_input("Nama Desa", "Keling")
nama_bumdes = st.sidebar.text_input("Nama Lembaga", "Buwana Raharja")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

st.sidebar.markdown("---")
st.sidebar.subheader("Pejabat Tanda Tangan")
bendahara = st.sidebar.text_input("Nama Bendahara", "Siti Aminah")
direktur = st.sidebar.text_input("Nama Ketua/Pimpinan", "Bambang Setiawan")
kepala_desa = st.sidebar.text_input("Nama Kepala Desa", "Sugeng Riyadi")
ketua_bpd = st.sidebar.text_input("Nama Ketua BPD", "Dwi Purnomo")

# === JUDUL DAN KOP ===
st.markdown(f"""
    <h3 style='text-align:center;'>Laporan Keuangan {lembaga} {nama_bumdes} Desa {desa}</h3>
    <h4 style='text-align:center;'>Alamat: Jl. Raya Keling, Bukaan, Keling, Kec. Kepung, Kabupaten Kediri, Jawa Timur 64293</h4>
    <hr>
""", unsafe_allow_html=True)

# === PANDUAN AKUN MANUAL ===
st.subheader("📘 Pedoman Daftar Akun dan Posisi")
pedoman_akun = pd.DataFrame({
    "Kode Akun": ["4.1.1", "4.1.2", "5.1.1", "5.2.1", "6.1", "1.1.1", "2.1.1", "3.1.1"],
    "Nama Akun": ["Penjualan Dagang", "Pendapatan Jasa", "Pembelian Barang", "Gaji & Tunjangan", "Pendapatan Bunga", "Kas", "Utang Usaha", "Modal Desa"],
    "Posisi": ["Pendapatan", "Pendapatan", "HPP", "Beban Usaha", "Non-Usaha", "Aset Lancar", "Kewajiban Pendek", "Ekuitas"],
    "Tipe (Default)": ["Kredit", "Kredit", "Debit", "Debit", "Kredit", "Debit", "Kredit", "Kredit"]
})
st.dataframe(pedoman_akun, use_container_width=True)

# === GENERAL LEDGER / JURNAL HARIAN ===
st.subheader("📒 Input Transaksi Jurnal Harian")
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Posisi", "Debit", "Kredit", "Keterangan", "Bukti"])

df_gl = st.session_state[key_gl]

with st.form("input_jurnal"):
    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal", value=datetime.today())
        kode_akun = st.text_input("Kode Akun (lihat pedoman di atas)")
        akun_nama = st.text_input("Nama Akun")
        posisi = st.selectbox("Posisi", ["Pendapatan", "HPP", "Beban Usaha", "Non-Usaha", "Aset Lancar", "Aset Tetap", "Kewajiban Pendek", "Kewajiban Panjang", "Ekuitas"])
    with col2:
        nominal = st.number_input("Nominal", 0.0, step=1000.0)
        keterangan = st.text_input("Keterangan")
        bukti = st.file_uploader("Upload Bukti Transaksi (opsional)", type=["jpg", "jpeg", "png", "pdf"])

    submitted = st.form_submit_button("+ Tambah Transaksi")
    if submitted:
        debit, kredit = (nominal, 0.0) if posisi in ["HPP", "Beban Usaha", "Aset Lancar", "Aset Tetap"] else (0.0, nominal)
        new_row = pd.DataFrame([[tanggal, kode_akun, akun_nama, posisi, debit, kredit, keterangan, bukti.name if bukti else ""]],
                               columns=df_gl.columns)
        st.session_state[key_gl] = pd.concat([df_gl, new_row], ignore_index=True)
        st.success("✅ Transaksi berhasil ditambahkan.")

# === TABEL BUKU BESAR ===
st.subheader("📊 Buku Besar / Jurnal Harian")
df_gl = st.session_state[key_gl]
if not df_gl.empty:
    for i in df_gl.index:
        col1, col2, col3 = st.columns([10, 1, 1])
        with col2:
            if st.button("🗑️", key=f"hapus_{i}"):
                st.session_state[key_gl] = df_gl.drop(index=i).reset_index(drop=True)
                st.experimental_rerun()
    st.dataframe(df_gl.style.set_table_attributes('class="table table-bordered"'), use_container_width=True)
else:
    st.info("Belum ada transaksi yang dimasukkan.")

# === LANJUTKAN KE: Laba Rugi, Neraca, dan Arus Kas Otomatis ===
st.success("✅ Jurnal Harian siap. Klik lanjut untuk melihat laporan otomatis.")
