import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import os
from io import BytesIO

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# === PILIHAN MULTI LEMBAGA DAN DESA ===
st.sidebar.title("🔰 Pilih Unit Lembaga")
lembaga = st.sidebar.selectbox("Lembaga", ["BUMDes", "PKK", "Karang Taruna", "LPMD", "BPD", "TPK", "Posyandu", "TSBD", "Pokmas"])
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
    <h3 style='text-align:center;'>Laporan Keuangan {nama_bumdes} Desa {desa}</h3>
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

# === INISIALISASI ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

# === DAFTAR AKUN SESUAI SISKEUDES ===
daftar_akun = pd.DataFrame({
    "Kode Akun": ["4.1", "4.2", "4.3", "5.1", "5.2", "1.1", "1.2", "2.1", "3.1"],
    "Nama Akun": [
        "Pendapatan Jasa", "Pendapatan Usaha Tani", "Pendapatan Sewa", 
        "Belanja Barang", "Belanja Jasa", 
        "Kas", "Bank", "Utang Dagang", 
        "Modal Desa"
    ],
    "Posisi": ["Pendapatan", "Pendapatan", "Pendapatan", "Beban", "Beban", "Aset", "Aset", "Kewajiban", "Ekuitas"],
    "Tipe": ["Kredit"] * 3 + ["Debit"] * 2 + ["Debit"] * 2 + ["Kredit", "Kredit"]
})

with st.expander("📚 Daftar Akun Standar Siskeudes"):
    st.dataframe(daftar_akun, use_container_width=True)

# === FORM TAMBAH TRANSAKSI ===
with st.expander("➕ Tambah Transaksi"):
    col1, col2, col3 = st.columns(3)
    with col1:
        tanggal = st.date_input("Tanggal", datetime.today())
    with col2:
        kode_akun = st.selectbox("Kode Akun", daftar_akun["Kode Akun"])
    with col3:
        nama_akun = daftar_akun.loc[daftar_akun["Kode Akun"] == kode_akun, "Nama Akun"].values[0]

    keterangan = st.text_input("Keterangan")
    col4, col5, col6 = st.columns(3)
    with col4:
        debit = st.number_input("Debit", min_value=0.0, format="%.2f")
    with col5:
        kredit = st.number_input("Kredit", min_value=0.0, format="%.2f")
    with col6:
        bukti_file = st.file_uploader("Upload Nota/Bukti", type=["png", "jpg", "jpeg", "pdf"])

    if st.button("💾 Simpan Transaksi"):
        if kode_akun and (debit > 0 or kredit > 0):
            if bukti_file:
                bukti_path = f"bukti_{datetime.now().strftime('%Y%m%d%H%M%S')}_{bukti_file.name}"
                with open(bukti_path, "wb") as f:
                    f.write(bukti_file.read())
            else:
                bukti_path = ""
            new_row = pd.DataFrame([{
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Kode Akun": kode_akun,
                "Nama Akun": nama_akun,
                "Debit": debit,
                "Kredit": kredit,
                "Keterangan": keterangan,
                "Bukti": bukti_path
            }])
            st.session_state[key_gl] = pd.concat([st.session_state[key_gl], new_row], ignore_index=True)
            st.success("✅ Transaksi berhasil disimpan.")
        else:
            st.warning("⚠️ Lengkapi semua data transaksi.")

# === TAMPILKAN DAN HAPUS ===
st.subheader("📋 Daftar Transaksi")
df_gl = st.session_state[key_gl]

if not df_gl.empty:
    for i in df_gl.index:
        st.write(f"{df_gl.at[i, 'Tanggal']} - {df_gl.at[i, 'Kode Akun']} {df_gl.at[i, 'Nama Akun']}")
        st.write(f"💬 {df_gl.at[i, 'Keterangan']} | Debit: Rp{df_gl.at[i, 'Debit']}, Kredit: Rp{df_gl.at[i, 'Kredit']}")
        if df_gl.at[i, 'Bukti'] and os.path.exists(df_gl.at[i, 'Bukti']):
            if df_gl.at[i, 'Bukti'].endswith(".pdf"):
                st.markdown(f"[📎 Lihat PDF]({df_gl.at[i, 'Bukti']})")
            else:
                st.image(df_gl.at[i, 'Bukti'], width=200)
        if st.button(f"Hapus Transaksi {i+1}", key=f"hapus_{i}"):
            st.session_state[key_gl] = df_gl.drop(index=i).reset_index(drop=True)
            st.experimental_rerun()
else:
    st.info("Belum ada transaksi.")

# === GABUNGKAN DATA DENGAN DAFTAR AKUN UNTUK POSISI ===
df_gl_merged = df_gl.merge(daftar_akun, on=["Kode Akun", "Nama Akun"], how="left")

# === HITUNG LABA RUGI SEDERHANA ===
pendapatan = df_gl_merged[df_gl_merged["Posisi"] == "Pendapatan"]["Kredit"].sum()
beban = df_gl_merged[df_gl_merged["Posisi"] == "Beban"]["Debit"].sum()
laba_bersih = pendapatan - beban

st.subheader("📊 Laporan Laba Rugi")
st.write(f"**Total Pendapatan:** Rp {pendapatan:,.2f}")
st.write(f"**Total Beban:** Rp {beban:,.2f}")
st.write(f"**Laba Bersih:** Rp {laba_bersih:,.2f}")

# === EKSPOR EXCEL LABA RUGI ===
def download_excel(dataframe, filename):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Sheet1')
    b64 = base64.b64encode(output.getvalue()).decode()
    return f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}' download='{filename}'>⬇️ Download Excel</a>"

st.markdown(download_excel(df_gl, f"General_Ledger_{lembaga}_{desa}_{tahun}.xlsx"), unsafe_allow_html=True)

# === LEMBAR PENGESAHAN ===
st.markdown("---")
st.markdown("""
    <br><br>
    <table style='width:100%; text-align:center;'>
        <tr>
            <td><b>Disusun oleh</b><br>Bendahara<br><br><br><br><u>{bendahara}</u></td>
            <td><b>Disetujui oleh</b><br>Direktur Utama<br><br><br><br><u>{direktur}</u></td>
        </tr>
        <tr>
            <td colspan='2'><br><br></td>
        </tr>
        <tr>
            <td><b>Mengetahui</b><br>Kepala Desa<br><br><br><br><u>{kepala_desa}</u></td>
            <td><b>Mengetahui</b><br>Ketua BPD<br><br><br><br><u>{ketua_bpd}</u></td>
        </tr>
    </table>
""".format(bendahara=bendahara, direktur=direktur, kepala_desa=kepala_desa, ketua_bpd=ketua_bpd), unsafe_allow_html=True)

st.success("✅ General Ledger dan Laba Rugi berhasil ditampilkan.")
