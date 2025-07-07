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

# === FORM INPUT TRANSAKSI ===
st.subheader("📝 Jurnal Harian")
with st.form("form_input"):
    col1, col2, col3 = st.columns(3)
    with col1:
        tanggal = st.date_input("Tanggal", value=datetime.today())
        debit = st.number_input("Jumlah Debit", 0.0, step=1000.0)
    with col2:
        kode_akun = st.selectbox("Kode Akun", options=[])  # Nanti diisi otomatis dari daftar_akun
        kredit = st.number_input("Jumlah Kredit", 0.0, step=1000.0)
    with col3:
        nama_akun = st.text_input("Nama Akun")
        keterangan = st.text_input("Keterangan")
        bukti = st.file_uploader("Upload Bukti", type=["jpg", "jpeg", "png", "pdf"])

    submit = st.form_submit_button("➕ Tambah Transaksi")
    if submit:
        df = st.session_state[key_gl]
        new_row = {
            "Tanggal": tanggal,
            "Kode Akun": kode_akun,
            "Nama Akun": nama_akun,
            "Debit": debit,
            "Kredit": kredit,
            "Keterangan": keterangan,
            "Bukti": bukti.name if bukti else ""
        }
        st.session_state[key_gl] = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("✅ Transaksi berhasil ditambahkan.")

# === TAMPILKAN TABEL JURNAL ===
st.write("### 📄 Data Transaksi")
st.dataframe(st.session_state[key_gl], use_container_width=True)

# === LAPORAN OTOMATIS ===
df_gl = st.session_state[key_gl]

# Fungsi akumulasi berdasarkan posisi
posisi_summary = df_gl.groupby("Nama Akun").agg({"Debit": "sum", "Kredit": "sum"}).reset_index()

# Laporan Laba Rugi
st.subheader("📊 Laporan Laba Rugi")
laba_rugi = posisi_summary[posisi_summary["Nama Akun"].str.contains("Pendapatan|Beban|HPP|Non|Pajak")]
st.dataframe(laba_rugi, use_container_width=True)

# Laporan Neraca
st.subheader("📊 Neraca (Laporan Posisi Keuangan)")
neraca = posisi_summary[posisi_summary["Nama Akun"].str.contains("Kas|Bank|Piutang|Persediaan|Aset|Utang|Modal")]
st.dataframe(neraca, use_container_width=True)

# Arus Kas (simpel)
st.subheader("📊 Laporan Arus Kas")
arus_kas = pd.DataFrame({
    "Arus Kas Masuk": [df_gl["Kredit"].sum()],
    "Arus Kas Keluar": [df_gl["Debit"].sum()],
    "Kenaikan Kas Bersih": [df_gl["Kredit"].sum() - df_gl["Debit"].sum()]
})
st.dataframe(arus_kas, use_container_width=True)

# === EKSPOR EXCEL DAN PDF ===
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

st.download_button("⬇️ Download Laba Rugi (CSV)", convert_df(laba_rugi), f"Laba_Rugi_{lembaga}_{tahun}.csv", "text/csv")
st.download_button("⬇️ Download Neraca (CSV)", convert_df(neraca), f"Neraca_{lembaga}_{tahun}.csv", "text/csv")
st.download_button("⬇️ Download Arus Kas (CSV)", convert_df(arus_kas), f"Arus_Kas_{lembaga}_{tahun}.csv", "text/csv")

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

st.success("✅ Laporan otomatis Laba Rugi, Neraca, dan Arus Kas berhasil ditampilkan.")
