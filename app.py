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

# === DATA SESSION GENERAL LEDGER ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

# === INPUT JURNAL HARIAN ===
st.subheader("📒 Input Jurnal Harian (Buku Besar)")
with st.form("form_jurnal"):
    col1, col2, col3 = st.columns(3)
    with col1:
        tgl = st.date_input("Tanggal", value=datetime.today())
    with col2:
        kode = st.text_input("Kode Akun")
    with col3:
        nama = st.text_input("Nama Akun")
    debit = st.number_input("Debit", min_value=0.0, step=1000.0)
    kredit = st.number_input("Kredit", min_value=0.0, step=1000.0)
    ket = st.text_input("Keterangan")
    uploaded_bukti = st.file_uploader("Upload Bukti Transaksi")
    submitted = st.form_submit_button("+ Tambah Transaksi")

    if submitted:
        new_row = {"Tanggal": tgl, "Kode Akun": kode, "Nama Akun": nama, "Debit": debit, "Kredit": kredit, "Keterangan": ket, "Bukti": uploaded_bukti.name if uploaded_bukti else ""}
        st.session_state[key_gl] = pd.concat([st.session_state[key_gl], pd.DataFrame([new_row])], ignore_index=True)
        st.success("✅ Transaksi berhasil ditambahkan")

# === TAMPILKAN JURNAL ===
st.write("### 📂 Buku Besar Tahun", tahun)
st.dataframe(st.session_state[key_gl], use_container_width=True)

# === LAPORAN LABA RUGI ===
st.header("📊 Laporan Laba Rugi Otomatis")
df = st.session_state[key_gl]
df["Debit"] = pd.to_numeric(df["Debit"], errors='coerce').fillna(0)
df["Kredit"] = pd.to_numeric(df["Kredit"], errors='coerce').fillna(0)

pendapatan = df[df["Kode Akun"].str.startswith("4")]["Kredit"].sum()
hpp = df[df["Kode Akun"].str.startswith("5.1")]["Debit"].sum()
beban_usaha = df[df["Kode Akun"].str.startswith("5.2")]["Debit"].sum()
non_usaha = df[df["Kode Akun"].str.startswith("6")]
pdpt_nonusaha = non_usaha["Kredit"].sum()
bbn_nonusaha = non_usaha["Debit"].sum()

laba_kotor = pendapatan - hpp
laba_usaha = laba_kotor - beban_usaha
laba_bersih_sebelum_pajak = laba_usaha + pdpt_nonusaha - bbn_nonusaha

st.metric("Pendapatan Usaha", f"Rp {pendapatan:,.0f}")
st.metric("HPP", f"Rp {hpp:,.0f}")
st.metric("Laba Kotor", f"Rp {laba_kotor:,.0f}")
st.metric("Beban Usaha", f"Rp {beban_usaha:,.0f}")
st.metric("Laba Usaha", f"Rp {laba_usaha:,.0f}")
st.metric("Laba Sebelum Pajak", f"Rp {laba_bersih_sebelum_pajak:,.0f}")

# === LAPORAN NERACA ===
st.header("📒 Neraca Otomatis")
aset = df[df["Kode Akun"].str.startswith("1")]["Debit"].sum()
kewajiban = df[df["Kode Akun"].str.startswith("2")]["Kredit"].sum()
ekuitas = df[df["Kode Akun"].str.startswith("3")]["Kredit"].sum()

st.metric("Total Aset", f"Rp {aset:,.0f}")
st.metric("Total Kewajiban", f"Rp {kewajiban:,.0f}")
st.metric("Total Ekuitas", f"Rp {ekuitas:,.0f}")

# === ARUS KAS SEDERHANA ===
st.header("💰 Laporan Arus Kas Otomatis")
kas_awal = 0
kas_masuk = df["Kredit"].sum()
kas_keluar = df["Debit"].sum()
kas_akhir = kas_awal + kas_masuk - kas_keluar

st.metric("Kas Masuk", f"Rp {kas_masuk:,.0f}")
st.metric("Kas Keluar", f"Rp {kas_keluar:,.0f}")
st.metric("Saldo Kas Akhir", f"Rp {kas_akhir:,.0f}")

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

st.success("✅ Laporan Laba Rugi, Neraca, dan Arus Kas berhasil dihitung secara otomatis.")
