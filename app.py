import streamlit as st
import pandas as pd
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

# === DAFTAR AKUN ===
daftar_akun = pd.DataFrame({
    "Kode Akun": ["5.2.1", "4.1.1", "1.1.1"],
    "Nama Akun": ["Gaji dan Tunjangan", "Penjualan Barang Dagang", "Kas"],
    "Posisi": ["Debit", "Kredit", "Debit"],
})

# === INISIALISASI ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan"])

# === FORM INPUT ===
st.subheader("Tambah Transaksi Jurnal Harian")
with st.form("form_input"):
    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal Transaksi", datetime.today())
        akun_opsi = st.selectbox("Pilih Nama Akun", daftar_akun["Nama Akun"])
    with col2:
        keterangan = st.text_input("Keterangan")
        jumlah = st.number_input("Jumlah", 0.0, step=1000.0)

    akun_row = daftar_akun[daftar_akun["Nama Akun"] == akun_opsi].iloc[0]
    kode_akun = akun_row["Kode Akun"]
    posisi = akun_row["Posisi"]

    submitted = st.form_submit_button("Tambah Transaksi")
    if submitted:
        debit = jumlah if posisi == "Debit" else 0.0
        kredit = jumlah if posisi == "Kredit" else 0.0
        new_row = pd.DataFrame([[tanggal, kode_akun, akun_opsi, debit, kredit, keterangan]],
                                columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan"])
        st.session_state[key_gl] = pd.concat([st.session_state[key_gl], new_row], ignore_index=True)
        st.success("✅ Transaksi berhasil ditambahkan.")

# === TABEL JURNAL ===
st.subheader("📑 Jurnal Harian / Buku Besar")
df_gl = st.session_state[key_gl]
st.dataframe(df_gl, use_container_width=True)

# === LAPORAN LABA RUGI ===
st.subheader("📊 Laporan Laba Rugi")
pendapatan = df_gl[df_gl["Nama Akun"].str.contains("Penjualan")]["Kredit"].sum()
beban = df_gl[df_gl["Nama Akun"].str.contains("Gaji")]["Debit"].sum()
laba_bersih = pendapatan - beban

laporan_lr = pd.DataFrame({
    "Pos": ["Pendapatan", "Beban", "Laba Bersih"],
    "Jumlah": [pendapatan, beban, laba_bersih]
})
st.table(laporan_lr)

# === LAPORAN NERACA ===
st.subheader("📈 Laporan Neraca")
kekayaan = df_gl[df_gl["Nama Akun"] == "Kas"]["Debit"].sum()
ekuitas = laba_bersih
laporan_neraca = pd.DataFrame({
    "Pos": ["Aset (Kas)", "Ekuitas (Laba Ditahan)"],
    "Jumlah": [kekayaan, ekuitas]
})
st.table(laporan_neraca)

# === LAPORAN ARUS KAS ===
st.subheader("💸 Laporan Arus Kas")
arus_kas = pd.DataFrame({
    "Jenis Arus": ["Arus Kas dari Operasi"],
    "Jumlah": [kekayaan]
})
st.table(arus_kas)
