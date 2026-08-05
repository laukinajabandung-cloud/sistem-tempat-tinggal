import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client
import plotly.express as px
import plotly.graph_objects as go
import io

# -------------------------------------------------------------
# 1. KONFIGURASI HALAMAN & THEME ELEGANT
# -------------------------------------------------------------
st.set_page_config(
    page_title="Sistem Tempat Tinggal - Insan Madani", 
    page_icon="🏠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Premium & Clean Design
st.markdown("""
<style>
    /* Google Font Import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #f8fafc;
    }

    /* Modern Header Banner */
    .header-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        color: white;
        padding: 30px 35px;
        border-radius: 16px;
        margin-bottom: 28px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .header-text h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    
    .header-text p {
        margin: 6px 0 0 0;
        color: #94a3b8;
        font-size: 14px;
        font-weight: 400;
    }

    .header-badge {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.3);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }

    /* Custom Metric Card */
    .metric-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        border: 1px solid #f1f5f9;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
    }

    .metric-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: #0ea5e9;
    }

    .metric-card.accent-emerald::before { background: #10b981; }
    .metric-card.accent-amber::before { background: #f59e0b; }
    .metric-card.accent-indigo::before { background: #6366f1; }
    .metric-card.accent-rose::before { background: #f43f5e; }

    .metric-card h4 {
        color: #64748b;
        font-size: 12px;
        margin-bottom: 6px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-card h2 {
        color: #0f172a;
        font-size: 22px;
        font-weight: 700;
        margin: 0;
    }

    /* Subheader Styling */
    .section-title {
        color: #0f172a;
        font-size: 18px;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Sidebar Clean Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #f1f5f9;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #e2e8f0;
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px;
        padding: 0 20px;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        font-size: 14px;
        color: #64748b;
    }

    .stTabs [aria-selected="true"] {
        color: #0ea5e9 !important;
        border-bottom-color: #0ea5e9 !important;
    }

    /* Hide Streamlit Footer & Menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. KONEKSI SUPABASE
# -------------------------------------------------------------
SUPABASE_URL = "https://lqczctceamyvzdgtnfdi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxxY3pjdGNlYW15dnpkZ3RuZmRpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc3MzYyMDgsImV4cCI6MjA5MzMxMjIwOH0.G7WVQV6OjAHLP1ecGCjKfcOml-XECQXrAOPDOWR-Muc"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"⚠️ Gagal terhubung ke Supabase: {e}")

# -------------------------------------------------------------
# 3. FUNGSI AMBIL DATA (SAFE LOAD WITH HANDLING)
# -------------------------------------------------------------
def load_pegawai():
    try:
        res = supabase.table('master_pegawai').select('id, nipy, nama, jabatan, unit_kerja, no_hp, email, status_kepegawaian').execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=['id', 'nipy', 'nama', 'jabatan', 'unit_kerja', 'no_hp', 'email', 'status_kepegawaian'])
    except Exception:
        return pd.DataFrame(columns=['id', 'nipy', 'nama', 'jabatan', 'unit_kerja', 'no_hp', 'email', 'status_kepegawaian'])

def load_rekap():
    try:
        res = supabase.table('rekap_tempat_tinggal').select('id, kode, nama, jenis, status, alamat, pic, penghuni, kondisi, prioritas, biaya_sewa_tahun, subsidi_yayasan').execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=['id', 'kode', 'nama', 'jenis', 'status', 'alamat', 'pic', 'penghuni', 'kondisi', 'prioritas', 'biaya_sewa_tahun', 'subsidi_yayasan'])
        
        if not df.empty:
            df['biaya_sewa_tahun'] = pd.to_numeric(df['biaya_sewa_tahun'], errors='coerce').fillna(0)
            df['subsidi_yayasan'] = pd.to_numeric(df['subsidi_yayasan'], errors='coerce').fillna(0)
            df['sisa_tanggungan_pegawai'] = (df['biaya_sewa_tahun'] - df['subsidi_yayasan']).apply(lambda x: max(x, 0))
        return df
    except Exception:
        return pd.DataFrame(columns=['id', 'kode', 'nama', 'jenis', 'status', 'alamat', 'pic', 'penghuni', 'kondisi', 'prioritas', 'biaya_sewa_tahun', 'subsidi_yayasan', 'sisa_tanggungan_pegawai'])

def load_penghuni():
    try:
        res = supabase.table('data_penghuni').select('id, kode_rumah, nama, status, jabatan, unit, no_hp, mulai_menempati').execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=['id', 'kode_rumah', 'nama', 'status', 'jabatan', 'unit', 'no_hp', 'mulai_menempati'])
    except Exception:
        return pd.DataFrame(columns=['id', 'kode_rumah', 'nama', 'status', 'jabatan', 'unit', 'no_hp', 'mulai_menempati'])

def load_inventaris():
    try:
        res = supabase.table('inventaris_aset').select('id, kode_rumah, barang, jumlah, kondisi, catatan').execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=['id', 'kode_rumah', 'barang', 'jumlah', 'kondisi', 'catatan'])
    except Exception:
        return pd.DataFrame(columns=['id', 'kode_rumah', 'barang', 'jumlah', 'kondisi', 'catatan'])

def load_maintenance():
    try:
        res = supabase.table('maintenance_log').select('id, tanggal, kode_rumah, jenis_perbaikan, biaya, vendor, pic, status').execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=['id', 'tanggal', 'kode_rumah', 'jenis_perbaikan', 'biaya', 'vendor', 'pic', 'status'])
        if not df.empty and 'biaya' in df:
            df['biaya'] = pd.to_numeric(df['biaya'], errors='coerce').fillna(0)
        return df
    except Exception:
        return pd.DataFrame(columns=['id', 'tanggal', 'kode_rumah', 'jenis_perbaikan', 'biaya', 'vendor', 'pic', 'status'])

# Load All Datasets
df_pegawai = load_pegawai()
df_rekap = load_rekap()
df_penghuni = load_penghuni()
df_inventaris = load_inventaris()
df_maint = load_maintenance()

# -------------------------------------------------------------
# 4. SIDEBAR NAVIGATION
# -------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/609/609803.png", width=60)
    st.markdown("<h2 style='font-size: 18px; font-weight: 700; color: #0f172a; margin-top: 5px;'>Insan Madani System</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 12px; color: #64748b; margin-bottom: 20px;'>Sistem Informasi Housing & Asset</p>", unsafe_allow_html=True)
    
    menu = st.radio(
        "NAVIGASI UTAMA", 
        [
            "📊 Dashboard & Analisis", 
            "👨‍💼 Data Pegawai (Master)",
            "📝 Form Sensus Baru", 
            "🏢 Rekap Unit & Subsidi", 
            "👥 Plotting Penghuni", 
            "📦 Inventaris & Aset", 
            "🛠️ Log Maintenance",
            "📥 Export Center"
        ],
        index=0
    )
    
    st.markdown("---")
    st.caption("v2.1 • Executive Dashboard")

# -------------------------------------------------------------
# 5. HEADER BANNER
# -------------------------------------------------------------
st.markdown("""
    <div class="header-box">
        <div class="header-text">
            <h1>🏠 Management Tempat Tinggal & Aset Insan Madani</h1>
            <p>Platform monitoring dan pengelolaan tempat tinggal, subsidi sewa, aset inventaris, serta pemeliharaan unit.</p>
        </div>
        <div class="header-badge">
            ● Database Connected
        </div>
    </div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# MENU 1: DASHBOARD & ANALISIS
# -------------------------------------------------------------
if menu == "📊 Dashboard & Analisis":
    # Calculating KPI Values
    tot_peg = len(df_pegawai)
    tot_tt = len(df_rekap)
    tot_penghuni = int(df_rekap["penghuni"].sum()) if not df_rekap.empty and 'penghuni' in df_rekap else 0
    tot_subsidi = df_rekap["subsidi_yayasan"].sum() if not df_rekap.empty and 'subsidi_yayasan' in df_rekap else 0
    tot_biaya_maint = df_maint["biaya"].sum() if not df_maint.empty and 'biaya' in df_maint else 0

    # Metric Cards Grid
    c1, c2, c3, c4, c5 = st.columns(5)
    
    c1.markdown(f'<div class="metric-card accent-indigo"><h4>Total Pegawai</h4><h2>{tot_peg:,} Staf</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><h4>Unit Rumah</h4><h2>{tot_tt:,} Unit</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card accent-emerald"><h4>Total Penghuni</h4><h2>{tot_penghuni:,} Jiwa</h2></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card accent-amber"><h4>Subsidi Sewa/Thn</h4><h2>Rp {tot_subsidi:,.0f}</h2></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="metric-card accent-rose"><h4>Biaya Maintenance</h4><h2>Rp {tot_biaya_maint:,.0f}</h2></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Visualisasi Data & Analisis Strategis</div>', unsafe_allow_html=True)
    
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        if not df_rekap.empty and 'kondisi' in df_rekap and not df_rekap['kondisi'].isnull().all():
            kondisi_counts = df_rekap['kondisi'].value_counts().reset_index()
            kondisi_counts.columns = ['Kondisi', 'Jumlah']
            fig_kondisi = px.bar(
                kondisi_counts, x='Kondisi', y='Jumlah', color='Kondisi', 
                title="<b>Kondisi Fisik Tempat Tinggal</b>",
                color_discrete_map={'Baik': '#10b981', 'Perlu Perbaikan': '#f59e0b', 'Perlu Renovasi': '#ef4444'},
                text_auto=True
            )
            fig_kondisi.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False, height=340, margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_kondisi, use_container_width=True)
        else:
            st.info("ℹ️ Belum ada data kondisi tempat tinggal.")

    with g_col2:
        if not df_rekap.empty and 'jenis' in df_rekap and not df_rekap['jenis'].isnull().all():
            jenis_counts = df_rekap['jenis'].value_counts().reset_index()
            jenis_counts.columns = ['Jenis', 'Jumlah']
            fig_jenis = px.pie(
                jenis_counts, names='Jenis', values='Jumlah', hole=0.5,
                title="<b>Distribusi Jenis Tempat Tinggal</b>",
                color_discrete_sequence=['#0ea5e9', '#6366f1', '#8b5cf6', '#ec4899', '#14b8a6']
            )
            fig_jenis.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', height=340, margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_jenis, use_container_width=True)
        else:
            st.info("ℹ️ Belum ada data jenis tempat tinggal.")

    st.markdown("<br>", unsafe_allow_html=True)
    g_col3, g_col4 = st.columns(2)

    with g_col3:
        if not df_inventaris.empty and 'kondisi' in df_inventaris and not df_inventaris['kondisi'].isnull().all():
            inv_counts = df_inventaris['kondisi'].value_counts().reset_index()
            inv_counts.columns = ['Kondisi', 'Jumlah']
            fig_inv = px.bar(
                inv_counts, x='Jumlah', y='Kondisi', orientation='h',
                title="<b>Status Kondisi Aset Inventaris</b>",
                color='Kondisi',
                color_discrete_map={'Baik': '#0ea5e9', 'Rusak Ringan': '#f59e0b', 'Rusak Berat': '#ef4444'},
                text_auto=True
            )
            fig_inv.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False, height=320, margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_inv, use_container_width=True)
        else:
            st.info("ℹ️ Belum ada data aset inventaris.")

    with g_col4:
        if not df_maint.empty and 'status' in df_maint and not df_maint['status'].isnull().all():
            maint_counts = df_maint['status'].value_counts().reset_index()
            maint_counts.columns = ['Status', 'Jumlah']
            fig_maint = px.pie(
                maint_counts, names='Status', values='Jumlah', hole=0.4,
                title="<b>Progress Task Maintenance</b>",
                color_discrete_sequence=['#f59e0b', '#06b6d4', '#10b981']
            )
            fig_maint.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', height=320, margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_maint, use_container_width=True)
        else:
            st.info("ℹ️ Belum ada log maintenance.")

# -------------------------------------------------------------
# MENU 2: DAFTAR PEGAWAI / INSAN MADANI
# -------------------------------------------------------------
elif menu == "👨‍💼 Data Pegawai (Master)":
    st.markdown('<div class="section-title">👨‍💼 Kelola Master Data Pegawai</div>', unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["📋 Master Data Pegawai", "➕ Tambah Pegawai", "📥 Batch Import (Excel)"])
    
    with t1:
        # Search & Filter Bar
        s_col1, s_col2 = st.columns([3, 1])
        search_kw = s_col1.text_input("🔍 Cari NIPY, Nama, atau Jabatan...", key="search_peg")
        unit_filter = s_col2.selectbox("Filter Unit Kerja", ["Semua"] + list(df_pegawai['unit_kerja'].unique()) if not df_pegawai.empty else ["Semua"])

        df_filtered = df_pegawai.copy()
        if search_kw:
            df_filtered = df_filtered[df_filtered.apply(lambda row: search_kw.lower() in str(row).lower(), axis=1)]
        if unit_filter != "Semua":
            df_filtered = df_filtered[df_filtered['unit_kerja'] == unit_filter]

        st.dataframe(df_filtered, use_container_width=True, hide_index=True)

    with t2:
        with st.form("f_pegawai_new", clear_on_submit=True):
            st.markdown("##### 📝 Form Tambah Pegawai Baru")
            c1, c2 = st.columns(2)
            nipy = c1.text_input("NIPY (Nomor Induk Pegawai Yayasan)*", placeholder="Contoh: IM-2024-001")
            nama_p = c2.text_input("Nama Lengkap Pegawai*", placeholder="Nama lengkap tanpa gelar")
            
            c3, c4, c5 = st.columns(3)
            jabatan = c3.text_input("Jabatan", placeholder="Guru / Staf / Ka. Unit")
            unit = c4.text_input("Unit Kerja", placeholder="SMA / SMP / Yayasan")
            status_k = c5.selectbox("Status Kepegawaian", ["Tetap", "Tidak Tetap", "Honorer", "Magang", "Lainnya"])
            
            c6, c7 = st.columns(2)
            hp = c6.text_input("No. WhatsApp", placeholder="08xxxxxxxxxx")
            email = c7.text_input("Alamat Email", placeholder="email@insanmadani.sch.id")
            
            submitted = st.form_submit_button("💾 Simpan Data Pegawai", use_container_width=True)
            if submitted:
                if nipy and nama_p:
                    data_peg = {
                        "nipy": nipy, "nama": nama_p, "jabatan": jabatan,
                        "unit_kerja": unit, "no_hp": hp, "email": email,
                        "status_kepegawaian": status_k
                    }
                    try:
                        supabase.table('master_pegawai').insert(data_peg).execute()
                        st.success("✅ Data pegawai berhasil ditambahkan!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Gagal menyimpan data: {e}")
                else:
                    st.warning("⚠️ NIPY dan Nama Pegawai wajib diisi!")

    with t3:
        st.markdown("##### 1. Unduh Template Excel Standards")
        df_template = pd.DataFrame([
            {"nipy": "IM-2024-001", "nama": "Ahmad Abdullah", "jabatan": "Guru Matematika", "unit_kerja": "SMA Insan Madani", "no_hp": "081234567890", "email": "ahmad@insanmadani.sch.id", "status_kepegawaian": "Tetap"},
            {"nipy": "IM-2024-002", "nama": "Siti Rahmawati", "jabatan": "Staf HRD", "unit_kerja": "Yayasan", "no_hp": "089876543210", "email": "siti@insanmadani.sch.id", "status_kepegawaian": "Kontrak"}
        ])
        
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            df_template.to_excel(writer, sheet_name='Template_Pegawai', index=False)
            
        st.download_button(
            label="📥 Unduh Template Format Excel (.xlsx)",
            data=buf.getvalue(),
            file_name="Template_Master_Pegawai.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.markdown("---")
        st.markdown("##### 2. Upload Data Excel Pegawai")
        up_file = st.file_uploader("Upload file Excel yang sudah diisi", type=["xlsx", "xls"])
        if up_file:
            try:
                df_up = pd.read_excel(up_file)
                st.write("Preview Data Import:")
                st.dataframe(df_up, use_container_width=True)
                
                req_cols = ["nipy", "nama", "jabatan", "unit_kerja", "no_hp", "email", "status_kepegawaian"]
                if all(c in df_up.columns for c in req_cols):
                    if st.button("🚀 Import Data Sekarang", use_container_width=True):
                        records = df_up[req_cols].fillna("").to_dict(orient="records")
                        supabase.table('master_pegawai').upsert(records).execute()
                        st.success(f"🎉 Berhasil mengimport {len(records)} data pegawai!")
                        st.rerun()
                else:
                    st.error(f"❌ Format Kolom tidak sesuai! Wajib menyertakan: {', '.join(req_cols)}")
            except Exception as e:
                st.error(f"❌ Gagal memproses file: {e}")

# -------------------------------------------------------------
# MENU 3: FORM SENSUS BARU
# -------------------------------------------------------------
elif menu == "📝 Form Sensus Baru":
    st.markdown('<div class="section-title">📝 Registration / Sensus Unit Tempat Tinggal</div>', unsafe_allow_html=True)
    
    with st.form("f_sensus_new", clear_on_submit=True):
        c1, c2 = st.columns(2)
        kode = c1.text_input("Kode Tempat Tinggal*", placeholder="Contoh: IM-SEWA-01")
        nama = c2.text_input("Nama Unit / Ringkasan Lokasi*", placeholder="Contoh: Rumdin Block A3")
        
        c3, c4 = st.columns(2)
        jenis = c3.selectbox("Jenis Aset/Hunian", ["Rumah Sewa", "Rumah Dinas", "Wisma", "Asrama", "Rumah Pribadi"])
        status_hak = c4.selectbox("Status Kepemilikan", ["Sewa", "Milik Sendiri", "Milik Yayasan"])
        
        alamat = st.text_area("Alamat Lengkap Unit", placeholder="Jl. ... No. ... RT/RW ...")
        
        st.markdown("---")
        st.markdown("##### 💵 Skema Sewa & Subsidi (Khusus Rumah Sewa)")
        c_sewa1, c_sewa2 = st.columns(2)
        biaya = c_sewa1.number_input("Biaya Sewa / Tahun (Rp)", min_value=0, value=12000000, step=500000)
        subsidi = c_sewa2.number_input("Subsidi Yayasan / Tahun (Rp)", min_value=0, value=10000000, step=500000)
        
        st.markdown("---")
        c5, c6, c7, c8 = st.columns(4)
        pic = c5.text_input("PIC Lapangan")
        penghuni_max = c6.number_input("Kapasitas Penghuni", min_value=1, value=1)
        kondisi = c7.selectbox("Kondisi Unit", ["Baik", "Perlu Perbaikan", "Perlu Renovasi"])
        prio = c8.selectbox("Prioritas Penanganan", ["Rendah", "Sedang", "Tinggi"])
        
        sub_btn = st.form_submit_button("💾 Simpan Data Sensus Unit", use_container_width=True)
        if sub_btn:
            if kode and nama:
                ins_data = {
                    "kode": kode, "nama": nama, "jenis": jenis, "status": status_hak, 
                    "alamat": alamat, "pic": pic, "penghuni": penghuni_max, 
                    "kondisi": kondisi, "prioritas": prio,
                    "biaya_sewa_tahun": biaya if status_hak == "Sewa" else 0,
                    "subsidi_yayasan": subsidi if status_hak == "Sewa" else 0
                }
                try:
                    supabase.table('rekap_tempat_tinggal').insert(ins_data).execute()
                    st.success("✅ Data unit berhasil disimpan ke database!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {e}")
            else:
                st.warning("⚠️ Kode Unit dan Nama Unit wajib diisi!")

# -------------------------------------------------------------
# MENU 4: REKAP TEMPAT TINGGAL & SUBSIDI
# -------------------------------------------------------------
elif menu == "🏢 Rekap Unit & Subsidi":
    st.markdown('<div class="section-title">🏢 Rekapituasi Tempat Tinggal & Rincian Subsidi</div>', unsafe_allow_html=True)
    
    if not df_rekap.empty:
        # Currency Formatter Display
        df_display = df_rekap.copy()
        df_display['biaya_sewa_tahun'] = df_display['biaya_sewa_tahun'].apply(lambda x: f"Rp {x:,.0f}")
        df_display['subsidi_yayasan'] = df_display['subsidi_yayasan'].apply(lambda x: f"Rp {x:,.0f}")
        if 'sisa_tanggungan_pegawai' in df_display:
            df_display['sisa_tanggungan_pegawai'] = df_display['sisa_tanggungan_pegawai'].apply(lambda x: f"Rp {x:,.0f}")
            
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ Belum ada data rekap unit tempat tinggal.")

# -------------------------------------------------------------
# MENU 5: DATA PENGHUNI
# -------------------------------------------------------------
elif menu == "👥 Plotting Penghuni":
    st.markdown('<div class="section-title">👥 Penempatan & Plotting Penghuni Unit</div>', unsafe_allow_html=True)
    
    list_kode = df_rekap["kode"].tolist() if not df_rekap.empty else ["-"]
    list_pegawai = df_pegawai["nama"].tolist() if not df_pegawai.empty else []
    
    with st.expander("➕ Form Plotting Penghuni Baru", expanded=False):
        with st.form("f_penghuni_add", clear_on_submit=True):
            c1, c2 = st.columns(2)
            kode_r = c1.selectbox("Pilih Kode Rumah/Unit", list_kode)
            
            if list_pegawai:
                nama_p = c2.selectbox("Pilih Pegawai (Master)", list_pegawai)
            else:
                nama_p = c2.text_input("Nama Penghuni")
                
            c3, c4, c5 = st.columns(3)
            status_p = c3.text_input("Status Penghuni", value="Pegawai Tetap")
            jab = c4.text_input("Jabatan")
            unit = c5.text_input("Unit Kerja")
            hp = st.text_input("No. HP / WhatsApp Active")
            
            btn_submit = st.form_submit_button("💾 Plotting Penghuni")
            if btn_submit and nama_p:
                p_data = {
                    "kode_rumah": kode_r, "nama": nama_p, "status": status_p, 
                    "jabatan": jab, "unit": unit, "no_hp": hp, 
                    "mulai_menempati": str(date.today())
                }
                supabase.table('data_penghuni').insert(p_data).execute()
                st.success("✅ Penghuni berhasil ditambahkan!")
                st.rerun()

    st.dataframe(df_penghuni, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# MENU 6: INVENTARIS ASET
# -------------------------------------------------------------
elif menu == "📦 Inventaris & Aset":
    st.markdown('<div class="section-title">📦 Pencatatan Inventaris & Aset Unit</div>', unsafe_allow_html=True)
    
    list_kode = df_rekap["kode"].tolist() if not df_rekap.empty else ["-"]
    
    with st.expander("➕ Registrasi Aset Inventaris Unit", expanded=False):
        with st.form("f_inv_add", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            kode_r = c1.selectbox("Lokasi Unit (Kode)", list_kode)
            nama_b = c2.text_input("Nama Barang / Aset*", placeholder="Contoh: AC Split 1 PK")
            jumlah = c3.number_input("Jumlah Unit", min_value=1, value=1)
            
            c4, c5 = st.columns(2)
            kondisi_b = c4.selectbox("Kondisi Fisik Barang", ["Baik", "Rusak Ringan", "Rusak Berat"])
            catatan_b = c5.text_input("Keterangan / Merk / SN")
            
            btn_inv = st.form_submit_button("💾 Simpan Data Aset")
            if btn_inv and nama_b:
                inv_data = {
                    "kode_rumah": kode_r, "barang": nama_b, 
                    "jumlah": jumlah, "kondisi": kondisi_b, "catatan": catatan_b
                }
                supabase.table('inventaris_aset').insert(inv_data).execute()
                st.success("✅ Barang inventaris berhasil didaftarkan!")
                st.rerun()

    st.dataframe(df_inventaris, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# MENU 7: MAINTENANCE
# -------------------------------------------------------------
elif menu == "🛠️ Log Maintenance":
    st.markdown('<div class="section-title">🛠️ Pemeliharaan & Perbaikan Unit</div>', unsafe_allow_html=True)
    
    list_kode = df_rekap["kode"].tolist() if not df_rekap.empty else ["-"]
    
    with st.expander("➕ Lapor/Catat Task Perbaikan Baru", expanded=False):
        with st.form("f_maint_add", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            tgl = c1.date_input("Tanggal Work Order", value=date.today())
            kode_r = c2.selectbox("Kode Unit Tempat Tinggal", list_kode)
            jenis_p = c3.text_input("Deskripsi Perbaikan/Kerusakan*", placeholder="Contoh: Perbaikan Atap Bocor")
            
            c4, c5, c6 = st.columns(3)
            biaya = c4.number_input("Estimasi / Realisasi Biaya (Rp)", min_value=0, value=0, step=50000)
            vendor = c5.text_input("Teknisi / Subkontraktor")
            pic_m = c6.text_input("PIC Internal / Supervisor")
            
            status_m = st.selectbox("Status Progress Work Order", ["Pending", "Diproses", "Selesai"])
            
            btn_maint = st.form_submit_button("💾 Catat Work Order Maintenance")
            if btn_maint and jenis_p:
                m_data = {
                    "tanggal": str(tgl), "kode_rumah": kode_r, "jenis_perbaikan": jenis_p, 
                    "biaya": biaya, "vendor": vendor, "pic": pic_m, "status": status_m
                }
                supabase.table('maintenance_log').insert(m_data).execute()
                st.success("✅ Log maintenance berhasil disimpan!")
                st.rerun()

    if not df_maint.empty:
        df_maint_disp = df_maint.copy()
        if 'biaya' in df_maint_disp:
            df_maint_disp['biaya'] = df_maint_disp['biaya'].apply(lambda x: f"Rp {x:,.0f}")
        st.dataframe(df_maint_disp, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ Belum ada riwayat perbaikan/maintenance.")

# -------------------------------------------------------------
# MENU 8: EXPORT CENTER
# -------------------------------------------------------------
elif menu == "📥 Export Center":
    st.markdown('<div class="section-title">📥 Download Laporan Master (Excel Workbook)</div>', unsafe_allow_html=True)
    st.write("Unduh seluruh basis data sistem dalam bentuk dokumen Excel multi-tab yang terstruktur.")
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_pegawai.to_excel(writer, sheet_name='Master Pegawai', index=False)
        df_rekap.to_excel(writer, sheet_name='Rekap Unit & Subsidi', index=False)
        df_penghuni.to_excel(writer, sheet_name='Data Penghuni', index=False)
        df_inventaris.to_excel(writer, sheet_name='Inventaris Aset', index=False)
        df_maint.to_excel(writer, sheet_name='Maintenance Log', index=False)
        
    st.download_button(
        label="📥 Download Master Report Workbook (.xlsx)",
        data=output.getvalue(),
        file_name=f"Laporan_Sensus_Insan_Madani_{date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )