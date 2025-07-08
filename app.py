import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

# === Sidebar: Identitas ===
st.sidebar.header("📌 Pilih Unit Lembaga")
lembaga = st.sidebar.selectbox("Lembaga", ["BUMDes", "TPK", "LPMD", "Karang Taruna", "Posyandu", "TSBD", "Pokmas"])
desa = st.sidebar.text_input("Nama Desa", "Keling")
nama_bumdes = st.sidebar.text_input("Nama Lembaga", "Buwana Raharja")
tahun = st.sidebar.number_input("Tahun Laporan", value=2025)

# === Sidebar: Pejabat ===
st.sidebar.header("🖊️ Pejabat Tanda Tangan")
bendahara = st.sidebar.text_input("Nama Bendahara", "Siti Aminah")
direktur = st.sidebar.text_input("Nama Ketua/Pimpinan", "Bambang Setiawan")
kepala_desa = st.sidebar.text_input("Nama Kepala Desa", "Sugeng Riyadi")
ketua_bpd = st.sidebar.text_input("Nama Ketua BPD", "Dwi Purnomo")

# === Header ===
st.markdown(f"""
<h3 style='text-align:center;'>Laporan Keuangan {lembaga} {nama_bumdes} Desa {desa}</h3>
<h4 style='text-align:center;'>Alamat: Jl. Raya Keling, Bukaan, Keling, Kec. Kepung, Kabupaten Kediri, Jawa Timur 64293</h4>
<hr>
""", unsafe_allow_html=True)

# === Pedoman Daftar Akun ===
pedoman_data = {
    "Nama Akun": [
        "Penjualan Barang", "Pendapatan Jasa", "Pendapatan Sewa", "Pendapatan Lainnya",
        "Pembelian Barang", "Beban Operasional", "Gaji", "Listrik", "Transportasi", "Penyusutan",
        "Pendapatan Bunga", "Pendapatan Investasi", "Kas", "Bank", "Piutang", "Persediaan",
        "Tanah", "Peralatan", "Utang Usaha", "Utang Pajak", "Modal Awal", "Laba Tahun Berjalan"
    ],
    "Posisi": [
        "Pendapatan", "Pendapatan", "Pendapatan", "Pendapatan",
        "Beban", "Beban", "Beban", "Beban", "Beban", "Beban",
        "Pendapatan", "Pendapatan", "Aset", "Aset", "Aset", "Aset",
        "Aset", "Aset", "Kewajiban", "Kewajiban", "Ekuitas", "Ekuitas"
    ],
    "Tipe": [
        "Kredit", "Kredit", "Kredit", "Kredit",
        "Debit", "Debit", "Debit", "Debit", "Debit", "Debit",
        "Kredit", "Kredit", "Debit", "Debit", "Debit", "Debit",
        "Debit", "Debit", "Kredit", "Kredit", "Kredit", "Kredit"
    ]
}
pedoman_akun = pd.DataFrame(pedoman_data)

with st.expander("📖 Pedoman Daftar Akun (Manual)"):
    st.dataframe(pedoman_akun, use_container_width=True)

# === Inisialisasi Session State ===
if "jurnal" not in st.session_state:
    st.session_state.jurnal = []

# === Tab Navigasi ===
tab1, tab2, tab3, tab4 = st.tabs(["📘 Jurnal Harian", "📊 Laba Rugi", "📉 Neraca", "💧 Arus Kas"])

# === 📘 JURNAL HARIAN ===
with tab1:
    st.subheader("📘 Jurnal Harian / Buku Besar")

    with st.form("form_input"):
        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal", datetime.today())
            nama_akun = st.selectbox("Pilih Nama Akun", pedoman_akun["Nama Akun"])
        with col2:
            posisi = pedoman_akun[pedoman_akun["Nama Akun"] == nama_akun]["Tipe"].values[0]
if posisi == "Debit":
            jumlah_debit = st.number_input("Jumlah (Debit)", min_value=0.0, step=1000.0)
    jumlah_kredit = 0.0
else:
    jumlah_kredit = st.number_input("Jumlah (Kredit)", min_value=0.0, step=1000.0)
    jumlah_debit = 0.0
        keterangan = st.text_input("Keterangan")
        simpan = st.form_submit_button("➕ Tambah Transaksi")

        st.session_state.jurnal.append({
    "Tanggal": tanggal.strftime("%Y-%m-%d"),
    "Nama Akun": nama_akun,
    "Posisi": posisi,
    "Debit": jumlah_debit,
    "Kredit": jumlah_kredit,
    "Keterangan": keterangan
})

    # Tabel Transaksi
    df_jurnal = pd.DataFrame(st.session_state.jurnal)
    if not df_jurnal.empty:
        st.dataframe(df_jurnal, use_container_width=True)
        hapus_index = st.number_input("Hapus Transaksi ke-", min_value=0, max_value=len(df_jurnal)-1, step=1)
        if st.button("🗑️ Hapus"):
            st.session_state.jurnal.pop(hapus_index)
            st.experimental_rerun()

# === 📊 LABA RUGI ===
with tab2:
    st.subheader("📊 Laporan Laba Rugi")
    if not df_jurnal.empty:
        pendapatan = df_jurnal[df_jurnal["Posisi"] == "Kredit"]["Kredit"].sum()
        beban = df_jurnal[df_jurnal["Posisi"] == "Debit"]["Debit"].sum()
        laba = pendapatan - beban
        lr_df = pd.DataFrame({
            "Uraian": ["Total Pendapatan", "Total Beban", "Laba Bersih"],
            "Jumlah": [pendapatan, beban, laba]
        })
        st.table(lr_df)

# === 📉 NERACA ===
with tab3:
    st.subheader("📉 Neraca")
    if not df_jurnal.empty:
        aset = df_jurnal[df_jurnal["Posisi"] == "Debit"]["Debit"].sum()
        kewajiban_ekuitas = df_jurnal[df_jurnal["Posisi"] == "Kredit"]["Kredit"].sum()
        neraca_df = pd.DataFrame({
            "Kelompok": ["Aset", "Kewajiban + Ekuitas"],
            "Jumlah": [aset, kewajiban_ekuitas]
        })
        st.table(neraca_df)

# === 💧 ARUS KAS ===
with tab4:
    st.subheader("💧 Arus Kas")
    if not df_jurnal.empty:
        kas_masuk = df_jurnal[(df_jurnal["Nama Akun"] == "Kas") & (df_jurnal["Posisi"] == "Debit")]["Debit"].sum()
        kas_keluar = df_jurnal[(df_jurnal["Nama Akun"] == "Kas") & (df_jurnal["Posisi"] == "Kredit")]["Kredit"].sum()
        saldo = kas_masuk - kas_keluar
        arus_df = pd.DataFrame({
            "Uraian": ["Kas Masuk", "Kas Keluar", "Saldo Akhir"],
            "Jumlah": [kas_masuk, kas_keluar, saldo]
        })
        st.table(arus_df)
