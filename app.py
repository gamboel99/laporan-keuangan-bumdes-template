import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import os
from io import BytesIO

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

# === INISIALISASI ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

# === DAFTAR AKUN STANDAR SISKEUDES ===
kode_akun = [
    "4.1.1", "4.1.2", "4.1.3", "4.1.4", "4.1.5", "4.1.6", "4.1.7",  # Pendapatan
    "5.1.1", "5.1.2", "5.1.3", "5.1.4", "5.1.5", "5.1.6",           # HPP
    "5.2.1", "5.2.2", "5.2.3", "5.2.4", "5.2.5", "5.2.6", "5.2.7", "5.2.8", "5.2.9", "5.2.10", "5.2.11",  # Beban Usaha
    "6.1", "6.2", "6.3", "6.4", "6.5", "6.6",                       # Non-Usaha
    "1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.5", "1.1.6", "1.1.7", "1.1.8",  # Aset Lancar
    "1.2.1", "1.2.2", "1.2.3", "1.2.4", "1.2.5", "1.2.6", "1.2.7", "1.2.8", "1.2.9",  # Aset Tetap
    "2.1.1", "2.1.2", "2.1.3", "2.1.4", "2.1.5",                  # Kewajiban Pendek
    "2.2.1", "2.2.2", "2.2.3",                                   # Kewajiban Panjang
    "3.1.1", "3.1.2", "3.1.3", "3.1.4", "3.1.5"                   # Ekuitas
]

nama_akun = [
    "Penjualan Barang Dagang", "Pendapatan Jasa", "Pendapatan Sewa Aset", "Pendapatan Simpan Pinjam", "Pendapatan Usaha Tani", "Pendapatan Wisata", "Pendapatan Lainnya",
    "Pembelian Barang Dagang", "Beban Produksi", "Beban Pemeliharaan Usaha", "Beban Penyusutan Aset Usaha", "Bahan Baku / Operasional", "Beban Lainnya",
    "Gaji dan Tunjangan", "Listrik, Air, Komunikasi", "Transportasi", "Administrasi & Umum", "Sewa Tempat", "Perlengkapan", "Penyusutan Aset Tetap", "Penyuluhan", "Promosi & Publikasi", "Operasional Wisata", "CSR / Kegiatan Desa",
    "Pendapatan Bunga", "Pendapatan Investasi", "Pendapatan Lain-lain", "Beban Bunga", "Kerugian Penjualan Aset", "Pajak",
    "Kas", "Bank", "Piutang Usaha", "Persediaan Dagang", "Persediaan Bahan Baku", "Uang Muka", "Investasi Pendek", "Pendapatan Diterima Di Muka",
    "Tanah", "Bangunan", "Peralatan", "Kendaraan", "Inventaris", "Aset Tetap Lainnya", "Akumulasi Penyusutan", "Investasi Panjang", "Aset Lain-lain",
    "Utang Usaha", "Utang Gaji", "Utang Pajak", "Pendapatan Diterima Di Muka", "Utang Lain-lain",
    "Pinjaman Bank", "Pinjaman Pemerintah", "Utang Pihak Ketiga",
    "Modal Desa", "Modal Pihak Ketiga", "Saldo Laba Ditahan", "Laba Tahun Berjalan", "Cadangan Sosial / Investasi"
]

posisi = (
    ["Pendapatan"] * 7 +
    ["HPP"] * 6 +
    ["Beban Usaha"] * 11 +
    ["Non-Usaha"] * 6 +
    ["Aset Lancar"] * 8 +
    ["Aset Tetap"] * 9 +
    ["Kewajiban Pendek"] * 5 +
    ["Kewajiban Panjang"] * 3 +
    ["Ekuitas"] * 5
)

tipe = (
    ["Kredit"] * 7 +            # Pendapatan
    ["Debit"] * 6 +             # HPP
    ["Debit"] * 11 +            # Beban Usaha
    ["Kredit"] * 3 + ["Debit"] * 3 +   # Non-Usaha (campuran)
    ["Debit"] * 8 +             # Aset Lancar
    ["Debit"] * 8 + ["Kredit"] * 1 +   # Aset Tetap
    ["Kredit"] * 5 +            # Kewajiban Pendek
    ["Kredit"] * 3 +            # Kewajiban Panjang
    ["Kredit"] * 5              # Ekuitas
)

# Pastikan panjangnya sama
assert len(kode_akun) == len(nama_akun) == len(posisi) == len(tipe), "Jumlah elemen pada daftar akun tidak sama."

# Buat DataFrame daftar akun
daftar_akun = pd.DataFrame({
    "Kode Akun": kode_akun,
    "Nama Akun": nama_akun,
    "Posisi": posisi,
    "Tipe": tipe
})
with st.expander("📚 Daftar Akun Standar SISKEUDES"):
    st.dataframe(daftar_akun, use_container_width=True)

# === FORM INPUT TRANSAKSI ===
st.subheader("✍️ Input Transaksi Jurnal Harian")
with st.form("form_transaksi"):
    tanggal = st.date_input("Tanggal Transaksi", datetime.today())
    nama_akun = st.selectbox("Pilih Nama Akun", daftar_akun["Nama Akun"])
    kode_akun = daftar_akun.loc[daftar_akun["Nama Akun"] == nama_akun, "Kode Akun"].values[0]
    posisi_akun = daftar_akun.loc[daftar_akun["Nama Akun"] == nama_akun, "Tipe"].values[0]

    nominal = st.number_input("Nominal Transaksi", min_value=0.0, step=1000.0, format="%.2f")
    keterangan = st.text_input("Keterangan")
    bukti = st.text_input("Nomor / Bukti Transaksi")
    submitted = st.form_submit_button("Tambah Transaksi")

    if submitted and nominal > 0:
        debit = nominal if posisi_akun == "Debit" else 0.0
        kredit = nominal if posisi_akun == "Kredit" else 0.0
        new_row = pd.DataFrame([[tanggal, kode_akun, nama_akun, debit, kredit, keterangan, bukti]],
                                columns=["Tanggal", "Kode Akun", "Nama Akun", "Debit", "Kredit", "Keterangan", "Bukti"])
        st.session_state[key_gl] = pd.concat([st.session_state[key_gl], new_row], ignore_index=True)
        st.success("Transaksi berhasil ditambahkan!")

# === TABEL JURNAL HARIAN ===
st.subheader("📒 Tabel Buku Besar / Jurnal Harian")
df_gl = st.session_state[key_gl]

# HAPUS PER BARIS
for idx in df_gl.index:
    col1, col2, col3 = st.columns([10, 1, 1])
    with col1:
        st.write(df_gl.loc[idx])
    with col2:
        if st.button("🗑️", key=f"hapus_{idx}"):
            df_gl = df_gl.drop(idx).reset_index(drop=True)
            st.session_state[key_gl] = df_gl
            st.experimental_rerun()
            break

# TAMPILKAN TABEL AKHIR
st.dataframe(df_gl, use_container_width=True)

# DOWNLOAD EXCEL
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Jurnal Harian")
    return output.getvalue()

excel_data = convert_df_to_excel(df_gl)
st.download_button("⬇️ Download Jurnal ke Excel", data=excel_data, file_name="jurnal_harian.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Catatan: Laporan otomatis Laba Rugi, Neraca, Arus Kas akan dilanjutkan
