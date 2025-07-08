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
with st.form("form_transaksi"):
    tanggal = st.date_input("Tanggal", value=datetime.date.today())
    akun_nama = st.selectbox("Pilih Nama Akun", daftar_akun["Nama Akun"])
    jumlah = st.number_input("Jumlah", min_value=0.0, step=1000.0, format="%.2f")
    keterangan = st.text_input("Keterangan")

    submitted = st.form_submit_button("Tambah Transaksi")
    if submitted:
        posisi_akun = daftar_akun.loc[daftar_akun["Nama Akun"] == akun_nama, "Tipe"].values[0]

        debit = jumlah if posisi_akun == "Debit" else 0.0
        kredit = jumlah if posisi_akun == "Kredit" else 0.0

        new_row = {
            "Tanggal": tanggal,
            "Nama Akun": akun_nama,
            "Posisi": posisi_akun,
            "Debit": debit,
            "Kredit": kredit,
            "Keterangan": keterangan
        }

        df_gl = pd.concat([df_gl, pd.DataFrame([new_row])], ignore_index=True)
        st.success("✅ Transaksi berhasil ditambahkan.")
        st.session_state["df_gl"] = df_gl

# ----------------------
# Tabel Jurnal
# ----------------------
# === Tabel Jurnal Harian ===
st.markdown("### 🧾 Tabel Jurnal Harian / Buku Besar")
st.dataframe(df_gl.style.format({"Debit": "Rp{:,.2f}", "Kredit": "Rp{:,.2f}"}), use_container_width=True)

# === Tombol Hapus Baris ===
hapus_index = st.number_input("Hapus Baris ke-", min_value=0, max_value=len(df_gl)-1 if len(df_gl) > 0 else 0, step=1)
if st.button("❌ Hapus Transaksi"):
    if not df_gl.empty:
        df_gl = df_gl.drop(hapus_index).reset_index(drop=True)
        st.session_state["df_gl"] = df_gl
        st.success(f"✅ Baris ke-{hapus_index} berhasil dihapus.")

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
