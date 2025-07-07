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

df_gl = st.session_state[key_gl]

# === DAFTAR AKUN STANDAR SISKEUDES ===
kode_akun = [...]
nama_akun = [...]
posisi = [...]
tipe = [...]

assert len(kode_akun) == len(nama_akun) == len(posisi) == len(tipe), "Jumlah elemen pada daftar akun tidak sama."

daftar_akun = pd.DataFrame({
    "Kode Akun": kode_akun,
    "Nama Akun": nama_akun,
    "Posisi": posisi,
    "Tipe": tipe
})

with st.expander("📚 Daftar Akun Standar SISKEUDES"):
    st.dataframe(daftar_akun, use_container_width=True)

# === LAPORAN LABA RUGI ===
st.subheader("📑 Laporan Laba Rugi")
df_laba_rugi = df_gl.merge(daftar_akun, on=["Kode Akun", "Nama Akun"], how="left")

pendapatan = df_laba_rugi[df_laba_rugi["Posisi"] == "Pendapatan"]["Kredit"].sum()
hpp = df_laba_rugi[df_laba_rugi["Posisi"] == "HPP"]["Debit"].sum()
beban_usaha = df_laba_rugi[df_laba_rugi["Posisi"] == "Beban Usaha"]["Debit"].sum()
penghasilan_lain = df_laba_rugi[df_laba_rugi["Posisi"] == "Non-Usaha"]["Kredit"].sum()
beban_lain = df_laba_rugi[df_laba_rugi["Posisi"] == "Non-Usaha"]["Debit"].sum()

laba_kotor = pendapatan - hpp
laba_operasional = laba_kotor - beban_usaha
laba_bersih = laba_operasional + penghasilan_lain - beban_lain

laporan_lr = pd.DataFrame({
    "Keterangan": ["Pendapatan", "HPP", "Laba Kotor", "Beban Usaha", "Laba Operasional", "Pendapatan/Beban Lainnya", "Laba Bersih"],
    "Jumlah": [pendapatan, hpp, laba_kotor, beban_usaha, laba_operasional, penghasilan_lain - beban_lain, laba_bersih]
})
st.dataframe(laporan_lr, use_container_width=True)

# === LAPORAN NERACA ===
st.subheader("📘 Laporan Neraca")
aset = df_laba_rugi[df_laba_rugi["Posisi"].str.contains("Aset")]
kewajiban = df_laba_rugi[df_laba_rugi["Posisi"].str.contains("Kewajiban")]
ekuitas = df_laba_rugi[df_laba_rugi["Posisi"] == "Ekuitas"]

aset_total = aset["Debit"].sum() - aset["Kredit"].sum()
kewajiban_total = kewajiban["Kredit"].sum() - kewajiban["Debit"].sum()
ekuitas_total = ekuitas["Kredit"].sum() - ekuitas["Debit"].sum()

eraca = pd.DataFrame({
    "Keterangan": ["Aset", "Kewajiban", "Ekuitas"],
    "Jumlah": [aset_total, kewajiban_total, ekuitas_total]
})
st.dataframe(eraca, use_container_width=True)

# === LAPORAN ARUS KAS ===
st.subheader("💰 Laporan Arus Kas (Langsung)")
kas = df_gl[df_gl["Nama Akun"].isin(["Kas", "Bank"])]
kas_masuk = kas["Debit"].sum()
kas_keluar = kas["Kredit"].sum()

arus_kas = pd.DataFrame({
    "Keterangan": ["Penerimaan Kas", "Pengeluaran Kas", "Saldo Kas Akhir"],
    "Jumlah": [kas_masuk, kas_keluar, kas_masuk - kas_keluar]
})
st.dataframe(arus_kas, use_container_width=True)

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

st.success("✅ Laporan Laba Rugi, Neraca, dan Arus Kas berhasil ditampilkan.")
