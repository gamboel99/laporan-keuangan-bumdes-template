import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Laporan Keuangan Lembaga Desa", layout="wide")

# === SIDEBAR ===
st.sidebar.title("🔰 Pilih Unit Lembaga")
lembaga = st.sidebar.selectbox("Lembaga", ["BUMDes", "TPK", "LPMD", "Karang Taruna", "Posyandu", "TSBD", "Pokmas"])
desa = st.sidebar.text_input("Nama Desa", "Keling")
nama_bumdes = st.sidebar.text_input("Nama Lembaga", "Buwana Raharja")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

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

# === DAFTAR PEDOMAN AKUN (TIDAK BERDAMPAK SISTEM, HANYA PANDUAN) ===
pedoman_akun = pd.DataFrame({
    "Kode Akun": ["4.1.1", "5.2.1", "1.1.1", "2.1.1", "3.1.1"],
    "Nama Akun": ["Pendapatan Usaha Dagang", "Gaji dan Tunjangan", "Kas", "Utang Usaha", "Modal Desa"],
    "Posisi": ["Pendapatan", "Beban Usaha", "Aset Lancar", "Kewajiban", "Ekuitas"],
    "Tipe": ["Kredit", "Debit", "Debit", "Kredit", "Kredit"]
})
with st.expander("📚 Pedoman Daftar Akun (Hanya Panduan)"):
    st.dataframe(pedoman_akun, use_container_width=True)

# === INISIALISASI JURNAL UMUM ===
st.title(f"📘 Jurnal Harian / Buku Besar ({lembaga})")
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

df_gl = st.session_state[key_gl]

# === INPUT TRANSAKSI ===
st.subheader("➕ Input Transaksi Baru")
with st.form("form_input"):
    col1, col2, col3 = st.columns(3)
    with col1:
        tanggal = st.date_input("Tanggal", datetime.now())
        akun_nama = st.selectbox("Pilih Nama Akun", pedoman_akun["Nama Akun"])
    with col2:
        keterangan = st.text_input("Keterangan")
        bukti = st.file_uploader("Upload Bukti Transaksi (opsional)", type=["jpg", "jpeg", "png", "pdf"])
    with col3:
        tipe = pedoman_akun[pedoman_akun["Nama Akun"] == akun_nama]["Tipe"].values[0]
        if tipe == "Debit":
            debit = st.number_input("Jumlah (Debit)", 0.0)
            kredit = 0.0
        else:
            kredit = st.number_input("Jumlah (Kredit)", 0.0)
            debit = 0.0

    submitted = st.form_submit_button("Simpan")
    if submitted:
        kode = pedoman_akun[pedoman_akun["Nama Akun"] == akun_nama]["Kode Akun"].values[0]
        new_data = pd.DataFrame([[tanggal, kode, akun_nama, debit, kredit, keterangan, bukti.name if bukti else ""]],
                                 columns=df_gl.columns)
        st.session_state[key_gl] = pd.concat([df_gl, new_data], ignore_index=True)
        st.success("✅ Transaksi berhasil ditambahkan!")

# === TAMPILKAN JURNAL ===
st.subheader("📄 Daftar Transaksi (Jurnal Harian)")
df_gl = st.session_state[key_gl]

if not df_gl.empty:
    for i in df_gl.index:
        col1, col2 = st.columns([10, 1])
        with col1:
            st.markdown(f"{i+1}. {df_gl.loc[i, 'Tanggal']} | {df_gl.loc[i, 'Kode Akun']} - {df_gl.loc[i, 'Nama Akun']} | Debit: Rp{df_gl.loc[i, 'Debit']:,.0f} | Kredit: Rp{df_gl.loc[i, 'Kredit']:,.0f} | {df_gl.loc[i, 'Keterangan']}")
        with col2:
            if st.button("❌", key=f"hapus_{i}"):
                st.session_state[key_gl] = df_gl.drop(i).reset_index(drop=True)
                st.experimental_rerun()
else:
    st.warning("Belum ada transaksi.")

# === LEMBAR PENGESAHAN ===
st.markdown("""
    <br><br><br>
    <table width='100%' style='text-align:center;'>
        <tr><td><b>Disusun oleh</b></td><td><b>Disetujui oleh</b></td></tr>
        <tr><td><br><br><br></td><td><br><br><br></td></tr>
        <tr><td><u>{}</u><br>Bendahara</td><td><u>{}</u><br>Direktur/Pimpinan</td></tr>
        <tr><td colspan='2'><br><br></td></tr>
        <tr><td><b>Mengetahui</b></td><td><b>Mengetahui</b></td></tr>
        <tr><td><br><br><br></td><td><br><br><br></td></tr>
        <tr><td><u>{}</u><br>Kepala Desa</td><td><u>{}</u><br>Ketua BPD</td></tr>
    </table>
    <br><br>
""".format(bendahara, direktur, kepala_desa, ketua_bpd), unsafe_allow_html=True)

st.success("✅ Semua sistem input dan tabel jurnal berhasil dimuat. Siap lanjut ke laporan otomatis.")
