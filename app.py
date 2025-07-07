import streamlit as st
import pandas as pd
import os
from datetime import datetime

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

# === INISIALISASI ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan"])

# === FORM INPUT TRANSAKSI ===
st.subheader("📥 Input Jurnal Harian")
with st.form("form_jurnal"):
    col1, col2, col3 = st.columns(3)
    with col1:
        tgl = st.date_input("Tanggal", datetime.now())
    with col2:
        kode = st.selectbox("Kode Akun", options=[])
    with col3:
        nama = st.text_input("Nama Akun")
    debit = st.number_input("Debit", 0.0)
    kredit = st.number_input("Kredit", 0.0)
    ket = st.text_input("Keterangan")
    submitted = st.form_submit_button("Simpan")

    if submitted:
        new_data = {"Tanggal": tgl, "Kode Akun": kode, "Nama Akun": nama, "Debit": debit, "Kredit": kredit, "Keterangan": ket}
        st.session_state[key_gl] = pd.concat([st.session_state[key_gl], pd.DataFrame([new_data])], ignore_index=True)
        st.success("✅ Transaksi berhasil disimpan.")

# === TAMPILKAN JURNAL ===
df_gl = st.session_state[key_gl]
if not df_gl.empty:
    st.subheader("📜 Jurnal Harian")
    st.dataframe(df_gl, use_container_width=True)

    # === LAPORAN LABA RUGI ===
    st.subheader("📈 Laporan Laba Rugi")
    total_pendapatan = df_gl[df_gl['Kode Akun'].str.startswith("4")]['Kredit'].sum()
    total_beban = df_gl[df_gl['Kode Akun'].str.startswith("5")]['Debit'].sum()
    total_nonusaha = df_gl[df_gl['Kode Akun'].str.startswith("6")]['Debit'].sum()
    laba_bersih = total_pendapatan - (total_beban + total_nonusaha)

    st.write(f"**Total Pendapatan:** Rp {total_pendapatan:,.0f}")
    st.write(f"**Total Beban Usaha:** Rp {total_beban:,.0f}")
    st.write(f"**Total Beban Non-Usaha:** Rp {total_nonusaha:,.0f}")
    st.write(f"**Laba/Rugi Bersih:** Rp {laba_bersih:,.0f}")

    # === NERACA ===
    st.subheader("📊 Neraca")
    aset = df_gl[df_gl['Kode Akun'].str.startswith("1")]['Debit'].sum()
    kewajiban = df_gl[df_gl['Kode Akun'].str.startswith("2")]['Kredit'].sum()
    ekuitas = df_gl[df_gl['Kode Akun'].str.startswith("3")]['Kredit'].sum()
    total_kewajiban_ekuitas = kewajiban + ekuitas

    st.write(f"**Total Aset:** Rp {aset:,.0f}")
    st.write(f"**Total Kewajiban:** Rp {kewajiban:,.0f}")
    st.write(f"**Total Ekuitas:** Rp {ekuitas:,.0f}")
    st.write(f"**Total Kewajiban + Ekuitas:** Rp {total_kewajiban_ekuitas:,.0f}")

    # === ARUS KAS ===
    st.subheader("💸 Laporan Arus Kas")
    kas_masuk = df_gl[df_gl['Kode Akun'].isin(["1.1.1", "1.1.2"])]  # Kas dan Bank
    arus_kas_masuk = kas_masuk['Debit'].sum()
    arus_kas_keluar = kas_masuk['Kredit'].sum()
    saldo_kas = arus_kas_masuk - arus_kas_keluar

    st.write(f"**Arus Kas Masuk:** Rp {arus_kas_masuk:,.0f}")
    st.write(f"**Arus Kas Keluar:** Rp {arus_kas_keluar:,.0f}")
    st.write(f"**Saldo Kas Akhir:** Rp {saldo_kas:,.0f}")

# === LEMBAR PENGESAHAN ===
st.markdown(f"""
    <br><br><br>
    <table width='100%' style='text-align:center;'>
        <tr><td><b>Disusun oleh</b></td><td><b>Disetujui oleh</b></td></tr>
        <tr><td><br><br><br></td><td><br><br><br></td></tr>
        <tr><td><u>{bendahara}</u><br>Bendahara</td><td><u>{direktur}</u><br>Direktur/Pimpinan</td></tr>
        <tr><td colspan='2'><br><br></td></tr>
        <tr><td><b>Mengetahui</b></td><td><b>Mengetahui</b></td></tr>
        <tr><td><br><br><br></td><td><br><br><br></td></tr>
        <tr><td><u>{kepala_desa}</u><br>Kepala Desa</td><td><u>{ketua_bpd}</u><br>Ketua BPD</td></tr>
    </table>
    <br><br>
""", unsafe_allow_html=True)
