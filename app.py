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

# === INISIALISASI ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

# === DAFTAR AKUN STANDAR ===
from utils import daftar_akun

with st.expander("📚 Daftar Akun Standar SISKEUDES"):
    st.dataframe(daftar_akun, use_container_width=True)

# === FORM INPUT TRANSAKSI ===
st.markdown("### 🧾 Input Transaksi Jurnal Harian")

with st.form("form_input_transaksi", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        tanggal = st.date_input("Tanggal Transaksi", datetime.today())
    with col2:
        akun_opsi = st.selectbox("Pilih Nama Akun", daftar_akun["Nama Akun"])
        kode_akun_otomatis = daftar_akun[daftar_akun["Nama Akun"] == akun_opsi]["Kode Akun"].values[0]
    with col3:
        posisi_akun = daftar_akun[daftar_akun["Nama Akun"] == akun_opsi]["Tipe"].values[0]

    col4, col5 = st.columns(2)
    with col4:
        debit = st.number_input("Jumlah Debit", min_value=0.0, step=1000.0)
    with col5:
        kredit = st.number_input("Jumlah Kredit", min_value=0.0, step=1000.0)

    keterangan = st.text_input("Keterangan Transaksi")
    bukti = st.text_input("Nomor / Bukti Transaksi")

    submitted = st.form_submit_button("✅ Simpan Transaksi")
    if submitted:
        new_row = pd.DataFrame({
            "Tanggal": [tanggal],
            "Kode Akun": [kode_akun_otomatis],
            "Nama Akun": [akun_opsi],
            "Debit": [debit],
            "Kredit": [kredit],
            "Keterangan": [keterangan],
            "Bukti": [bukti]
        })
        st.session_state[key_gl] = pd.concat([st.session_state[key_gl], new_row], ignore_index=True)
        st.success("Transaksi berhasil disimpan ✅")

# === TAMPILKAN JURNAL ===
st.markdown("### 📋 Daftar Jurnal Harian")
df_gl = st.session_state[key_gl]

if not df_gl.empty:
    for idx, row in df_gl.iterrows():
        st.write(f"**{row['Tanggal']} | {row['Kode Akun']} - {row['Nama Akun']}**")
        st.write(f"📌 {row['Keterangan']} | Bukti: {row['Bukti']}")
        st.write(f"🟢 Debit: Rp {row['Debit']:,.0f} | 🔴 Kredit: Rp {row['Kredit']:,.0f}")
        if st.button(f"Hapus Baris {idx+1}", key=f"hapus_{idx}"):
            df_gl = df_gl.drop(index=idx).reset_index(drop=True)
            st.session_state[key_gl] = df_gl
            st.experimental_rerun()
        st.markdown("---")
else:
    st.warning("Belum ada transaksi yang diinput.")

# === LAPORAN LABA RUGI ===
st.markdown("## 📊 Laporan Laba Rugi")
laba_rugi = df_gl.merge(daftar_akun, on=["Kode Akun", "Nama Akun"], how="left")
pendapatan = laba_rugi[laba_rugi["Posisi"] == "Pendapatan"]["Kredit"].sum()
hpp = laba_rugi[laba_rugi["Posisi"] == "HPP"]["Debit"].sum()
beban = laba_rugi[laba_rugi["Posisi"] == "Beban Usaha"]["Debit"].sum()
nonusaha = laba_rugi[laba_rugi["Posisi"] == "Non-Usaha"]["Debit"].sum()

laba_bersih = pendapatan - hpp - beban - nonusaha

st.metric("Pendapatan", f"Rp {pendapatan:,.0f}")
st.metric("HPP", f"Rp {hpp:,.0f}")
st.metric("Beban Usaha", f"Rp {beban:,.0f}")
st.metric("Beban Non-Usaha", f"Rp {nonusaha:,.0f}")
st.metric("Laba Bersih", f"Rp {laba_bersih:,.0f}")

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

st.success("✅ Semua laporan otomatis berhasil ditampilkan.")
