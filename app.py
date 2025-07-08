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
st.subheader("✍️ Input Transaksi Baru")
with st.form("form_transaksi", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal Transaksi", value=datetime.now())
        akun_nama = st.selectbox("Pilih Nama Akun", daftar_akun["Nama Akun"])
        kode_akun = daftar_akun[daftar_akun["Nama Akun"] == akun_nama]["Kode Akun"].values[0]
        posisi = daftar_akun[daftar_akun["Nama Akun"] == akun_nama]["Tipe"].values[0]
    with col2:
        jumlah = st.number_input("Jumlah (Rp)", min_value=0.0, step=1000.0)
        keterangan = st.text_input("Keterangan")
        bukti = st.file_uploader("Upload Bukti Transaksi (Opsional)", type=["jpg", "jpeg", "png", "pdf"])

    submitted = st.form_submit_button("➕ Tambah Transaksi")
    if submitted:
        debit = jumlah if posisi == "Debit" else 0.0
        kredit = jumlah if posisi == "Kredit" else 0.0
        new_row = {
            "Tanggal": tanggal,
            "Kode Akun": kode_akun,
            "Nama Akun": akun_nama,
            "Debit": debit,
            "Kredit": kredit,
            "Keterangan": keterangan,
            "Bukti": bukti.name if bukti else ""
        }
        st.session_state[key_gl] = pd.concat([st.session_state[key_gl], pd.DataFrame([new_row])], ignore_index=True)
        st.success("Transaksi berhasil ditambahkan.")

# === TAMPILKAN TABEL BUKU BESAR ===
st.subheader("📑 Buku Besar")
df_gl = st.session_state[key_gl]
st.dataframe(df_gl, use_container_width=True)

# === FITUR HAPUS TRANSAKSI ===
st.subheader("🗑️ Hapus Transaksi")
if not df_gl.empty:
    hapus_index = st.number_input("Masukkan Nomor Index Transaksi yang akan dihapus:", min_value=0, max_value=len(df_gl)-1, step=1)
    if st.button("Hapus Transaksi"):
        st.session_state[key_gl] = df_gl.drop(hapus_index).reset_index(drop=True)
        st.success("Transaksi berhasil dihapus.")
else:
    st.info("Belum ada transaksi yang ditambahkan.")

# === DOWNLOAD EXCEL ===
st.download_button("⬇️ Download Buku Besar (Excel)", data=df_gl.to_csv(index=False).encode(), file_name="buku_besar.csv", mime="text/csv")

# === PERHITUNGAN LABA RUGI OTOMATIS ===
st.subheader("📊 Laporan Laba Rugi Otomatis")
pd_laba = df_gl[df_gl["Nama Akun"].isin(daftar_akun[daftar_akun["Posisi"] == "Pendapatan"]["Nama Akun"])]
pd_beban = df_gl[df_gl["Nama Akun"].isin(daftar_akun[daftar_akun["Posisi"].isin(["Beban Usaha", "HPP", "Non-Usaha"])]["Nama Akun"])]


total_pendapatan = pd_laba["Kredit"].sum()
total_beban = pd_beban["Debit"].sum()
laba_bersih = total_pendapatan - total_beban

laporan_lr = pd.DataFrame({
    "Keterangan": ["Total Pendapatan", "Total Beban", "Laba Bersih"],
    "Jumlah (Rp)": [total_pendapatan, total_beban, laba_bersih]
})
st.dataframe(laporan_lr, use_container_width=True)

# === NERACA OTOMATIS ===
st.subheader("📘 Neraca Otomatis")
aset = df_gl[df_gl["Nama Akun"].isin(daftar_akun[daftar_akun["Posisi"].str.contains("Aset")]["Nama Akun"])]
kewajiban = df_gl[df_gl["Nama Akun"].isin(daftar_akun[daftar_akun["Posisi"].str.contains("Kewajiban")]["Nama Akun"])]
ekuitas = df_gl[df_gl["Nama Akun"].isin(daftar_akun[daftar_akun["Posisi"] == "Ekuitas"]["Nama Akun"])]

total_aset = aset["Debit"].sum()
total_kewajiban = kewajiban["Kredit"].sum()
total_ekuitas = ekuitas["Kredit"].sum()

laporan_neraca = pd.DataFrame({
    "Posisi": ["Total Aset", "Total Kewajiban", "Total Ekuitas"],
    "Jumlah (Rp)": [total_aset, total_kewajiban, total_ekuitas]
})
st.dataframe(laporan_neraca, use_container_width=True)

# === ARUS KAS OTOMATIS ===
st.subheader("💰 Arus Kas Otomatis")
kategori_kas = ["Kas", "Bank"]
kas_masuk = df_gl[(df_gl["Nama Akun"].isin(kategori_kas)) & (df_gl["Debit"] > 0)]["Debit"].sum()
kas_keluar = df_gl[(df_gl["Nama Akun"].isin(kategori_kas)) & (df_gl["Kredit"] > 0)]["Kredit"].sum()
saldo_kas = kas_masuk - kas_keluar

laporan_kas = pd.DataFrame({
    "Jenis": ["Kas Masuk", "Kas Keluar", "Saldo Kas Akhir"],
    "Jumlah (Rp)": [kas_masuk, kas_keluar, saldo_kas]
})
st.dataframe(laporan_kas, use_container_width=True)

# === PENGESAHAN ===
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

st.success("✅ Semua laporan otomatis berhasil dimuat.")
