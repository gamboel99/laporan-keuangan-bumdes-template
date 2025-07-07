import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import os
from io import BytesIO

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

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

# === INISIALISASI GL ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

# === DAFTAR AKUN SESUAI SISKEUDES ===
daftar_akun = pd.DataFrame({
    "Kode Akun": ["4.1.1", "4.1.2", "5.1.1", "5.1.2", "1.1.1", "1.1.2", "2.1.1", "3.1.1"],
    "Nama Akun": ["Pendapatan Penjualan", "Pendapatan Sewa", "Belanja Barang", "Belanja Jasa", "Kas", "Bank", "Utang Usaha", "Modal Penyertaan"],
    "Posisi": ["Pendapatan", "Pendapatan", "Beban", "Beban", "Aset", "Aset", "Kewajiban", "Ekuitas"],
    "Tipe": ["Kredit", "Kredit", "Debit", "Debit", "Debit", "Debit", "Kredit", "Kredit"]
})

with st.expander("📚 Daftar Akun Standar (SISKEUDES)"):
    st.dataframe(daftar_akun, use_container_width=True)

# === AMBIL DATA GL ===
df_gl = st.session_state[key_gl]

# === LABA RUGI ===
st.header("📊 Laporan Laba Rugi")
pendapatan = df_gl[df_gl["Posisi"] == "Pendapatan"]["Kredit"].sum()
beban = df_gl[df_gl["Posisi"] == "Beban"]["Debit"].sum()
laba_bersih = pendapatan - beban

col_lr1, col_lr2 = st.columns(2)
with col_lr1:
    st.metric("Total Pendapatan", f"Rp {pendapatan:,.2f}")
    st.metric("Total Beban", f"Rp {beban:,.2f}")
    st.metric("Laba Bersih", f"Rp {laba_bersih:,.2f}")

# === NERACA ===
st.header("📄 Neraca (Posisi Keuangan)")
kas = df_gl[df_gl["Nama Akun"] == "Kas"]["Debit"].sum() - df_gl[df_gl["Nama Akun"] == "Kas"]["Kredit"].sum()
bank = df_gl[df_gl["Nama Akun"] == "Bank"]["Debit"].sum() - df_gl[df_gl["Nama Akun"] == "Bank"]["Kredit"].sum()
utang = df_gl[df_gl["Nama Akun"] == "Utang Usaha"]["Kredit"].sum() - df_gl[df_gl["Nama Akun"] == "Utang Usaha"]["Debit"].sum()
modal = df_gl[df_gl["Nama Akun"] == "Modal Penyertaan"]["Kredit"].sum()

aset = kas + bank
total_ke = utang + modal + laba_bersih

col_n1, col_n2 = st.columns(2)
with col_n1:
    st.subheader("Aset")
    st.markdown(f"- Kas: Rp {kas:,.2f}")
    st.markdown(f"- Bank: Rp {bank:,.2f}")
    st.markdown(f"**Total Aset: Rp {aset:,.2f}**")

with col_n2:
    st.subheader("Kewajiban dan Ekuitas")
    st.markdown(f"- Utang Usaha: Rp {utang:,.2f}")
    st.markdown(f"- Modal Penyertaan: Rp {modal:,.2f}")
    st.markdown(f"- Laba Tahun Berjalan: Rp {laba_bersih:,.2f}")
    st.markdown(f"**Total KE: Rp {total_ke:,.2f}**")

# === ARUS KAS ===
st.header("💰 Arus Kas")
kas_masuk = df_gl[df_gl["Nama Akun"] == "Kas"]["Debit"].sum()
kas_keluar = df_gl[df_gl["Nama Akun"] == "Kas"]["Kredit"].sum()
saldo_kas = kas_masuk - kas_keluar

st.metric("Saldo Kas Akhir", f"Rp {saldo_kas:,.2f}")

# === LEMBAR PENGESAHAN ===
st.markdown("---")
st.markdown("""
<h4 style='text-align:center;'>LEMBAR PENGESAHAN</h4>
<table style='width:100%; text-align:center;'>
<tr><td><b>Disusun Oleh</b></td><td><b>Disetujui Oleh</b></td></tr>
<tr><td height='80px'></td><td></td></tr>
<tr><td><u>{}</u><br>Bendahara</td><td><u>{}</u><br>Ketua/Pimpinan</td></tr>
<tr><td colspan='2'><br><b>Mengetahui</b></td></tr>
<tr><td><u>{}</u><br>Kepala Desa</td><td><u>{}</u><br>Ketua BPD</td></tr>
</table>
""".format(bendahara, direktur, kepala_desa, ketua_bpd), unsafe_allow_html=True)

# === DOWNLOADS ===
def download_excel(df, nama_file):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    b64 = base64.b64encode(output.getvalue()).decode()
    return f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}' download='{nama_file}'>⬇️ Download Excel</a>"

st.subheader("📥 Unduh Laporan")
st.markdown(download_excel(df_gl, f"General_Ledger_{lembaga}_{desa}_{tahun}.xlsx"), unsafe_allow_html=True)
st.markdown(download_excel(df_gl[df_gl["Posisi"] == "Pendapatan"], f"Pendapatan_{tahun}.xlsx"), unsafe_allow_html=True)
st.markdown(download_excel(df_gl[df_gl["Posisi"] == "Beban"], f"Beban_{tahun}.xlsx"), unsafe_allow_html=True)

st.success("✅ Laporan Laba Rugi, Neraca, dan Arus Kas selesai dibuat.")
