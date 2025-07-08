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

# === PEDOMAN AKUN MANUAL ===
with st.expander("📚 Pedoman Daftar Akun Manual (SISKEUDES)"):
    st.markdown("""
    | Kode Akun | Nama Akun | Posisi | Tipe |
    |-----------|-----------|--------|------|
    | 5.2.1     | Gaji dan Tunjangan | Beban Usaha | Debit |
    | 4.1.1     | Penjualan Barang Dagang | Pendapatan | Kredit |
    | 1.1.1     | Kas | Aset Lancar | Debit |
    | ...       | ...       | ...    | ...  |
    
    👉 Silakan input berdasarkan tabel di atas untuk menghindari kesalahan posisi debit/kredit.
    """, unsafe_allow_html=True)

# === FORM INPUT TRANSAKSI ===
st.subheader("✍️ Input Transaksi Buku Besar")
with st.form("form_gl", clear_on_submit=True):
    tgl = st.date_input("Tanggal")
    kode_akun = st.text_input("Kode Akun")
    akun_nama = st.text_input("Nama Akun")
    posisi = st.selectbox("Posisi Akun", ["Debit", "Kredit"])
    jumlah = st.number_input("Jumlah", min_value=0.0, step=1000.0)
    keterangan = st.text_area("Keterangan")
    bukti = st.file_uploader("Upload Bukti Transaksi (Opsional)", type=["jpg", "png", "pdf"])
    simpan = st.form_submit_button("✅ Simpan Transaksi")

if simpan:
    debit = jumlah if posisi == "Debit" else 0
    kredit = jumlah if posisi == "Kredit" else 0
    new_row = {"Tanggal": tgl, "Kode Akun": kode_akun, "Nama Akun": akun_nama, "Debit": debit, "Kredit": kredit, "Keterangan": keterangan, "Bukti": bukti.name if bukti else "-"}
    st.session_state[key_gl] = pd.concat([st.session_state[key_gl], pd.DataFrame([new_row])], ignore_index=True)
    st.success("✅ Transaksi berhasil disimpan")

# === TAMPILKAN JURNAL HARIAN ===
st.subheader("📒 Tabel Jurnal Harian (Buku Besar)")
df_gl = st.session_state[key_gl]

# Fitur hapus per baris
hapus_index = st.number_input("Hapus Transaksi Nomor Baris (Opsional)", min_value=0, max_value=len(df_gl)-1 if len(df_gl) > 0 else 0, step=1)
if st.button("🗑️ Hapus Transaksi Ini"):
    st.session_state[key_gl] = df_gl.drop(hapus_index).reset_index(drop=True)
    st.experimental_rerun()

st.dataframe(df_gl.style.set_table_attributes('border="1" class="dataframe table table-bordered table-sm"'), use_container_width=True)

# Catatan: Laporan otomatis Laba Rugi, Neraca, Arus Kas akan ditambahkan selanjutnya.
st.info("📌 Silakan lanjutkan input untuk menghasilkan Laporan Otomatis: Laba Rugi, Neraca, dan Arus Kas")
