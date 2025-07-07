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

# === INPUT TRANSAKSI ===
st.subheader("🧾 Input Transaksi Jurnal Harian")
with st.form("input_transaksi"):
    tgl = st.date_input("Tanggal")
    akun_opsi = st.selectbox("Pilih Nama Akun", daftar_akun["Nama Akun"])
    kode_akun = daftar_akun[daftar_akun["Nama Akun"] == akun_opsi]["Kode Akun"].values[0]
    debit = st.number_input("Debit", 0.0)
    kredit = st.number_input("Kredit", 0.0)
    ket = st.text_input("Keterangan")
    bukti = st.text_input("No. Bukti / Upload")
    submit = st.form_submit_button("+ Tambah Transaksi")

if submit:
    new_row = pd.DataFrame([[tgl, kode_akun, akun_opsi, debit, kredit, ket, bukti]], columns=st.session_state[key_gl].columns)
    st.session_state[key_gl] = pd.concat([st.session_state[key_gl], new_row], ignore_index=True)
    st.success("✅ Transaksi berhasil ditambahkan!")
    st.experimental_rerun()

# === TABEL TRANSAKSI ===
st.subheader("📑 Daftar Transaksi")
if not st.session_state[key_gl].empty:
    edited_df = st.session_state[key_gl].copy()
    for i in range(len(edited_df)):
        col1, col2 = st.columns([9, 1])
        with col1:
            st.write(f"{i+1}. {edited_df.iloc[i].to_dict()}")
        with col2:
            if st.button("🗑️", key=f"hapus_{i}"):
                st.session_state[key_gl] = edited_df.drop(index=i).reset_index(drop=True)
                st.experimental_rerun()
else:
    st.info("Belum ada transaksi dimasukkan.")

# === DAFTAR AKUN ===
with st.expander("📚 Daftar Akun Standar SISKEUDES"):
    st.dataframe(daftar_akun, use_container_width=True)

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

st.success("✅ Fitur input transaksi, kode akun otomatis, dan hapus transaksi telah berhasil ditambahkan.")
