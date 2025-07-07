import streamlit as st
import pandas as pd
import base64
from datetime import datetime
from io import BytesIO
import os

st.set_page_config(page_title="Laporan Keuangan BUMDes", layout="wide")

# ---------------------------
# 1. SIDEBAR – Identitas & Pejabat
# ---------------------------
st.sidebar.title("🔰 Unit Lembaga")
lembaga = st.sidebar.selectbox("Lembaga", ["BUMDes", "PKK", "Karang Taruna", "LPMD", "BPD"], index=0)
desa = st.sidebar.text_input("Nama Desa", "Keling")
nama_bumdes = st.sidebar.text_input("Nama Lembaga", "BUMDes Buwana Raharja")
tahun = st.sidebar.number_input("Tahun Laporan", 2025, step=1)

st.sidebar.markdown("---")
st.sidebar.subheader("Pejabat Tanda Tangan")
bendahara = st.sidebar.text_input("Bendahara", "Siti Aminah")
direktur = st.sidebar.text_input("Pimpinan", "Bambang Setiawan")
kepala_desa = st.sidebar.text_input("Kepala Desa", "Sugeng Riyadi")
ketua_bpd = st.sidebar.text_input("Ketua BPD", "Dwi Purnomo")

# ---------------------------
# 2. LOGO (Opsional)
# ---------------------------
col_l1, col_l2 = st.columns([1, 6])
with col_l1:
    if os.path.exists("logo_pemdes.png"):
        st.image("logo_pemdes.png", width=90)
with col_l2:
    if os.path.exists("logo_bumdes.png"):
        st.image("logo_bumdes.png", width=90)

# ---------------------------
# 3. KOP LAPORAN
# ---------------------------
st.markdown(f"""
<div style='text-align:center;'>
    <h2>LAPORAN KEUANGAN {nama_bumdes.upper()}</h2>
    <h3>DESA {desa.upper()}</h3>
    <p>Alamat: Jl. Raya Keling, Bukaan, Keling, Kec. Kepung, Kabupaten Kediri, Jawa Timur 64293</p>
</div><hr>
""", unsafe_allow_html=True)

# ---------------------------
# 4. CHART OF ACCOUNTS (PSAK sederhana)
# ---------------------------
coa = pd.DataFrame([
    # Pendapatan
    ["4-100", "Pendapatan Usaha", "Pendapatan", "LR"],
    ["4-200", "Pendapatan Lain", "Pendapatan", "LR"],
    # Beban
    ["5-100", "Beban Operasional", "Beban", "LR"],
    ["5-200", "Beban Penyusutan", "Beban", "LR"],
    # Aset Lancar
    ["1-100", "Kas", "Aset Lancar", "NER"],
    ["1-110", "Bank", "Aset Lancar", "NER"],
    ["1-120", "Piutang Usaha", "Aset Lancar", "NER"],
    # Aset Tetap
    ["1-300", "Peralatan", "Aset Tetap", "NER"],
    # Kewajiban
    ["2-100", "Utang Usaha", "Kewajiban", "NER"],
    # Ekuitas
    ["3-100", "Modal Awal", "Ekuitas", "EQ"],
    ["3-200", "Penambahan Modal", "Ekuitas", "EQ"],
    ["3-300", "Prive", "Ekuitas", "EQ"],
])
coa.columns = ["Kode", "Akun", "Kategori", "Report"]

st.markdown("### 🗂️ Daftar Akun (COA)")
st.dataframe(coa, use_container_width=True)

# ---------------------------
# 5. SESSION STATE – General Ledger
# ---------------------------
key_gl = f"gl_{lembaga}_{desa}_{tahun}"
if key_gl not in st.session_state:
    st.session_state[key_gl] = pd.DataFrame(columns=["Tanggal", "Kode", "Akun", "Kategori", "Debit", "Kredit", "Keterangan"])

df_gl = st.session_state[key_gl]

# ---------------------------
# 6. FORM INPUT TRANSAKSI
# ---------------------------
with st.expander("➕ Tambah Transaksi"):
    c1, c2, c3 = st.columns(3)
    with c1:
        tgl = st.date_input("Tanggal", datetime.today())
    with c2:
        kode = st.selectbox("Kode Akun", coa["Kode"])
    with c3:
        baris = coa[coa["Kode"] == kode].iloc[0]
        akun = baris["Akun"]
        kategori = baris["Kategori"]
        pos_default = "Debit" if kategori in ["Aset Lancar", "Aset Tetap", "Beban"] else "Kredit"

    c4, c5 = st.columns(2)
    with c4:
        debit = st.number_input("Debit", min_value=0.0) if pos_default == "Debit" else 0.0
    with c5:
        kredit = st.number_input("Kredit", min_value=0.0) if pos_default == "Kredit" else 0.0

    ket = st.text_input("Keterangan")
    if st.button("💾 Simpan"):
        df_gl.loc[len(df_gl)] = [tgl.strftime("%Y-%m-%d"), kode, akun, kategori, debit, kredit, ket]
        st.success("Transaksi tersimpan")

# ---------------------------
# 7. TAMPILKAN GL + UNDUH EXCEL
# ---------------------------
st.markdown("### 📋 General Ledger")
if df_gl.empty:
    st.warning("Belum ada transaksi")
else:
    st.dataframe(df_gl, use_container_width=True)

    # ===== download excel =====
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_gl.to_excel(writer, index=False, sheet_name="GL")
    b64 = base64.b64encode(buffer.getvalue()).decode()
    st.markdown(f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}' download='GL_{tahun}.xlsx'>📥 Download GL (Excel)</a>", unsafe_allow_html=True)

# ---------------------------
# 8. RUMUS KONVERSI OTOMATIS
# ---------------------------
pendapatan = df_gl[df_gl["Kategori"] == "Pendapatan"]["Kredit"].sum() - df_gl[df_gl["Kategori"] == "Pendapatan"]["Debit"].sum()
beban = df_gl[df_gl["Kategori"] == "Beban"]["Debit"].sum() - df_gl[df_gl["Kategori"] == "Beban"]["Kredit"].sum()
laba_bersih = pendapatan - beban

# Neraca
aset_lancar = df_gl[df_gl["Kategori"] == "Aset Lancar"]["Debit"].sum() - df_gl[df_gl["Kategori"] == "Aset Lancar"]["Kredit"].sum()
aset_tetap = df_gl[df_gl["Kategori"] == "Aset Tetap"]["Debit"].sum() - df_gl[df_gl["Kategori"] == "Aset Tetap"]["Kredit"].sum()
utang = df_gl[df_gl["Kategori"] == "Kewajiban"]["Kredit"].sum() - df_gl[df_gl["Kategori"] == "Kewajiban"]["Debit"].sum()
modal_awal = df_gl[df_gl["Akun"] == "Modal Awal"]["Kredit"].sum()
penambahan_modal = df_gl[df_gl["Akun"] == "Penambahan Modal"]["Kredit"].sum()
prive = df_gl[df_gl["Akun"] == "Prive"]["Debit"].sum()
modal_akhir = modal_awal + penambahan_modal - prive + laba_bersih

# ---------------------------
# 9. LAPORAN LABA RUGI DETAIL
# ---------------------------
st.markdown("### 📑 Laporan Laba Rugi")
if df_gl.empty:
    st.info("Belum ada data")
else:
    lr = (
        df_gl[df_gl["Kategori"].isin(["Pendapatan", "Beban"])]
        .groupby(["Kode", "Akun", "Kategori"]).sum()[["Debit", "Kredit"]]
        .reset_index()
    )
    lr["Saldo"] = lr.apply(lambda r: r["Kredit"]-r["Debit"] if r["Kategori"]=="Pendapatan" else r["Debit"]-r["Kredit"], axis=1)
    st.dataframe(lr[["Kode", "Akun", "Saldo"]], use_container_width=True)

    # download LR
    buf_lr = BytesIO()
    with pd.ExcelWriter(buf_lr, engine="xlsxwriter") as w:
        lr.to_excel(w, index=False, sheet_name="LabaRugi")
    b64lr = base64.b64encode(buf_lr.getvalue()).decode()
    st.markdown(f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64lr}' download='LR_{tahun}.xlsx'>📋 Download LR (Excel)</a>", unsafe_allow_html=True)

# ---------------------------
# 10. LAPORAN NERACA DETAIL
# ---------------------------
st.markdown("### 📊 Neraca")
if not df_gl.empty:
    neraca = pd.DataFrame({
        "Posisi": ["Aset Lancar", "Aset Tetap", "Total Aset", "Kewajiban", "Ekuitas"],
        "Jumlah": [aset_lancar, aset_tetap, aset_lancar+aset_tetap, utang, modal_akhir]
    })
    st.dataframe(neraca, use_container_width=True)
    buf_ne = BytesIO()
    with pd.ExcelWriter(buf_ne, engine="xlsxwriter") as w:
        neraca.to_excel(w, index=False, sheet_name="Neraca")
    st.markdown(f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(buf_ne.getvalue()).decode()}' download='Neraca_{tahun}.xlsx'>📊 Download Neraca (Excel)</a>", unsafe_allow_html=True)

# ---------------------------
# 11. LAPORAN PERUBAHAN EKUITAS
# ---------------------------
st.markdown("### 🧾 Perubahan Ekuitas")
if not df_gl.empty:
    ek = pd.DataFrame({
        "Keterangan": ["Modal Awal", "Penambahan Modal", "Laba Bersih", "Prive", "Modal Akhir"],
        "Jumlah": [modal_awal, penambahan_modal, laba_bersih, prive, modal_akhir]
    })
    st.dataframe(ek, use_container_width=True)
    buf_eq = BytesIO()
    with pd.ExcelWriter(buf_eq, engine="xlsxwriter") as w:
        ek.to_excel(w, index=False, sheet_name="Ekuitas")
    st.markdown(
    f"<a href='data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(buf_eq.getvalue()).decode()}' download='Ekuitas_{tahun}.xlsx'>🧾 Download Ekuitas (Excel)</a>",
    unsafe_allow_html=True
)
