# Laporan Keuangan Lembaga Desa vFinal
import streamlit as st
import pandas as pd
import base64
from datetime import datetime
from io import BytesIO
import os

st.set_page_config(page_title="Laporan Keuangan Lembaga Desa", layout="wide")

# === INPUT DASAR ===
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

# === HEADER LAPORAN ===
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

# === DAFTAR AKUN SESUAI SISKEUDES ===
daftar_akun_data = [
    # Format: (Kode Akun, Nama Akun, Posisi, Tipe)
    ("4.1.1", "Penjualan Barang Dagang", "Pendapatan", "Kredit"),
    ("5.1.1", "Pembelian Barang Dagang", "HPP", "Debit"),
    ("5.2.1", "Gaji dan Tunjangan", "Beban Usaha", "Debit"),
    ("6.1", "Pendapatan Bunga", "Non-Usaha", "Kredit"),
    ("6.4", "Beban Bunga", "Non-Usaha", "Debit"),
    ("1.1.1", "Kas", "Aset Lancar", "Debit"),
    ("2.1.1", "Utang Usaha", "Kewajiban Pendek", "Kredit"),
    ("3.1.1", "Modal Desa", "Ekuitas", "Kredit"),
    ("3.1.4", "Laba Tahun Berjalan", "Ekuitas", "Kredit")
]
daftar_akun = pd.DataFrame(daftar_akun_data, columns=["Kode Akun", "Nama Akun", "Posisi", "Tipe"])

# === INISIALISASI GENERAL LEDGER ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan"])

df_gl = st.session_state[key_gl]

# === INPUT TRANSAKSI ===
st.subheader("📝 Input Transaksi Buku Besar")
with st.form("form_gl"):
    col1, col2, col3 = st.columns(3)
    with col1:
        tanggal = st.date_input("Tanggal")
        kode = st.selectbox("Kode Akun", daftar_akun["Kode Akun"])
    with col2:
        nama_akun = daftar_akun.set_index("Kode Akun").loc[kode]["Nama Akun"]
        debit = st.number_input("Debit", value=0.0)
    with col3:
        kredit = st.number_input("Kredit", value=0.0)
        keterangan = st.text_input("Keterangan")
    submitted = st.form_submit_button("Tambah")
    if submitted:
        new_data = pd.DataFrame([[tanggal, kode, nama_akun, debit, kredit, keterangan]], columns=df_gl.columns)
        st.session_state[key_gl] = pd.concat([df_gl, new_data], ignore_index=True)
        st.experimental_rerun()

# === TABEL BUKU BESAR ===
st.subheader("📘 Buku Besar")
st.dataframe(st.session_state[key_gl], use_container_width=True)

# === LAPORAN OTOMATIS ===
if not df_gl.empty:
    df_gl = df_gl.merge(daftar_akun, on="Kode Akun", how="left")

    st.subheader("📊 Laporan Laba Rugi")
    laba_rugi = df_gl[df_gl["Posisi"].isin(["Pendapatan", "HPP", "Beban Usaha", "Non-Usaha"])]
    grouped_lr = laba_rugi.groupby(["Posisi", "Nama Akun"]).sum(numeric_only=True)[["Debit", "Kredit"]]
    st.dataframe(grouped_lr)

    total_pendapatan = df_gl[df_gl["Posisi"] == "Pendapatan"]["Kredit"].sum()
    total_hpp = df_gl[df_gl["Posisi"] == "HPP"]["Debit"].sum()
    total_beban = df_gl[df_gl["Posisi"] == "Beban Usaha"]["Debit"].sum()
    total_nonusaha = df_gl[df_gl["Posisi"] == "Non-Usaha"]["Kredit"].sum() - df_gl[df_gl["Posisi"] == "Non-Usaha"]["Debit"].sum()
    laba_bersih = total_pendapatan - total_hpp - total_beban + total_nonusaha

    st.metric("Laba Tahun Berjalan", f"Rp {laba_bersih:,.0f}")

    st.subheader("📗 Neraca")
    neraca = df_gl[df_gl["Posisi"].isin(["Aset Lancar", "Aset Tetap", "Kewajiban Pendek", "Kewajiban Panjang", "Ekuitas"])]
    grouped_nrc = neraca.groupby(["Posisi", "Nama Akun"]).sum(numeric_only=True)[["Debit", "Kredit"]]
    st.dataframe(grouped_nrc)

    st.subheader("📙 Arus Kas")
    kas_masuk = df_gl["Debit"].sum()
    kas_keluar = df_gl["Kredit"].sum()
    saldo_kas = kas_masuk - kas_keluar
    st.metric("Saldo Kas", f"Rp {saldo_kas:,.0f}")

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
""", unsafe_allow_html=True)

# === EKSPOR EXCEL ===
def convert_df(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Buku Besar')
    processed_data = output.getvalue()
    return processed_data

if not df_gl.empty:
    st.download_button("⬇️ Download Buku Besar (Excel)", data=convert_df(df_gl), file_name=f"Buku_Besar_{lembaga}_{desa}_{tahun}.xlsx")
