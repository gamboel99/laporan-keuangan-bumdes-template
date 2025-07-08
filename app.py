import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

# Inisialisasi session state
if "jurnal" not in st.session_state:
    st.session_state.jurnal = []

# ----------------------
# Header dan Identitas
# ----------------------
st.title("Laporan Keuangan BUMDes Buwana Raharja Desa Keling")
st.markdown("""
**Alamat:** Jl. Raya Keling, Bukaan, Keling, Kec. Kepung, Kabupaten Kediri, Jawa Timur 64293
""")

# ----------------------
# Pedoman Akun
# ----------------------
pedoman_data = {
    "Nama Akun": [
        "Modal Awal", "Kas", "Bank", "Piutang Usaha", "Persediaan Barang Dagang", "Peralatan", "Aset Tetap Lainnya",
        "Hutang Usaha", "Pendapatan Usaha", "Pendapatan Non-Usaha", "HPP", "Beban Gaji", "Beban Listrik", "Beban Sewa",
        "Beban Penyusutan", "Beban Operasional Lainnya", "Laba Ditahan"
    ],
    "Tipe": [
        "Kredit", "Debit", "Debit", "Debit", "Debit", "Debit", "Debit",
        "Kredit", "Kredit", "Kredit", "Debit", "Debit", "Debit", "Debit",
        "Debit", "Debit", "Kredit"
    ]
}

pedoman_akun = pd.DataFrame(pedoman_data)

with st.expander("📘 Pedoman Daftar Akun (Manual)"):
    st.dataframe(pedoman_akun, use_container_width=True)

# ----------------------
# Form Input Transaksi
# ----------------------
st.header("📒 Jurnal Harian / Buku Besar")
with st.form("form_transaksi"):
    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal", datetime.today())
    with col2:
        nama_akun = st.selectbox("Pilih Nama Akun", pedoman_akun["Nama Akun"])

    posisi = pedoman_akun[pedoman_akun["Nama Akun"] == nama_akun]["Tipe"].values[0]

    col3 = st.columns(1)[0]
    if posisi == "Debit":
        jumlah_debit = col3.number_input("Jumlah (Debit)", min_value=0.0, step=1000.0)
        jumlah_kredit = 0.0
    else:
        jumlah_kredit = col3.number_input("Jumlah (Kredit)", min_value=0.0, step=1000.0)
        jumlah_debit = 0.0

    keterangan = st.text_input("Keterangan")

    submitted = st.form_submit_button("+ Tambah Transaksi")
    if submitted:
        st.session_state.jurnal.append({
            "Tanggal": tanggal.strftime("%Y-%m-%d"),
            "Nama Akun": nama_akun,
            "Posisi": posisi,
            "Debit": jumlah_debit,
            "Kredit": jumlah_kredit,
            "Keterangan": keterangan
        })
        st.success("✅ Transaksi berhasil ditambahkan.")

# ----------------------
# Tabel Jurnal
# ----------------------
st.subheader("📑 Tabel Jurnal Harian / Buku Besar")
df_jurnal = pd.DataFrame(st.session_state.jurnal)

if not df_jurnal.empty:
    st.dataframe(df_jurnal, use_container_width=True)
    # Fitur Hapus
    for i, row in df_jurnal.iterrows():
        if st.button(f"❌ Hapus {i+1}", key=f"hapus_{i}"):
            st.session_state.jurnal.pop(i)
            st.experimental_rerun()
else:
    st.warning("Belum ada transaksi.")

# ----------------------
# Laporan Otomatis
# ----------------------
st.header("📊 Laporan Keuangan Otomatis")
tabs = st.tabs(["Laba Rugi", "Neraca", "Arus Kas"])

# --- LABA RUGI ---
with tabs[0]:
    st.subheader("📈 Laporan Laba Rugi")
    df = df_jurnal.copy()
    df["Debit"] = pd.to_numeric(df["Debit"], errors='coerce').fillna(0)
    df["Kredit"] = pd.to_numeric(df["Kredit"], errors='coerce').fillna(0)

    pendapatan = df[(df["Posisi"] == "Kredit") & (df["Nama Akun"].str.contains("Pendapatan"))]["Kredit"].sum()
    hpp = df[df["Nama Akun"] == "HPP"]["Debit"].sum()
    beban = df[(df["Posisi"] == "Debit") & (df["Nama Akun"].str.contains("Beban"))]["Debit"].sum()
    laba_bersih = pendapatan - hpp - beban

    laba_rugi = pd.DataFrame({
        "Keterangan": ["Pendapatan", "HPP", "Beban", "Laba Bersih"],
        "Jumlah": [pendapatan, hpp, beban, laba_bersih]
    })
    st.table(laba_rugi.set_index("Keterangan"))

# --- NERACA ---
with tabs[1]:
    st.subheader("📒 Neraca")
    aset = df[df["Posisi"] == "Debit"]["Debit"].sum()
    kewajiban = df[df["Nama Akun"] == "Hutang Usaha"]["Kredit"].sum()
    ekuitas = df[df["Nama Akun"] == "Modal Awal"]["Kredit"].sum() + laba_bersih

    neraca = pd.DataFrame({
        "Keterangan": ["Aset", "Kewajiban", "Ekuitas"],
        "Jumlah": [aset, kewajiban, ekuitas]
    })
    st.table(neraca.set_index("Keterangan"))

# --- ARUS KAS ---
with tabs[2]:
    st.subheader("💸 Laporan Arus Kas")
    kas_masuk = df[df["Posisi"] == "Debit"]["Debit"].sum()
    kas_keluar = df[df["Posisi"] == "Kredit"]["Kredit"].sum()
    saldo_kas = kas_masuk - kas_keluar

    arus_kas = pd.DataFrame({
        "Keterangan": ["Kas Masuk", "Kas Keluar", "Saldo Kas"],
        "Jumlah": [kas_masuk, kas_keluar, saldo_kas]
    })
    st.table(arus_kas.set_index("Keterangan"))
