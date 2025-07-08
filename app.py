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

# === PEDOMAN AKUN ===
akun_data = [
    ("Penjualan Barang Dagang", "Pendapatan", "Kredit"),
    ("Pendapatan Jasa", "Pendapatan", "Kredit"),
    ("Pendapatan Sewa Aset", "Pendapatan", "Kredit"),
    ("Pendapatan Simpan Pinjam", "Pendapatan", "Kredit"),
    ("Pendapatan Usaha Tani", "Pendapatan", "Kredit"),
    ("Pendapatan Wisata", "Pendapatan", "Kredit"),
    ("Pendapatan Lainnya", "Pendapatan", "Kredit"),
    ("Pembelian Barang Dagang", "HPP", "Debit"),
    ("Beban Produksi", "HPP", "Debit"),
    ("Beban Pemeliharaan Usaha", "HPP", "Debit"),
    ("Beban Penyusutan Aset Usaha", "HPP", "Debit"),
    ("Bahan Baku / Operasional", "HPP", "Debit"),
    ("Beban Lainnya", "HPP", "Debit"),
    ("Gaji dan Tunjangan", "Beban Usaha", "Debit"),
    ("Listrik, Air, Komunikasi", "Beban Usaha", "Debit"),
    ("Transportasi", "Beban Usaha", "Debit"),
    ("Administrasi & Umum", "Beban Usaha", "Debit"),
    ("Sewa Tempat", "Beban Usaha", "Debit"),
    ("Perlengkapan", "Beban Usaha", "Debit"),
    ("Penyusutan Aset Tetap", "Beban Usaha", "Debit"),
    ("Penyuluhan", "Beban Usaha", "Debit"),
    ("Promosi & Publikasi", "Beban Usaha", "Debit"),
    ("Operasional Wisata", "Beban Usaha", "Debit"),
    ("CSR / Kegiatan Desa", "Beban Usaha", "Debit"),
    ("Pendapatan Bunga", "Non-Usaha", "Kredit"),
    ("Pendapatan Investasi", "Non-Usaha", "Kredit"),
    ("Pendapatan Lain-lain", "Non-Usaha", "Kredit"),
    ("Beban Bunga", "Non-Usaha", "Debit"),
    ("Kerugian Penjualan Aset", "Non-Usaha", "Debit"),
    ("Pajak", "Non-Usaha", "Debit"),
    ("Kas", "Aset Lancar", "Debit"),
    ("Bank", "Aset Lancar", "Debit"),
    ("Piutang Usaha", "Aset Lancar", "Debit"),
    ("Persediaan Dagang", "Aset Lancar", "Debit"),
    ("Persediaan Bahan Baku", "Aset Lancar", "Debit"),
    ("Uang Muka", "Aset Lancar", "Debit"),
    ("Investasi Pendek", "Aset Lancar", "Debit"),
    ("Pendapatan Diterima di Muka", "Aset Lancar", "Kredit"),
    ("Tanah", "Aset Tetap", "Debit"),
    ("Bangunan", "Aset Tetap", "Debit"),
    ("Peralatan", "Aset Tetap", "Debit"),
    ("Kendaraan", "Aset Tetap", "Debit"),
    ("Inventaris", "Aset Tetap", "Debit"),
    ("Aset Tetap Lainnya", "Aset Tetap", "Debit"),
    ("Akumulasi Penyusutan", "Aset Tetap", "Kredit"),
    ("Investasi Panjang", "Aset Tetap", "Debit"),
    ("Aset Lain-lain", "Aset Tetap", "Debit"),
    ("Utang Usaha", "Kewajiban Pendek", "Kredit"),
    ("Utang Gaji", "Kewajiban Pendek", "Kredit"),
    ("Utang Pajak", "Kewajiban Pendek", "Kredit"),
    ("Pendapatan Diterima Di Muka", "Kewajiban Pendek", "Kredit"),
    ("Utang Lain-lain", "Kewajiban Pendek", "Kredit"),
    ("Pinjaman Bank", "Kewajiban Panjang", "Kredit"),
    ("Pinjaman Pemerintah", "Kewajiban Panjang", "Kredit"),
    ("Utang Pihak Ketiga", "Kewajiban Panjang", "Kredit"),
    ("Modal Desa", "Ekuitas", "Kredit"),
    ("Modal Pihak Ketiga", "Ekuitas", "Kredit"),
    ("Saldo Laba Ditahan", "Ekuitas", "Kredit"),
    ("Laba Tahun Berjalan", "Ekuitas", "Kredit"),
    ("Cadangan Sosial / Investasi", "Ekuitas", "Kredit"),
]

pedoman_akun = pd.DataFrame(akun_data, columns=["Nama Akun", "Posisi", "Tipe"])

with st.expander("📚 Pedoman Daftar Akun (Manual)"):
    st.dataframe(pedoman_akun, use_container_width=True)
# === INISIALISASI ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Nama Akun", "Debit", "Kredit", "Keterangan"])

df_gl = st.session_state[key_gl]

# === FORM INPUT JURNAL ===
with st.form("Input Transaksi"):
    tanggal = st.date_input("Tanggal", value=datetime.today())
    akun_nama = st.selectbox("Pilih Nama Akun", pedoman_akun["Nama Akun"])
    posisi = pedoman_akun.loc[pedoman_akun["Nama Akun"] == akun_nama, "Posisi"].values[0]
    jumlah = st.number_input("Jumlah (Rp)", 0.0, step=1000.0)
    keterangan = st.text_input("Keterangan")
    submit = st.form_submit_button("➕ Tambah Transaksi")

    if submit:
        debit = jumlah if posisi == "Debit" else 0.0
        kredit = jumlah if posisi == "Kredit" else 0.0
        new_row = pd.DataFrame([[tanggal, akun_nama, debit, kredit, keterangan]],
                                columns=["Tanggal", "Nama Akun", "Debit", "Kredit", "Keterangan"])
        st.session_state[key_gl] = pd.concat([st.session_state[key_gl], new_row], ignore_index=True)
        st.experimental_rerun()

# === TABEL JURNAL ===
st.markdown("### 📖 Jurnal Harian (General Ledger)")
if not df_gl.empty:
    for i, row in df_gl.iterrows():
        st.write(f"{row['Tanggal']} | {row['Nama Akun']} | Rp {row['Debit']:,.0f} (D) | Rp {row['Kredit']:,.0f} (K) | {row['Keterangan']}")
        if st.button(f"Hapus", key=f"hapus_{i}"):
            st.session_state[key_gl] = df_gl.drop(index=i).reset_index(drop=True)
            st.experimental_rerun()
else:
    st.info("Belum ada transaksi dimasukkan.")

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

st.success("✅ Siap ditambahkan: Laba Rugi, Neraca, dan Arus Kas otomatis dalam format tabel bergaris. Konfirmasi untuk lanjut.")
