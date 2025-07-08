import streamlit as st
import pandas as pd
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

# === DAFTAR AKUN STANDAR ===
kode_akun = ["4.1.1", "4.1.2", "5.1.1"]
nama_akun = ["Pendapatan Jual", "Pendapatan Sewa", "Pembelian Barang"]
posisi = ["Pendapatan", "Pendapatan", "HPP"]
tipe = ["Kredit", "Kredit", "Debit"]

assert len(kode_akun) == len(nama_akun) == len(posisi) == len(tipe), "Jumlah elemen pada daftar akun tidak sama."

daftar_akun = pd.DataFrame({
    "Kode Akun": kode_akun,
    "Nama Akun": nama_akun,
    "Posisi": posisi,
    "Tipe": tipe
})

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

# === GENERAL LEDGER ===
st.title(f"📘 Buku Besar ({lembaga})")
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

with st.form("form_transaksi"):
    st.subheader("✏️ Input Transaksi")
    tanggal = st.date_input("Tanggal", datetime.today())
    akun_nama = st.selectbox("Pilih Nama Akun", daftar_akun["Nama Akun"])
    kode_otomatis = daftar_akun[daftar_akun["Nama Akun"] == akun_nama]["Kode Akun"].values[0]
    tipe_otomatis = daftar_akun[daftar_akun["Nama Akun"] == akun_nama]["Tipe"].values[0]
    st.text(f"Kode Akun: {kode_otomatis} | Posisi: {tipe_otomatis}")
    jumlah = st.number_input("Jumlah", min_value=0.0, step=1000.0)
    keterangan = st.text_input("Keterangan")
    bukti = st.file_uploader("Upload Bukti Transaksi (Opsional)", type=["jpg", "png", "pdf"])
    submitted = st.form_submit_button("Simpan")

    if submitted:
        debit = jumlah if tipe_otomatis == "Debit" else 0
        kredit = jumlah if tipe_otomatis == "Kredit" else 0
        st.session_state[key_gl] = pd.concat([
            st.session_state[key_gl],
            pd.DataFrame.from_records([{
                "Tanggal": tanggal,
                "Kode Akun": kode_otomatis,
                "Nama Akun": akun_nama,
                "Debit": debit,
                "Kredit": kredit,
                "Keterangan": keterangan,
                "Bukti": bukti.name if bukti else ""
            }])
        ], ignore_index=True)
        st.success("Transaksi berhasil disimpan")

# === TAMPILKAN JURNAL HARIAN ===
st.subheader("📑 Jurnal Harian (General Ledger)")
if not st.session_state[key_gl].empty:
    st.dataframe(st.session_state[key_gl], use_container_width=True)
else:
    st.info("Belum ada transaksi.")
