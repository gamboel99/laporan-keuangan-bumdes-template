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

# === INISIALISASI DATAFRAME ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

# === JURNAL UMUM ===
st.header("📑 Jurnal Umum")
st.caption("Input transaksi harian secara manual")
df_gl = st.session_state[key_gl]

with st.form("form_jurnal"):
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        tanggal = st.date_input("Tanggal")
        kode = st.text_input("Kode Akun")
    with col2:
        nama = st.text_input("Nama Akun")
        debit = st.number_input("Debit", value=0.0, step=1000.0)
    with col3:
        kredit = st.number_input("Kredit", value=0.0, step=1000.0)
        keterangan = st.text_input("Keterangan")
        bukti = st.file_uploader("Bukti Transaksi", type=["jpg", "jpeg", "png", "pdf"], label_visibility="collapsed")

    submitted = st.form_submit_button("➕ Tambah Transaksi")
    if submitted:
        st.session_state[key_gl] = pd.concat([st.session_state[key_gl], pd.DataFrame.from_records([{
            "Tanggal": tanggal,
            "Kode Akun": kode,
            "Nama Akun": nama,
            "Debit": debit,
            "Kredit": kredit,
            "Keterangan": keterangan,
            "Bukti": bukti.name if bukti else ""
        }])], ignore_index=True)
        st.success("✅ Transaksi berhasil ditambahkan")
        st.experimental_rerun()

st.dataframe(df_gl, use_container_width=True)

# === DOWNLOAD GENERAL LEDGER ===
def download_excel(df, filename):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='General Ledger')
    processed_data = output.getvalue()
    b64 = base64.b64encode(processed_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📥 Download General Ledger Excel</a>'
    return href

st.markdown(download_excel(df_gl, f"General_Ledger_{lembaga}_{desa}_{tahun}.xlsx"), unsafe_allow_html=True)

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

st.success("✅ General Ledger dan Lembar Pengesahan berhasil dimuat. Lanjutkan ke laporan otomatis di bawah ini.")
