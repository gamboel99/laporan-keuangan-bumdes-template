import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import os
import io

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

st.title(f"📘 Buku Besar ({lembaga})")

# === LOGO ===
col_logo1, col_logo2 = st.columns([1, 6])
with col_logo1:
    if os.path.exists("logo_pemdes.png"):
        st.image("logo_pemdes.png", width=80)
with col_logo2:
    if os.path.exists("logo_bumdes.png"):
        st.image("logo_bumdes.png", width=80)

# === TAMPILKAN DAFTAR AKUN ===
st.subheader("📖 Daftar Kode Akun")
kode_akun_df = pd.DataFrame([
    {"Kode": "4-100", "Akun": "Pendapatan Usaha", "Posisi": "Laba Rugi", "Tipe": "Kredit"},
    {"Kode": "5-100", "Akun": "Beban Operasional", "Posisi": "Laba Rugi", "Tipe": "Debit"},
    {"Kode": "3-100", "Akun": "Modal Awal", "Posisi": "Perubahan Ekuitas", "Tipe": "Kredit"},
    {"Kode": "3-200", "Akun": "Penambahan Modal", "Posisi": "Perubahan Ekuitas", "Tipe": "Kredit"},
    {"Kode": "3-300", "Akun": "Prive", "Posisi": "Perubahan Ekuitas", "Tipe": "Debit"},
    {"Kode": "1-100", "Akun": "Kas", "Posisi": "Neraca", "Tipe": "Debit"},
    {"Kode": "1-200", "Akun": "Piutang", "Posisi": "Neraca", "Tipe": "Debit"},
    {"Kode": "1-300", "Akun": "Peralatan", "Posisi": "Neraca", "Tipe": "Debit"},
    {"Kode": "2-100", "Akun": "Utang", "Posisi": "Neraca", "Tipe": "Kredit"},
])
st.dataframe(kode_akun_df, use_container_width=True)

# === INISIALISASI ===
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode Akun", "Akun", "Debit", "Kredit", "Keterangan", "Bukti"])

# === FORM TAMBAH TRANSAKSI ===
with st.expander("➕ Tambah Transaksi"):
    col1, col2, col3 = st.columns(3)
    with col1:
        tanggal = st.date_input("Tanggal", datetime.today())
    with col2:
        kode_akun = st.selectbox("Kode Akun", kode_akun_df["Kode"])
    with col3:
        keterangan = st.text_input("Keterangan")

    akun_row = kode_akun_df[kode_akun_df["Kode"] == kode_akun].iloc[0]
    akun = akun_row["Akun"]

    col4, col5, col6 = st.columns(3)
    with col4:
        debit = st.number_input("Debit", min_value=0.0, format="%.2f")
    with col5:
        kredit = st.number_input("Kredit", min_value=0.0, format="%.2f")
    with col6:
        bukti_file = st.file_uploader("Upload Nota/Bukti", type=["png", "jpg", "jpeg", "pdf"])

    if st.button("💾 Simpan Transaksi"):
        if akun and (debit > 0 or kredit > 0):
            if bukti_file:
                bukti_path = f"bukti_{datetime.now().strftime('%Y%m%d%H%M%S')}_{bukti_file.name}"
                with open(bukti_path, "wb") as f:
                    f.write(bukti_file.read())
            else:
                bukti_path = ""
            new_row = pd.DataFrame([{
                "Tanggal": tanggal.strftime("%Y-%m-%d"),
                "Kode Akun": kode_akun,
                "Akun": akun,
                "Debit": debit,
                "Kredit": kredit,
                "Keterangan": keterangan,
                "Bukti": bukti_path
            }])
            st.session_state[key_gl] = pd.concat([st.session_state[key_gl], new_row], ignore_index=True)
            st.success("✅ Transaksi berhasil disimpan.")
        else:
            st.warning("⚠️ Lengkapi akun dan nilai debit/kredit.")

# === TAMPILKAN GL ===
st.subheader("📋 Daftar Transaksi")
gl_df = st.session_state[key_gl].copy()
if not gl_df.empty:
    for i in gl_df.index:
        row = gl_df.loc[i]
        st.write(f"{row['Tanggal']} | {row['Kode Akun']} - {row['Akun']} | Debit: Rp{row['Debit']}, Kredit: Rp{row['Kredit']}")
        st.caption(row['Keterangan'])
        if row['Bukti'] and os.path.exists(row['Bukti']):
            if row['Bukti'].endswith(".pdf"):
                st.markdown(f"[📄 Lihat Bukti PDF]({row['Bukti']})")
            else:
                st.image(row['Bukti'], width=200)
        if st.button(f"❌ Hapus", key=f"hapus_{i}"):
            st.session_state[key_gl] = gl_df.drop(i).reset_index(drop=True)
            st.experimental_rerun()
else:
    st.info("Belum ada transaksi.")

# === UNDUH GL EXCEL ===
def download_excel(df, filename):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='GL')
    data = output.getvalue()
    b64 = base64.b64encode(data).decode()
    href = f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}' download='{filename}'>📤 Download Buku Besar (Excel)</a>"
    return href

st.markdown(download_excel(gl_df, f"General_Ledger_{lembaga}_{desa}_{tahun}.xlsx"), unsafe_allow_html=True)
)
