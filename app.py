import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# --- Inisialisasi Session State untuk General Ledger ---
if "df_gl" not in st.session_state:
    st.session_state.df_gl = pd.DataFrame(columns=["Tanggal", "Nama Akun", "Posisi", "Debit", "Kredit", "Keterangan"])

df_gl = st.session_state.df_gl

# --- Data Pedoman Akun ---
pedoman_data = {
    "Nama Akun": [
        "Kas", "Bank", "Piutang Dagang", "Persediaan Barang Dagang", "Perlengkapan",
        "Peralatan", "Bangunan", "Tanah", "Akumulasi Penyusutan", "Hutang Usaha",
        "Modal Awal", "Pendapatan Usaha", "Pendapatan Non Usaha", "HPP", "Gaji Pegawai",
        "Biaya Listrik", "Biaya Air", "Biaya Transportasi", "Biaya Pemasaran", "Biaya Penyusutan"
    ],
    "Tipe": [
        "Debit", "Debit", "Debit", "Debit", "Debit",
        "Debit", "Debit", "Debit", "Kredit", "Kredit",
        "Kredit", "Kredit", "Kredit", "Debit", "Debit",
        "Debit", "Debit", "Debit", "Debit", "Debit"
    ]
}

pedoman_akun = pd.DataFrame(pedoman_data)

# --- Tampilan Pedoman Akun ---
with st.expander("📘 Pedoman Daftar Akun (Manual)"):
    st.dataframe(pedoman_akun, use_container_width=True)

# === FORM TRANSAKSI ===
st.markdown("### 🧾 Jurnal Harian / Buku Besar")
with st.form("form_transaksi"):
    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal", value=datetime.date.today())
    with col2:
        akun_nama = st.selectbox("Pilih Nama Akun", pedoman_akun["Nama Akun"])

    posisi_akun = pedoman_akun[pedoman_akun["Nama Akun"] == akun_nama]["Tipe"].values[0]

    jumlah = st.number_input(f"Jumlah ({posisi_akun})", min_value=0.0, step=1000.0, format="%.2f")
    keterangan = st.text_input("Keterangan")

    submitted = st.form_submit_button("Tambah Transaksi")

    if submitted:
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

        st.session_state.df_gl = pd.concat([st.session_state.df_gl, pd.DataFrame([new_row])], ignore_index=True)
        st.success("✅ Transaksi berhasil ditambahkan.")

# === TABEL JURNAL ===
st.markdown("### 📑 Tabel Jurnal Harian / Buku Besar")
st.dataframe(st.session_state.df_gl.style.format({"Debit": "Rp{:,.2f}", "Kredit": "Rp{:,.2f}"}), use_container_width=True)

# === HAPUS TRANSAKSI ===
if not st.session_state.df_gl.empty:
    hapus_index = st.number_input("Hapus Baris ke-", min_value=0, max_value=len(st.session_state.df_gl)-1, step=1)
    if st.button("❌ Hapus Transaksi"):
        st.session_state.df_gl = st.session_state.df_gl.drop(hapus_index).reset_index(drop=True)
        st.success(f"✅ Baris ke-{hapus_index} berhasil dihapus.")

# === LAPORAN OTOMATIS ===
st.markdown("---")
st.markdown("### 📊 Laporan Otomatis")
tab1, tab2, tab3 = st.tabs(["Laba Rugi", "Neraca", "Arus Kas"])

with tab1:
    st.subheader("Laporan Laba Rugi")
    df_laba_rugi = st.session_state.df_gl[st.session_state.df_gl["Nama Akun"].isin(
        pedoman_akun[pedoman_akun["Nama Akun"].str.contains("Pendapatan|HPP|Biaya")]["Nama Akun"])]
    st.dataframe(df_laba_rugi, use_container_width=True)
    total_pendapatan = df_laba_rugi[df_laba_rugi["Posisi"] == "Kredit"]["Kredit"].sum()
    total_beban = df_laba_rugi[df_laba_rugi["Posisi"] == "Debit"]["Debit"].sum()
    laba_bersih = total_pendapatan - total_beban
    st.write(f"**Laba Bersih:** Rp {laba_bersih:,.2f}")

with tab2:
    st.subheader("Laporan Neraca")
    df_neraca = st.session_state.df_gl[st.session_state.df_gl["Nama Akun"].isin(
        pedoman_akun[pedoman_akun["Nama Akun"].isin([
            "Kas", "Bank", "Piutang Dagang", "Persediaan Barang Dagang", "Perlengkapan",
            "Peralatan", "Bangunan", "Tanah", "Akumulasi Penyusutan", "Hutang Usaha", "Modal Awal"
        ])]["Nama Akun"])]
    st.dataframe(df_neraca, use_container_width=True)

with tab3:
    st.subheader("Laporan Arus Kas")
    df_arus_kas = st.session_state.df_gl[st.session_state.df_gl["Nama Akun"].isin([
        "Kas", "Bank"
    ])]
    kas_masuk = df_arus_kas["Debit"].sum()
    kas_keluar = df_arus_kas["Kredit"].sum()
    saldo_kas = kas_masuk - kas_keluar
    st.dataframe(df_arus_kas, use_container_width=True)
    st.write(f"**Saldo Kas Akhir:** Rp {saldo_kas:,.2f}")
