import streamlit as st
import pandas as pd
from datetime import datetime
import os

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

# === DAFTAR AKUN SISKEUDES ===
daftar_akun = pd.DataFrame({
    "Kode Akun": ["4.1.1", "4.1.2", "4.1.3", "5.1.1", "5.1.2", "5.2.1", "5.2.2", "6.1", "6.2", "1.1.1", "1.2.1", "2.1.1", "3.1.1"],
    "Nama Akun": ["Penjualan Barang", "Pendapatan Jasa", "Pendapatan Lain", "Pembelian Barang", "Biaya Operasional", "Gaji", "Listrik & Air", "Pendapatan Lain", "Beban Pajak", "Kas", "Aset Tetap", "Utang Usaha", "Modal Awal"],
    "Posisi": ["Pendapatan", "Pendapatan", "Pendapatan", "HPP", "Beban Usaha", "Beban Usaha", "Beban Usaha", "Non-Usaha", "Non-Usaha", "Aset Lancar", "Aset Tetap", "Kewajiban", "Ekuitas"],
    "Tipe": ["Kredit", "Kredit", "Kredit", "Debit", "Debit", "Debit", "Debit", "Kredit", "Kredit", "Debit", "Debit", "Kredit", "Kredit"]
})

# === JURNAL UMUM ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan"])

st.subheader("📥 Input Transaksi Jurnal Harian")
with st.form("input_transaksi"):
    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal", value=datetime.today())
        akun_opsi = st.selectbox("Pilih Nama Akun", daftar_akun["Nama Akun"])
        keterangan = st.text_input("Keterangan")
    with col2:
        nominal_debit = st.number_input("Debit (Rp)", min_value=0, step=1000)
        nominal_kredit = st.number_input("Kredit (Rp)", min_value=0, step=1000)
    submitted = st.form_submit_button("Tambah Transaksi")
    if submitted:
        kode = daftar_akun.loc[daftar_akun["Nama Akun"] == akun_opsi, "Kode Akun"].values[0]
        new_row = pd.DataFrame([[tanggal, kode, akun_opsi, nominal_debit, nominal_kredit, keterangan]], columns=st.session_state[key_gl].columns)
        st.session_state[key_gl] = pd.concat([st.session_state[key_gl], new_row], ignore_index=True)
        st.success("✅ Transaksi berhasil ditambahkan.")

st.subheader("📋 Tabel Buku Besar")
df_gl = st.session_state[key_gl]
if not df_gl.empty:
    for i in df_gl.index:
        st.write(f"{i+1}. {df_gl.loc[i, 'Tanggal']} - {df_gl.loc[i, 'Nama Akun']} - Rp {df_gl.loc[i, 'Debit']:,} / Rp {df_gl.loc[i, 'Kredit']:,}")
        if st.button(f"Hapus {i+1}", key=f"hapus_{i}"):
            st.session_state[key_gl] = df_gl.drop(i).reset_index(drop=True)
            st.experimental_rerun()
else:
    st.warning("Belum ada transaksi yang ditambahkan.")

# === LAPORAN OTOMATIS ===
if not df_gl.empty:
    st.subheader("📑 Laporan Laba Rugi")
    df_merge = df_gl.merge(daftar_akun, on="Nama Akun", how="left")
    pendapatan = df_merge[df_merge["Posisi"] == "Pendapatan"]["Kredit"].sum()
    hpp = df_merge[df_merge["Posisi"] == "HPP"]["Debit"].sum()
    beban = df_merge[df_merge["Posisi"] == "Beban Usaha"]["Debit"].sum()
    nonusaha = df_merge[df_merge["Posisi"] == "Non-Usaha"].fillna(0)
    total_nonusaha = nonusaha["Kredit"].sum() - nonusaha["Debit"].sum()
    laba_bersih = pendapatan - hpp - beban + total_nonusaha
    st.metric("Pendapatan", f"Rp {pendapatan:,.0f}")
    st.metric("HPP", f"Rp {hpp:,.0f}")
    st.metric("Beban Usaha", f"Rp {beban:,.0f}")
    st.metric("Laba Bersih", f"Rp {laba_bersih:,.0f}")

    st.subheader("🧾 Neraca")
    aset = df_merge[df_merge["Posisi"].str.contains("Aset")]
    kewajiban = df_merge[df_merge["Posisi"] == "Kewajiban"]
    ekuitas = df_merge[df_merge["Posisi"] == "Ekuitas"]
    total_aset = aset["Debit"].sum() - aset["Kredit"].sum()
    total_kewajiban = kewajiban["Kredit"].sum() - kewajiban["Debit"].sum()
    total_ekuitas = ekuitas["Kredit"].sum() - ekuitas["Debit"].sum()
    st.metric("Aset", f"Rp {total_aset:,.0f}")
    st.metric("Kewajiban", f"Rp {total_kewajiban:,.0f}")
    st.metric("Ekuitas", f"Rp {total_ekuitas:,.0f}")
    st.metric("Balance", f"Rp {total_aset:,.0f}" if abs(total_aset - (total_kewajiban + total_ekuitas)) < 1 else "Tidak Seimbang")

    st.subheader("💰 Arus Kas")
    kas_masuk = df_merge[df_merge["Nama Akun"] == "Kas"]["Debit"].sum()
    kas_keluar = df_merge[df_merge["Nama Akun"] == "Kas"]["Kredit"].sum()
    saldo_kas = kas_masuk - kas_keluar
    st.metric("Kas Masuk", f"Rp {kas_masuk:,.0f}")
    st.metric("Kas Keluar", f"Rp {kas_keluar:,.0f}")
    st.metric("Saldo Akhir Kas", f"Rp {saldo_kas:,.0f}")

# === LEMBAR PENGESAHAN ===
st.markdown("""
    <br><br><br>
    <table width='100%' style='text-align:center;'>
        <tr><td><b>Disusun oleh</b></td><td><b>Disetujui oleh</b></td></tr>
        <tr><td><br><br><br></td><td><br><br><br></td></tr>
        <tr><td><u>{}</u><br>Bendahara</td><td><u>{}</u><br>Ketua/Pimpinan</td></tr>
        <tr><td colspan='2'><br><br></td></tr>
        <tr><td><b>Mengetahui</b></td><td><b>Mengetahui</b></td></tr>
        <tr><td><br><br><br></td><td><br><br><br></td></tr>
        <tr><td><u>{}</u><br>Kepala Desa</td><td><u>{}</u><br>Ketua BPD</td></tr>
    </table>
    <br><br>
""".format(bendahara, direktur, kepala_desa, ketua_bpd), unsafe_allow_html=True)

st.success("✅ Laporan keuangan lengkap berhasil dimuat dan diproses tanpa error.")
