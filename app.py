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
pedoman_akun = pd.DataFrame({
    "Nama Akun": [
        "Penjualan Barang Dagang", "Pendapatan Jasa", "Pendapatan Sewa Aset", "Pendapatan Simpan Pinjam", "Pendapatan Usaha Tani", "Pendapatan Wisata", "Pendapatan Lainnya",
        "Pembelian Barang Dagang", "Beban Produksi", "Beban Pemeliharaan Usaha", "Beban Penyusutan Aset Usaha", "Bahan Baku / Operasional", "Beban Lainnya",
        "Gaji dan Tunjangan", "Listrik, Air, Komunikasi", "Transportasi", "Administrasi & Umum", "Sewa Tempat", "Perlengkapan", "Penyusutan Aset Tetap", "Penyuluhan", "Promosi & Publikasi", "Operasional Wisata", "CSR / Kegiatan Desa",
        "Pendapatan Bunga", "Pendapatan Investasi", "Pendapatan Lain-lain", "Beban Bunga", "Kerugian Penjualan Aset", "Pajak",
        "Kas", "Bank", "Piutang Usaha", "Persediaan Dagang", "Persediaan Bahan Baku", "Uang Muka", "Investasi Pendek", "Pendapatan Diterima Di Muka",
        "Tanah", "Bangunan", "Peralatan", "Kendaraan", "Inventaris", "Aset Tetap Lainnya", "Akumulasi Penyusutan", "Investasi Panjang", "Aset Lain-lain",
        "Utang Usaha", "Utang Gaji", "Utang Pajak", "Pendapatan Diterima Di Muka", "Utang Lain-lain",
        "Pinjaman Bank", "Pinjaman Pemerintah", "Utang Pihak Ketiga",
        "Modal Desa", "Modal Pihak Ketiga", "Saldo Laba Ditahan", "Laba Tahun Berjalan", "Cadangan Sosial / Investasi"
    ],
    "Posisi": [
        "Kredit"]*7 + ["Debit"]*6 + ["Debit"]*11 + ["Kredit"]*3 + ["Debit"]*8 + ["Debit"]*9 + ["Kredit"]*5 + ["Kredit"]*3 + ["Kredit"]*5
})

with st.expander("📚 Pedoman Akun - Posisi Debit/Kredit"):
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
