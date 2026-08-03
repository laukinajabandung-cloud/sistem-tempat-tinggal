import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client
import plotly.express as px
import io

# -------------------------------------------------------------
# KONFIGURASI HALAMAN & THEME ELEGANT
# -------------------------------------------------------------
st.set_page_config(
    page_title="Sistem Tempat Tinggal - Insan Madani", 
    page_icon="🏠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .metric-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e9ecef;
        text-align: center;
    }
    .metric-card h4 { color: #6c757d; font-size: 13px; margin-bottom: 8px; font-weight: 500; }
    .metric-card h2 { color: #1e293b; font-size: 22px; font-weight: bold; margin: 0; }
    .header-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white; padding: 24px; border-radius: 12px; margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .header-box h1 { margin: 0; font-size: 26px; font-weight: 700; color: #ffffff; }
    .header-box p { margin: 5px 0 0 0; color: #94a3b8; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# KONEKSI SUPABASE
# -------------------------------------------------------------
SUPABASE_URL = "https://lqczctceamyvzdgtnfdi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxxY3pjdGNlYW15dnpkZ3RuZmRpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc3MzYyMDgsImV4cCI6MjA5MzMxMjIwOH0.G7WVQV6OjAHLP1ecGCjKfcOml-XECQXrAOPDOWR-Muc"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# -------------------------------------------------------------
# FUNGSI AMBIL DATA
# -------------------------------------------------------------
def load_pegawai():
    res = supabase.table('master_pegawai').select('id, nipy, nama, jabatan, unit_kerja, no_hp, email, status_kepegawaian').execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=['id', 'nipy', 'nama', 'jabatan', 'unit_kerja', 'no_hp', 'email', 'status_kepegawaian'])

def load_rekap():
    res = supabase.table('rekap_tempat_tinggal').select('id, kode, nama, jenis, status, alamat, pic, penghuni, kondisi, prioritas, biaya_sewa_tahun, subsidi_yayasan').execute()
    df = pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=['id', 'kode', 'nama', 'jenis', 'status', 'alamat', 'pic', 'penghuni', 'kondisi', 'prioritas', 'biaya_sewa_tahun', 'subsidi_yayasan'])
    
    # Isi NaN dengan 0
    if not df.empty:
        df['biaya_sewa_tahun'] = df['biaya_sewa_tahun'].fillna(0)
        df['subsidi_yayasan'] = df['subsidi_yayasan'].fillna(0)
        df['sisa_tanggungan_pegawai'] = df['biaya_sewa_tahun'] - df['subsidi_yayasan']
        df['sisa_tanggungan_pegawai'] = df['sisa_tanggungan_pegawai'].apply(lambda x: max(x, 0))
    return df

def load_penghuni():
    res = supabase.table('data_penghuni').select('id, kode_rumah, nama, status, jabatan, unit, no_hp, mulai_menempati').execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=['id', 'kode_rumah', 'nama', 'status', 'jabatan', 'unit', 'no_hp', 'mulai_menempati'])

def load_inventaris():
    res = supabase.table('inventaris_aset').select('id, kode_rumah, barang, jumlah, kondisi, catatan').execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=['id', 'kode_rumah', 'barang', 'jumlah', 'kondisi', 'catatan'])

def load_maintenance():
    res = supabase.table('maintenance_log').select('id, tanggal, kode_rumah, jenis_perbaikan, biaya, vendor, pic, status').execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=['id', 'tanggal', 'kode_rumah', 'jenis_perbaikan', 'biaya', 'vendor', 'pic', 'status'])

# Load Data
df_pegawai = load_pegawai()
df_rekap = load_rekap()
df_penghuni = load_penghuni()
df_inventaris = load_inventaris()
df_maint = load_maintenance()

# Header Banner
st.markdown("""
    <div class="header-box">
        <h1>🏠 Sistem Manajemen Tempat Tinggal Insan Madani</h1>
        <p>Platform Monitoring Pegawai, Aset, Penghuni, Subsidi Sewa, dan Maintenance Terintegrasi</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Menu Navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/609/609803.png", width=70)
    st.title("Menu Utama")
    menu = st.radio("", [
        "📊 Dashboard & Grafik Analisis", 
        "👨‍💼 Daftar Pegawai / Insan Madani",
        "📝 Form Sensus Baru", 
        "🏢 Rekap Tempat Tinggal & Subsidi", 
        "👥 Data Penghuni", 
        "📦 Inventaris Aset", 
        "🛠️ Maintenance / Perbaikan",
        "📥 Ekspor Excel Laporan"
    ])

# -------------------------------------------------------------
# 1. DASHBOARD & GRAFIK ANALISIS
# -------------------------------------------------------------
if menu == "📊 Dashboard & Grafik Analisis":
    col1, col2, col3, col4, col5 = st.columns(5)
    
    tot_peg = len(df_pegawai)
    tot_tt = len(df_rekap)
    tot_penghuni = int(df_rekap["penghuni"].sum()) if not df_rekap.empty and 'penghuni' in df_rekap else 0
    tot_subsidi = df_rekap["subsidi_yayasan"].sum() if not df_rekap.empty and 'subsidi_yayasan' in df_rekap else 0
    tot_biaya_maint = df_maint["biaya"].sum() if not df_maint.empty and 'biaya' in df_maint else 0

    col1.markdown(f'<div class="metric-card"><h4>Total Pegawai</h4><h2>{tot_peg} Staf</h2></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card"><h4>Tempat Tinggal</h4><h2>{tot_tt} Unit</h2></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-card"><h4>Total Penghuni</h4><h2>{tot_penghuni} Jiwa</h2></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="metric-card"><h4>Total Subsidi Sewa</h4><h2>Rp {tot_subsidi:,.0f}</h2></div>', unsafe_allow_html=True)
    col5.markdown(f'<div class="metric-card"><h4>Biaya Maintenance</h4><h2>Rp {tot_biaya_maint:,.0f}</h2></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📈 Analisis Data & Visualisasi")
    
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.markdown("##### 🏢 Kondisi Fisik Tempat Tinggal")
        if not df_rekap.empty and 'kondisi' in df_rekap:
            kondisi_counts = df_rekap['kondisi'].value_counts().reset_index()
            kondisi_counts.columns = ['Kondisi', 'Jumlah']
            fig_kondisi = px.bar(kondisi_counts, x='Kondisi', y='Jumlah', color='Kondisi', 
                                 color_discrete_map={'Baik': '#10b981', 'Perlu Perbaikan': '#f59e0b', 'Perlu Renovasi': '#ef4444'}, text_auto=True)
            fig_kondisi.update_layout(showlegend=False, height=350, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_kondisi, use_container_width=True)
        else:
            st.info("Belum ada data tempat tinggal.")

    with g_col2:
        st.markdown("##### 🏘️ Distribusi Jenis Tempat Tinggal")
        if not df_rekap.empty and 'jenis' in df_rekap:
            jenis_counts = df_rekap['jenis'].value_counts().reset_index()
            jenis_counts.columns = ['Jenis', 'Jumlah']
            fig_jenis = px.pie(jenis_counts, names='Jenis', values='Jumlah', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_jenis.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_jenis, use_container_width=True)
        else:
            st.info("Belum ada data tempat tinggal.")

    st.markdown("---")
    g_col3, g_col4 = st.columns(2)

    with g_col3:
        st.markdown("##### 📦 Status Kondisi Aset Inventaris")
        if not df_inventaris.empty and 'kondisi' in df_inventaris:
            inv_counts = df_inventaris['kondisi'].value_counts().reset_index()
            inv_counts.columns = ['Kondisi', 'Jumlah']
            fig_inv = px.bar(
                inv_counts, x='Jumlah', y='Kondisi', orientation='h',
                color='Kondisi',
                color_discrete_map={'Baik': '#3b82f6', 'Rusak Ringan': '#f59e0b', 'Rusak Berat': '#ef4444'},
                text_auto=True
            )
            fig_inv.update_layout(showlegend=False, height=320, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_inv, use_container_width=True)
        else:
            st.info("Belum ada data inventaris.")

    with g_col4:
        st.markdown("##### 🛠️ Status Progress Maintenance")
        if not df_maint.empty and 'status' in df_maint:
            maint_counts = df_maint['status'].value_counts().reset_index()
            maint_counts.columns = ['Status', 'Jumlah']
            fig_maint = px.pie(
                maint_counts, names='Status', values='Jumlah',
                color_discrete_sequence=['#f59e0b', '#06b6d4', '#10b981']
            )
            fig_maint.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_maint, use_container_width=True)
        else:
            st.info("Belum ada data maintenance.")

# -------------------------------------------------------------
# 2. DAFTAR PEGAWAI / INSAN MADANI (PENGGUNAAN NIPY)
# -------------------------------------------------------------
elif menu == "👨‍💼 Daftar Pegawai / Insan Madani":
    st.subheader("👨‍💼 Master Data Pegawai Insan Madani")
    
    t1, t2, t3 = st.tabs(["📋 Daftar Pegawai", "➕ Input Manual", "📥 Import dari Excel"])
    
    # Tab 1: Daftar Pegawai
    with t1:
        st.dataframe(df_pegawai, use_container_width=True, hide_index=True)
        
    # Tab 2: Input Manual
    with t2:
        with st.form("f_pegawai", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nipy = c1.text_input("NIPY (Nomor Induk Pegawai Yayasan)")
            nama_p = c2.text_input("Nama Lengkap Pegawai")
            
            c3, c4, c5 = st.columns(3)
            jabatan = c3.text_input("Jabatan")
            unit = c4.text_input("Unit Kerja / Lembaga")
            status_k = c5.selectbox("Status Kepegawaian", ["Tetap", "Kontrak", "Guru/Pengajar", "Magang", "Lainnya"])
            
            c6, c7 = st.columns(2)
            hp = c6.text_input("No. HP / WhatsApp")
            email = c7.text_input("Alamat Email")
            
            sub_p = st.form_submit_button("💾 Simpan Data Pegawai", use_container_width=True)
            if sub_p:
                if nama_p:
                    data_peg = {"nipy": nipy, "nama": nama_p, "jabatan": jabatan, "unit_kerja": unit, "no_hp": hp, "email": email, "status_kepegawaian": status_k}
                    supabase.table('master_pegawai').insert(data_peg).execute()
                    st.success("✅ Data Pegawai berhasil ditambahkan ke database!")
                    st.rerun()
                else:
                    st.error("⚠️ Nama Pegawai wajib diisi!")

    # Tab 3: Import Excel & Download Template (Menggunakan NIPY)
    with t3:
        st.markdown("##### 1. Unduh Template Excel")
        st.write("Gunakan template standar di bawah ini untuk mengisi data pegawai sebelum diunggah.")
        
        # Buat File Template Excel dengan Header NIPY
        df_template = pd.DataFrame([
            {
                "nipy": "IM-2024-001",
                "nama": "Ahmad Abdullah",
                "jabatan": "Guru Matematika",
                "unit_kerja": "SMA Insan Madani",
                "no_hp": "081234567890",
                "email": "ahmad@insanmadani.sch.id",
                "status_kepegawaian": "Tetap"
            },
            {
                "nipy": "IM-2024-002",
                "nama": "Siti Rahmawati",
                "jabatan": "Staf HRD",
                "unit_kerja": "Yayasan",
                "no_hp": "089876543210",
                "email": "siti@insanmadani.sch.id",
                "status_kepegawaian": "Kontrak"
            }
        ])
        
        output_tmpl = io.BytesIO()
        with pd.ExcelWriter(output_tmpl, engine='openpyxl') as writer:
            df_template.to_excel(writer, sheet_name='Template_Pegawai', index=False)
            
        st.download_button(
            label="📥 Download Template Excel (.xlsx)",
            data=output_tmpl.getvalue(),
            file_name="Template_Data_Pegawai_Insan_Madani.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.markdown("---")
        st.markdown("##### 2. Upload File Excel Data Pegawai")
        uploaded_file = st.file_uploader("Pilih file Excel (.xlsx) yang sudah diisi", type=["xlsx", "xls"])
        
        if uploaded_file is not None:
            try:
                df_upload = pd.read_excel(uploaded_file)
                st.write("🔍 **Preview Data yang Akan Di-import:**")
                st.dataframe(df_upload, use_container_width=True)
                
                # Validation Kolom Wajib (nipy)
                req_cols = ["nipy", "nama", "jabatan", "unit_kerja", "no_hp", "email", "status_kepegawaian"]
                if all(col in df_upload.columns for col in req_cols):
                    if st.button("🚀 Proses Import Data ke Database", use_container_width=True):
                        data_to_insert = df_upload[req_cols].fillna("").to_dict(orient="records")
                        supabase.table('master_pegawai').upsert(data_to_insert).execute()
                        st.success(f"🎉 Berhasil meng-import {len(data_to_insert)} data pegawai ke database!")
                        st.rerun()
                else:
                    st.error(f"⚠️ Kolom dalam file Excel tidak sesuai. Kolom wajib: {', '.join(req_cols)}")
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan saat membaca file Excel: {str(e)}")

# -------------------------------------------------------------
# 3. FORM SENSUS BARU (DENGAN FIELD SUBSIDI)
# -------------------------------------------------------------
elif menu == "📝 Form Sensus Baru":
    st.subheader("📝 Tambah Data Tempat Tinggal Baru")
    
    with st.form("f_sensus", clear_on_submit=True):
        c1, c2 = st.columns(2)
        k = c1.text_input("Kode Rumah (Contoh: IM-SEWA-01)")
        n = c2.text_input("Nama Tempat Tinggal / Alamat Ringkas")
        
        c3, c4 = st.columns(2)
        j = c3.selectbox("Jenis Tempat Tinggal", ["Rumah Sewa", "Rumah Dinas", "Wisma", "Asrama", "Rumah Pribadi"])
        s = c4.selectbox("Status Kepemilikan", ["Sewa", "Milik Sendiri", "Milik Yayasan"])
        
        a = st.text_area("Alamat Lengkap")
        
        st.markdown("---")
        st.markdown("##### 💵 Informasi Biaya Sewa & Subsidi Yayasan (Khusus Rumah Sewa)")
        c_sewa1, c_sewa2 = st.columns(2)
        biaya_sewa = c_sewa1.number_input("Total Biaya Sewa Pertahun (Rp)", min_value=0, value=12000000, step=500000)
        subsidi = c_sewa2.number_input("Subsidi dari Yayasan Pertahun (Rp)", min_value=0, max_value=25000000, value=10000000, step=500000, help="Rekomendasi Subsidi: Rp 8.000.000 - Rp 15.000.000 / tahun")
        
        st.markdown("---")
        c5, c6, c7, c8 = st.columns(4)
        pic = c5.text_input("Nama PIC / Penanggung Jawab")
        p_num = c6.number_input("Kapasitas/Jumlah Penghuni", min_value=0, value=1)
        kon = c7.selectbox("Kondisi Fisik", ["Baik", "Perlu Perbaikan", "Perlu Renovasi"])
        prio = c8.selectbox("Tingkat Prioritas", ["Rendah", "Sedang", "Tinggi"])
        
        sub = st.form_submit_button("💾 Simpan Data Sensus Tempat Tinggal", use_container_width=True)
        if sub and k and n:
            data = {
                "kode": k, "nama": n, "jenis": j, "status": s, "alamat": a, 
                "pic": pic, "penghuni": p_num, "kondisi": kon, "prioritas": prio,
                "biaya_sewa_tahun": biaya_sewa if s == "Sewa" else 0,
                "subsidi_yayasan": subsidi if s == "Sewa" else 0
            }
            supabase.table('rekap_tempat_tinggal').insert(data).execute()
            st.success("✅ Data Tempat Tinggal & Subsidi berhasil disimpan secara permanen!")
            st.rerun()

# -------------------------------------------------------------
# 4. REKAP TEMPAT TINGGAL & SUBSIDI
# -------------------------------------------------------------
elif menu == "🏢 Rekap Tempat Tinggal & Subsidi":
    st.subheader("🏢 Rekap Tempat Tinggal & Rincian Subsidi Sewa")
    
    # Format Tampilan Rupiah untuk Tabel
    df_show = df_rekap.copy()
    if not df_show.empty:
        df_show['biaya_sewa_tahun'] = df_show['biaya_sewa_tahun'].apply(lambda x: f"Rp {x:,.0f}")
        df_show['subsidi_yayasan'] = df_show['subsidi_yayasan'].apply(lambda x: f"Rp {x:,.0f}")
        df_show['sisa_tanggungan_pegawai'] = df_show['sisa_tanggungan_pegawai'].apply(lambda x: f"Rp {x:,.0f}")

    st.dataframe(df_show, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# 5. DATA PENGHUNI
# -------------------------------------------------------------
elif menu == "👥 Data Penghuni":
    st.subheader("👥 Kelola Data Penghuni Tempat Tinggal")
    list_kode = df_rekap["kode"].tolist() if not df_rekap.empty else ["-"]
    list_pegawai = df_pegawai["nama"].tolist() if not df_pegawai.empty else []
    
    with st.expander("➕ Plotting Penghuni Tempat Tinggal", expanded=False):
        with st.form("f_penghuni", clear_on_submit=True):
            c1, c2 = st.columns(2)
            kode_r = c1.selectbox("Pilih Tempat Tinggal (Kode)", list_kode)
            
            if list_pegawai:
                nama_p = c2.selectbox("Pilih Nama Pegawai", list_pegawai)
            else:
                nama_p = c2.text_input("Nama Lengkap Penghuni")
            
            c3, c4, c5 = st.columns(3)
            status_p = c3.text_input("Status (Karyawan / Guru / Dll)")
            jab = c4.text_input("Jabatan")
            unit = c5.text_input("Unit Kerja")
            hp = st.text_input("No HP / WhatsApp")
            
            btn_p = st.form_submit_button("Simpan Data Penghuni")
            if btn_p and nama_p:
                data_p = {"kode_rumah": kode_r, "nama": nama_p, "status": status_p, "jabatan": jab, "unit": unit, "no_hp": hp, "mulai_menempati": str(date.today())}
                supabase.table('data_penghuni').insert(data_p).execute()
                st.success("✅ Data Penghuni berhasil ditambahkan!")
                st.rerun()

    st.dataframe(df_penghuni, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# 6. INVENTARIS ASET
# -------------------------------------------------------------
elif menu == "📦 Inventaris Aset":
    st.subheader("📦 Daftar Inventaris & Aset")
    list_kode = df_rekap["kode"].tolist() if not df_rekap.empty else ["-"]
    
    with st.expander("➕ Tambah Aset Inventaris Baru", expanded=False):
        with st.form("f_inv", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            kode_r = c1.selectbox("Kode Rumah", list_kode)
            nama_b = c2.text_input("Nama Barang / Aset")
            jumlah = c3.number_input("Jumlah Unit", min_value=1, value=1)
            
            c4, c5 = st.columns(2)
            kondisi_b = c4.selectbox("Kondisi Aset", ["Baik", "Rusak Ringan", "Rusak Berat"])
            catatan_b = c5.text_input("Catatan Tambahan")
            
            btn_i = st.form_submit_button("Simpan Aset")
            if btn_i and nama_b:
                data_i = {"kode_rumah": kode_r, "barang": nama_b, "jumlah": jumlah, "kondisi": kondisi_b, "catatan": catatan_b}
                supabase.table('inventaris_aset').insert(data_i).execute()
                st.success("✅ Aset berhasil dicatat!")
                st.rerun()

    st.dataframe(df_inventaris, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# 7. MAINTENANCE
# -------------------------------------------------------------
elif menu == "🛠️ Maintenance / Perbaikan":
    st.subheader("🛠️ Riwayat Maintenance & Perbaikan")
    list_kode = df_rekap["kode"].tolist() if not df_rekap.empty else ["-"]
    
    with st.expander("➕ Catat Perbaikan Baru", expanded=False):
        with st.form("f_maint", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            tgl = c1.date_input("Tanggal Perbaikan", value=date.today())
            kode_r = c2.selectbox("Kode Rumah", list_kode)
            jenis_p = c3.text_input("Jenis Perbaikan / Kerusakan")
            
            c4, c5, c6 = st.columns(3)
            biaya = c4.number_input("Estimasi / Biaya (Rp)", min_value=0, value=0, step=50000)
            vendor = c5.text_input("Teknisi / Vendor")
            pic_m = c6.text_input("PIC Lapangan")
            
            status_m = st.selectbox("Status Pekerjaan", ["Pending", "Diproses", "Selesai"])
            
            btn_m = st.form_submit_button("Simpan Catatan Maintenance")
            if btn_m and jenis_p:
                data_m = {"tanggal": str(tgl), "kode_rumah": kode_r, "jenis_perbaikan": jenis_p, "biaya": biaya, "vendor": vendor, "pic": pic_m, "status": status_m}
                supabase.table('maintenance_log').insert(data_m).execute()
                st.success("✅ Catatan maintenance disimpan!")
                st.rerun()

    st.dataframe(df_maint, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# 8. EKSPOR EXCEL LAPORAN
# -------------------------------------------------------------
elif menu == "📥 Ekspor Excel Laporan":
    st.subheader("📥 Unduh Laporan Master Excel")
    st.write("Tekan tombol di bawah untuk mengunduh seluruh data dalam satu file Excel multi-sheet.")
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_pegawai.to_excel(writer, sheet_name='Master Pegawai', index=False)
        df_rekap.to_excel(writer, sheet_name='Rekap & Subsidi', index=False)
        df_penghuni.to_excel(writer, sheet_name='Data Penghuni', index=False)
        df_inventaris.to_excel(writer, sheet_name='Inventaris Aset', index=False)
        df_maint.to_excel(writer, sheet_name='Maintenance Log', index=False)
    
    st.download_button(
        label="📥 Download Laporan Lengkap (.xlsx)",
        data=output.getvalue(),
        file_name="Laporan_Master_Sensus_Insan_Madani.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )