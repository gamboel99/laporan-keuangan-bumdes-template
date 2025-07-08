# ================================================
#  APLIKASI ACCOUNTING: LAPORAN KEUANGAN BUMDes BUWANA RAHARJA
# ================================================

import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# ======== SIDEBAR IDENTITAS DESA/LEMBAGA ========
st.sidebar.title("🧾 Identitas Lembaga")
desa = st.sidebar.text_input("Nama Desa", "Keling")
lembaga = st.sidebar.selectbox("Nama Lembaga", ["BUMDes", "TPK", "LPMD", "Karang Taruna", "Posyandu", "TSBD", "Pokmas"])
nama_bumdes = st.sidebar.text_input("Nama Unit", "Buwana Raharja")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

# === PEJABAT UNTUK PENGESAHAN ===
st.sidebar.markdown("---")
st.sidebar.subheader("Pejabat Tanda Tangan")
bendahara = st.sidebar.text_input("Bendahara", "Siti Aminah")
direktur = st.sidebar.text_input("Pimpinan", "Bambang Setiawan")
kepala_desa = st.sidebar.text_input("Kepala Desa", "Sugeng Riyadi")
ketua_bpd = st.sidebar.text_input("Ketua BPD", "Dwi Purnomo")

# ========= HEADER & LOGO =========
col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    if os.path.exists("logo_pemdes.png"):
        st.image("logo_pemdes.png", width=80)
with col2:
    st.markdown(f"""
        <h3 style='text-align:center;'>Laporan Keuangan {lembaga} {nama_bumdes} Desa {desa}</h3>
        <h5 style='text-align:center;'>Alamat: Jl. Raya Keling, Bukaan, Keling, Kec. Kepung, Kabupaten Kediri, Jawa Timur 64293</h5>
        <hr>
    """, unsafe_allow_html=True)
with col3:
    if os.path.exists("logo_bumdes.png"):
        st.image("logo_bumdes.png", width=80)

# ========= PEDOMAN AKUN =========
pedoman_data = {
    "Nama Akun": [
        "Penjualan Barang Dagang", "Pendapatan Sewa", "Pendapatan Jasa", "Pendapatan Lainnya",
        "Pembelian Barang Dagang", "Beban Produksi", "Gaji & Tunjangan", "Pajak", "Penyusutan",
        "Kas", "Bank", "Piutang", "Utang", "Modal", "Laba Ditahan", "Laba Tahun Berjalan"
    ],
    "Posisi": [
        "Pendapatan", "Pendapatan", "Pendapatan", "Pendapatan",
        "Beban", "Beban", "Beban", "Beban", "Beban",
        "Aset", "Aset", "Aset", "Kewajiban", "Ekuitas", "Ekuitas", "Ekuitas"
    ],
    "Tipe": [
        "Kredit", "Kredit", "Kredit", "Kredit",
        "Debit", "Debit", "Debit", "Debit", "Debit",
        "Debit", "Debit", "Debit", "Kredit", "Kredit", "Kredit", "Kredit"
    ]
}
pedoman_akun = pd.DataFrame(pedoman_data)

with st.expander("📚 Pedoman Akun (Panduan Posisi Debit/Kredit)"):
    st.dataframe(pedoman_akun, use_container_width=True)

# ========= JURNAL TRANSAKSI =========
st.markdown("## 📒 Jurnal Harian / Buku Besar")
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

df_gl = st.session_state[key_gl]

with st.form("form_input"):
    tanggal = st.date_input("Tanggal", value=datetime.now())
    akun_nama = st.selectbox("Pilih Nama Akun", pedoman_akun["Nama Akun"])
    tipe = pedoman_akun[pedoman_akun["Nama Akun"] == akun_nama]["Tipe"].values[0]

    debit, kredit = 0.0, 0.0
    if tipe == "Debit":
        debit = st.number_input("Jumlah (Debit)", min_value=0.0, format="%.2f")
    else:
        kredit = st.number_input("Jumlah (Kredit)", min_value=0.0, format="%.2f")

    keterangan = st.text_input("Keterangan")
    bukti = st.file_uploader("Upload Bukti Transaksi", type=["jpg", "jpeg", "png", "pdf"])
    submitted = st.form_submit_button("✅ Tambah Transaksi")

    if submitted:
        new_row = {
            "Tanggal": tanggal.strftime("%Y-%m-%d"),
            "Nama Akun": akun_nama,
            "Debit": debit,
            "Kredit": kredit,
            "Keterangan": keterangan,
            "Bukti": bukti.name if bukti else "-"
        }
        st.session_state[key_gl] = pd.concat([df_gl, pd.DataFrame([new_row])], ignore_index=True)
        st.success("✅ Transaksi berhasil ditambahkan.")

# === TABEL JURNAL & FITUR HAPUS ===
st.markdown("### 📋 Tabel Jurnal Transaksi")
df_gl = st.session_state[key_gl]
if not df_gl.empty:
    st.dataframe(df_gl, use_container_width=True)
    hapus = st.number_input("Hapus transaksi ke (baris)", min_value=1, max_value=len(df_gl), step=1)
    if st.button("🗑️ Hapus Baris"):
        st.session_state[key_gl] = df_gl.drop(df_gl.index[hapus - 1]).reset_index(drop=True)
        st.success("Baris berhasil dihapus.")
else:
    st.info("Belum ada transaksi yang dicatat.")

# === NAVIGASI LAPORAN ===
tabs = st.tabs(["📊 Laba Rugi", "📑 Neraca", "💸 Arus Kas", "📦 Unduh Semua"])

# === PERHITUNGAN OTOMATIS ===
df = st.session_state[key_gl]
if not df.empty:
    pd_pendapatan = df[df["Nama Akun"].isin(pedoman_akun[pedoman_akun["Posisi"] == "Pendapatan"]["Nama Akun"])]
    pd_beban = df[df["Nama Akun"].isin(pedoman_akun[pedoman_akun["Posisi"] == "Beban"]["Nama Akun"])]
    pd_aset = df[df["Nama Akun"].isin(pedoman_akun[pedoman_akun["Posisi"] == "Aset"]["Nama Akun"])]
    pd_kewajiban = df[df["Nama Akun"].isin(pedoman_akun[pedoman_akun["Posisi"] == "Kewajiban"]["Nama Akun"])]
    pd_ekuitas = df[df["Nama Akun"].isin(pedoman_akun[pedoman_akun["Posisi"] == "Ekuitas"]["Nama Akun"])]

    laba = pd_pendapatan["Kredit"].sum() - pd_beban["Debit"].sum()
    kas = pd_aset["Debit"].sum() - df[df["Nama Akun"] == "Kas"]["Kredit"].sum()

    with tabs[0]:
        st.subheader("📊 Laporan Laba Rugi")
        st.table({
            "Pendapatan": [pd_pendapatan["Kredit"].sum()],
            "Beban": [pd_beban["Debit"].sum()],
            "Laba Bersih": [laba]
        })

    with tabs[1]:
        st.subheader("📑 Neraca")
        st.table({
            "Aset": [pd_aset["Debit"].sum()],
            "Kewajiban": [pd_kewajiban["Kredit"].sum()],
            "Ekuitas": [pd_ekuitas["Kredit"].sum()],
            "Saldo Akhir": [kas]
        })

    with tabs[2]:
        st.subheader("💸 Arus Kas")
        st.table({
            "Kas Masuk": [df["Debit"].sum()],
            "Kas Keluar": [df["Kredit"].sum()],
            "Saldo Kas": [df["Debit"].sum() - df["Kredit"].sum()]
        })

    with tabs[3]:
        st.download_button("📥 Unduh Jurnal Excel", data=df.to_csv(index=False).encode(), file_name="jurnal.csv")
else:
    st.warning("📭 Belum ada transaksi, laporan belum tersedia.")

# === LEMBAR PENGESAHAN ===
st.markdown("""
    <br><br><br><hr>
    <h5 style='text-align:center;'>LEMBAR PENGESAHAN</h5>
    <table width='100%' style='text-align:center;'>
        <tr><td><b>Disusun oleh</b></td><td><b>Disetujui oleh</b></td></tr>
        <tr><td><br><br><br></td><td><br><br><br></td></tr>
        <tr><td><u>{}</u><br>Bendahara</td><td><u>{}</u><br>Pimpinan Lembaga</td></tr>
        <tr><td colspan='2'><br><br></td></tr>
        <tr><td><b>Mengetahui</b></td><td><b>Mengetahui</b></td></tr>
        <tr><td><br><br><br></td><td><br><br><br></td></tr>
        <tr><td><u>{}</u><br>Kepala Desa</td><td><u>{}</u><br>Ketua BPD</td></tr>
    </table>
""".format(bendahara, direktur, kepala_desa, ketua_bpd), unsafe_allow_html=True)
