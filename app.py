import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import os
from io import BytesIO

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# === PILIHAN MULTI LEMBAGA DAN DESA ===
st.sidebar.title("🔰 Pilih Unit Lembaga")
lembaga = st.sidebar.selectbox("Lembaga", ["BUMDes", "PKK", "Karang Taruna", "LPMD", "BPD"])
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
st.markdown("""
    <h3 style='text-align:center;'>Laporan Keuangan BUMDes Buwana Raharja Desa Keling</h3>
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

# === DAFTAR AKUN ===
daftar_akun = pd.DataFrame({
    "Kode Akun": ["4.1", "5.1", "3.1", "3.2", "1.1", "2.1", "1.2"],
    "Nama Akun": ["Pendapatan Usaha", "Beban Operasional", "Modal Awal", "Prive", "Kas", "Utang", "Piutang"],
    "Posisi": ["Laba Rugi", "Laba Rugi", "Ekuitas", "Ekuitas", "Neraca", "Neraca", "Neraca"],
    "Tipe": ["Kredit", "Debit", "Kredit", "Debit", "Debit", "Kredit", "Debit"]
})

with st.expander("📚 Daftar Akun Standar"):
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

# === LAPORAN OTOMATIS ===
st.header("📑 Laporan Keuangan Otomatis")

# Fungsi total
def total_akun(kode):
    df = st.session_state[key_gl]
    debit = df[df['Kode Akun'] == kode]['Debit'].sum()
    kredit = df[df['Kode Akun'] == kode]['Kredit'].sum()
    return kredit - debit if daftar_akun.loc[daftar_akun['Kode Akun'] == kode, 'Tipe'].values[0] == 'Kredit' else debit - kredit

# Laba Rugi
pendapatan = total_akun("4.1")
beban = total_akun("5.1")
laba = pendapatan - beban

# Ekuitas
modal_awal = total_akun("3.1")
prive = total_akun("3.2")
modal_akhir = modal_awal + laba - prive

# Neraca
kas = total_akun("1.1")
piutang = total_akun("1.2")
utang = total_akun("2.1")
aset = kas + piutang
kewajiban_ekuitas = utang + modal_akhir

col1, col2 = st.columns(2)
with col1:
    st.subheader("📄 Laba Rugi")
    st.write(f"**Pendapatan Usaha:** Rp {pendapatan:,.2f}")
    st.write(f"**Beban Operasional:** Rp {beban:,.2f}")
    st.write(f"**Laba Bersih:** Rp {laba:,.2f}")

    st.subheader("📈 Ekuitas")
    st.write(f"**Modal Awal:** Rp {modal_awal:,.2f}")
    st.write(f"**Prive:** Rp {prive:,.2f}")
    st.write(f"**Laba Ditahan:** Rp {laba:,.2f}")
    st.write(f"**Modal Akhir:** Rp {modal_akhir:,.2f}")

with col2:
    st.subheader("💰 Neraca")
    st.write(f"**Kas:** Rp {kas:,.2f}")
    st.write(f"**Piutang:** Rp {piutang:,.2f}")
    st.write(f"**Total Aset:** Rp {aset:,.2f}")
    st.write(f"**Utang:** Rp {utang:,.2f}")
    st.write(f"**Ekuitas:** Rp {modal_akhir:,.2f}")
    st.write(f"**Total Kewajiban + Ekuitas:** Rp {kewajiban_ekuitas:,.2f}")

# === EKSPOR EXCEL PER LAPORAN ===
def ekspor_excel(data, judul):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame(data.items(), columns=["Uraian", "Jumlah"])
        df.to_excel(writer, index=False, sheet_name=judul)
    b64 = base64.b64encode(output.getvalue()).decode()
    return f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}' download='{judul}_{tahun}.xlsx'>⬇️ Download {judul}</a>"

st.markdown("### 📥 Ekspor Excel per Laporan")
st.markdown(ekspor_excel({"Pendapatan Usaha": pendapatan, "Beban Operasional": beban, "Laba Bersih": laba}, "LabaRugi"), unsafe_allow_html=True)
st.markdown(ekspor_excel({"Modal Awal": modal_awal, "Prive": prive, "Laba Ditahan": laba, "Modal Akhir": modal_akhir}, "Ekuitas"), unsafe_allow_html=True)
st.markdown(ekspor_excel({"Kas": kas, "Piutang": piutang, "Total Aset": aset, "Utang": utang, "Ekuitas": modal_akhir, "Total Kewajiban + Ekuitas": kewajiban_ekuitas}, "Neraca"), unsafe_allow_html=True)

# === PENGESAHAN ===
st.markdown("""
    <br><br>
    <h4 style='text-align:center;'>LEMBAR PENGESAHAN</h4>
    <table style='width:100%; text-align:center;'>
    <tr>
        <td>Bendahara<br><br><br><br>({bendahara})</td>
        <td>Direktur/Pimpinan<br><br><br><br>({direktur})</td>
    </tr>
    <tr>
        <td colspan='2'><br></td>
    </tr>
    <tr>
        <td>Mengetahui,<br>Kepala Desa<br><br><br>({kepala_desa})</td>
        <td>Ketua BPD<br><br><br><br>({ketua_bpd})</td>
    </tr>
    </table>
""", unsafe_allow_html=True)

# === SELESAI ===
st.success("✅ Laporan Keuangan lengkap. Siap diekspor dan dicetak.")
