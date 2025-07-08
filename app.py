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

# === INISIALISASI JURNAL HARIAN ===
st.title(f"📘 Buku Besar / Jurnal Harian ({lembaga})")

key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

# === INPUT TRANSAKSI ===
st.subheader("➕ Tambah Transaksi Baru")
with st.form("form_transaksi"):
    tanggal = st.date_input("Tanggal Transaksi", value=datetime.now())
    akun_nama = st.selectbox("Pilih Nama Akun", daftar_akun["Nama Akun"])
    akun_row = daftar_akun[daftar_akun["Nama Akun"] == akun_nama].iloc[0]
    kode_akun = akun_row["Kode Akun"]
    tipe_akun = akun_row["Tipe"]
    nominal = st.number_input("Jumlah (Rp)", min_value=0.0, step=1000.0, format="%.2f")
    keterangan = st.text_input("Keterangan")
    bukti = st.file_uploader("Upload Bukti Transaksi (opsional)", type=["jpg", "jpeg", "png", "pdf"])
    submit = st.form_submit_button("Simpan Transaksi")

    if submit:
        debit = nominal if tipe_akun == "Debit" else 0.0
        kredit = nominal if tipe_akun == "Kredit" else 0.0
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
        st.success("✅ Transaksi berhasil ditambahkan")

# === TAMPILKAN JURNAL HARIAN ===
st.subheader("📑 Jurnal Harian Lengkap")
df_gl = st.session_state[key_gl].copy()

if not df_gl.empty:
    df_gl = df_gl.sort_values("Tanggal")
    for i, row in df_gl.iterrows():
        col1, col2, col3 = st.columns([7, 2, 1])
        with col1:
            st.markdown(f"**{row['Tanggal']}** | {row['Kode Akun']} - {row['Nama Akun']}<br>Keterangan: {row['Keterangan']}<br>Debit: Rp {row['Debit']:,} | Kredit: Rp {row['Kredit']:,}", unsafe_allow_html=True)
        with col2:
            if row['Bukti']:
                st.markdown(f"📎 [{row['Bukti']}](/file/{row['Bukti']})")
        with col3:
            if st.button("Hapus", key=f"hapus_{i}"):
                st.session_state[key_gl] = df_gl.drop(i).reset_index(drop=True)
                st.experimental_rerun()
else:
    st.info("Belum ada transaksi yang dimasukkan.")

# === CATATAN AKHIR ===
st.markdown("""
    <br><br><hr><br>
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

st.success("✅ Jurnal harian berhasil ditampilkan dengan fitur hapus dan upload bukti.")
