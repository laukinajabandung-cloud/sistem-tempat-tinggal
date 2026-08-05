import streamlit as st
import pandas as pd
from datetime import date, datetime
from supabase import create_client, Client
import plotly.express as px
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
        padding: 26px 30px;
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .header-text h1 {
        margin: 0;
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    
    .header-text p {
        margin: 4px 0 0 0;
        color: #94a3b8;
        font-size: 13px;
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
        padding: 18px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        border: 1px solid #f1f5f9;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
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
        font-size: 11px;
        margin-bottom: 6px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-card h2 {
        color: #0f172a;
        font-size: 20px;
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
# 3. FUNGSI AMBIL DATA
# -------------------------------------------------------------
def load_pegawai():
    try:
        res = supabase.table('master_pegawai').select('*').execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=['id', 'nipy', 'nama', 'jabatan', 'unit_kerja', 'no_hp', 'email', 'status_kepegawaian'])
    except Exception:
        return pd.DataFrame(columns=['id', 'nipy', 'nama', 'jabatan', 'unit_kerja', 'no_hp', 'email', 'status_kepegawaian'])

def load_rekap():
    try:
        res = supabase.table('rekap_tempat_tinggal').select('*').execute()
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
        res = supabase.table('data_penghuni').select('*').execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=['id', 'kode_rumah', 'nama', 'status', 'jabatan', 'unit', 'no_hp', 'mulai_menempati'])
    except Exception:
        return pd.DataFrame(columns=['id', 'kode_rumah', 'nama', 'status', 'jabatan', 'unit', 'no_hp', 'mulai_menempati'])

def load_inventaris():
    try:
        res = supabase.table('inventaris_aset').select('*').execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=['id', 'kode_rumah', 'barang', 'jumlah', 'kondisi', 'catatan'])
    except Exception:
        return pd.DataFrame(columns=['id', 'kode_rumah', 'barang', 'jumlah', 'kondisi', 'catatan'])

def load_maintenance():
    try:
        res = supabase.table('maintenance_log').select('*').execute()
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
# 4. SIDEBAR & HEADER
# -------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/609/609803.png", width=60)
    st.markdown("<h2 style='font-size: 18px; font-weight: 700; color: #0f172a; margin-top: 5px;'>Insan Madani System</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 12px; color: #64748b; margin-bottom: 20px;'>Sistem Housing & Management Aset</p>", unsafe_allow_html=True)
    
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
    st.caption("v2.2 • Complete CRUD Supported")

st.markdown("""
    <div class="header-box">
        <div class="header-text">
            <h1>🏠 Management Tempat Tinggal Insan Madani</h1>
            <p>Platform monitoring, kelola pegawai, unit hunian, inventaris, dan maintenance terintegrasi.</p>
        </div>
        <div class="header-badge">
            ● Database Active
        </div>
    </div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# MENU 1: DASHBOARD
# -------------------------------------------------------------
if menu == "📊 Dashboard & Analisis":
    tot_peg = len(df_pegawai)
    tot_tt = len(df_rekap)
    tot_penghuni = int(df_rekap["penghuni"].sum()) if not df_rekap.empty and 'penghuni' in df_rekap else 0
    tot_subsidi = df_rekap["subsidi_yayasan"].sum() if not df_rekap.empty and 'subsidi_yayasan' in df_rekap else 0
    tot_biaya_maint = df_maint["biaya"].sum() if not df_maint.empty and 'biaya' in df_maint else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(f'<div class="metric-card accent-indigo"><h4>Total Pegawai</h4><h2>{tot_peg:,} Staf</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><h4>Unit Rumah</h4><h2>{tot_tt:,} Unit</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card accent-emerald"><h4>Total Penghuni</h4><h2>{tot_penghuni:,} Jiwa</h2></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card accent-amber"><h4>Subsidi Sewa/Thn</h4><h2>Rp {tot_subsidi:,.0f}</h2></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="metric-card accent-rose"><h4>Biaya Maintenance</h4><h2>Rp {tot_biaya_maint:,.0f}</h2></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Visualisasi Data & Ringkasan Dashboard</div>', unsafe_allow_html=True)
    
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        if not df_rekap.empty and 'kondisi' in df_rekap and not df_rekap['kondisi'].isnull().all():
            kondisi_counts = df_rekap['kondisi'].value_counts().reset_index()
            kondisi_counts.columns = ['Kondisi', 'Jumlah']
            fig_kondisi = px.bar(kondisi_counts, x='Kondisi', y='Jumlah', color='Kondisi', 
                                 title="<b>Kondisi Fisik Tempat Tinggal</b>",
                                 color_discrete_map={'Baik': '#10b981', 'Perlu Perbaikan': '#f59e0b', 'Perlu Renovasi': '#ef4444'}, text_auto=True)
            fig_kondisi.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, height=340)
            st.plotly_chart(fig_kondisi, use_container_width=True)
        else:
            st.info("ℹ️ Belum ada data tempat tinggal.")

    with g_col2:
        if not df_rekap.empty and 'jenis' in df_rekap and not df_rekap['jenis'].isnull().all():
            jenis_counts = df_rekap['jenis'].value_counts().reset_index()
            jenis_counts.columns = ['Jenis', 'Jumlah']
            fig_jenis = px.pie(jenis_counts, names='Jenis', values='Jumlah', hole=0.5,
                               title="<b>Distribusi Jenis Tempat Tinggal</b>", color_discrete_sequence=['#0ea5e9', '#6366f1', '#8b5cf6', '#ec4899'])
            fig_jenis.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=340)
            st.plotly_chart(fig_jenis, use_container_width=True)
        else:
            st.info("ℹ️ Belum ada data tempat tinggal.")

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
# MENU 2: DAFTAR PEGAWAI (DENGAN CRUD)
# -------------------------------------------------------------
elif menu == "👨‍💼 Data Pegawai (Master)":
    st.markdown('<div class="section-title">👨‍💼 Kelola Master Data Pegawai</div>', unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["📋 Master Data & Aksi", "➕ Tambah Pegawai", "📥 Batch Import Excel"])
    
    with t1:
        s_col1, s_col2 = st.columns([3, 1])
        search_kw = s_col1.text_input("🔍 Cari NIPY, Nama, atau Jabatan...", key="search_peg")
        unit_filter = s_col2.selectbox("Filter Unit Kerja", ["Semua"] + list(df_pegawai['unit_kerja'].unique()) if not df_pegawai.empty else ["Semua"])

        df_filtered = df_pegawai.copy()
        if search_kw:
            df_filtered = df_filtered[df_filtered.apply(lambda row: search_kw.lower() in str(row).lower(), axis=1)]
        if unit_filter != "Semua":
            df_filtered = df_filtered[df_filtered['unit_kerja'] == unit_filter]

        st.dataframe(df_filtered, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("##### ⚙️ Aksi Kelola Data (View, Edit, Delete)")
        
        if not df_filtered.empty:
            peg_options = {f"{row['nipy']} - {row['nama']}": row['id'] for _, row in df_filtered.iterrows()}
            selected_peg_label = st.selectbox("Pilih Pegawai untuk Diolah", list(peg_options.keys()), key="sel_peg")
            selected_peg_id = peg_options[selected_peg_label]
            row_peg = df_filtered[df_filtered['id'] == selected_peg_id].iloc[0]

            act_col1, act_col2, act_col3 = st.columns(3)
            
            # VIEW
            with act_col1:
                with st.expander("👁️ View Detail", expanded=False):
                    st.write(f"**NIPY:** {row_peg['nipy']}")
                    st.write(f"**Nama:** {row_peg['nama']}")
                    st.write(f"**Jabatan:** {row_peg['jabatan']}")
                    st.write(f"**Unit Kerja:** {row_peg['unit_kerja']}")
                    st.write(f"**Status:** {row_peg['status_kepegawaian']}")
                    st.write(f"**No. HP:** {row_peg['no_hp']}")
                    st.write(f"**Email:** {row_peg['email']}")

            # EDIT
            with act_col2:
                with st.expander("✏️ Edit Data", expanded=False):
                    with st.form(f"f_edit_peg_{selected_peg_id}"):
                        e_nipy = st.text_input("NIPY", value=str(row_peg['nipy']))
                        e_nama = st.text_input("Nama Lengkap", value=str(row_peg['nama']))
                        e_jab = st.text_input("Jabatan", value=str(row_peg['jabatan']))
                        e_unit = st.text_input("Unit Kerja", value=str(row_peg['unit_kerja']))
                        e_stat = st.selectbox("Status", ["Tetap", "Kontrak", "Guru/Pengajar", "Magang", "Lainnya"], index=0)
                        e_hp = st.text_input("No HP", value=str(row_peg['no_hp']))
                        e_email = st.text_input("Email", value=str(row_peg['email']))
                        
                        btn_up_peg = st.form_submit_button("Update Data")
                        if btn_up_peg:
                            supabase.table('master_pegawai').update({
                                "nipy": e_nipy, "nama": e_nama, "jabatan": e_jab,
                                "unit_kerja": e_unit, "status_kepegawaian": e_stat,
                                "no_hp": e_hp, "email": e_email
                            }).eq('id', selected_peg_id).execute()
                            st.success("✅ Data berhasil diperbarui!")
                            st.rerun()

            # DELETE
            with act_col3:
                with st.expander("🗑️ Hapus Data", expanded=False):
                    st.warning("Apakah Anda yakin ingin menghapus pegawai ini?")
                    if st.button("🔴 Konfirmasi Hapus Pegawai", key=f"del_peg_{selected_peg_id}"):
                        supabase.table('master_pegawai').delete().eq('id', selected_peg_id).execute()
                        st.success("🗑️ Data pegawai berhasil dihapus!")
                        st.rerun()

    with t2:
        with st.form("f_pegawai_add", clear_on_submit=True):
            st.markdown("##### 📝 Form Tambah Pegawai Baru")
            c1, c2 = st.columns(2)
            nipy = c1.text_input("NIPY*", placeholder="IM-2024-001")
            nama_p = c2.text_input("Nama Lengkap*", placeholder="Nama Lengkap")
            
            c3, c4, c5 = st.columns(3)
            jabatan = c3.text_input("Jabatan")
            unit = c4.text_input("Unit Kerja")
            status_k = c5.selectbox("Status Kepegawaian", ["Tetap", "Tidak Tetap", "Honorer", "Magang", "Lainnya"])
            
            c6, c7 = st.columns(2)
            hp = c6.text_input("No. WhatsApp")
            email = c7.text_input("Alamat Email")
            
            submitted = st.form_submit_button("💾 Simpan Data Pegawai", use_container_width=True)
            if submitted and nipy and nama_p:
                data_peg = {"nipy": nipy, "nama": nama_p, "jabatan": jabatan, "unit_kerja": unit, "no_hp": hp, "email": email, "status_kepegawaian": status_k}
                supabase.table('master_pegawai').insert(data_peg).execute()
                st.success("✅ Data pegawai berhasil ditambahkan!")
                st.rerun()

    with t3:
        st.markdown("##### 1. Unduh Template Excel Standards")
        df_template = pd.DataFrame([{"nipy": "IM-2024-001", "nama": "Ahmad Abdullah", "jabatan": "Guru", "unit_kerja": "SMA", "no_hp": "08123", "email": "a@im.sch.id", "status_kepegawaian": "Tetap"}])
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            df_template.to_excel(writer, sheet_name='Template_Pegawai', index=False)
            
        st.download_button(label="📥 Download Template Excel", data=buf.getvalue(), file_name="Template_Pegawai.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        st.markdown("---")
        up_file = st.file_uploader("Upload Excel Pegawai", type=["xlsx", "xls"])
        if up_file:
            df_up = pd.read_excel(up_file)
            st.dataframe(df_up, use_container_width=True)
            if st.button("🚀 Import Sekarang", use_container_width=True):
                req_cols = ["nipy", "nama", "jabatan", "unit_kerja", "no_hp", "email", "status_kepegawaian"]
                records = df_up[req_cols].fillna("").to_dict(orient="records")
                supabase.table('master_pegawai').upsert(records).execute()
                st.success("🎉 Import Berhasil!")
                st.rerun()

# -------------------------------------------------------------
# MENU 3: FORM SENSUS BARU
# -------------------------------------------------------------
elif menu == "📝 Form Sensus Baru":
    st.markdown('<div class="section-title">📝 Form Pendaftaran Unit Baru</div>', unsafe_allow_html=True)
    with st.form("f_sensus_new", clear_on_submit=True):
        c1, c2 = st.columns(2)
        kode = c1.text_input("Kode Tempat Tinggal*", placeholder="IM-SEWA-01")
        nama = c2.text_input("Nama Unit / Ringkasan Lokasi*", placeholder="Rumdin Block A3")
        
        c3, c4 = st.columns(2)
        jenis = c3.selectbox("Jenis Hunian", ["Rumah Sewa", "Rumah Dinas", "Wisma", "Asrama", "Rumah Pribadi"])
        status_hak = c4.selectbox("Status Kepemilikan", ["Sewa", "Milik Sendiri", "Milik Yayasan"])
        
        alamat = st.text_area("Alamat Lengkap Unit")
        
        st.markdown("---")
        st.markdown("##### 💵 Skema Sewa & Subsidi")
        c_sewa1, c_sewa2 = st.columns(2)
        biaya = c_sewa1.number_input("Biaya Sewa / Tahun (Rp)", min_value=0, value=12000000)
        subsidi = c_sewa2.number_input("Subsidi Yayasan / Tahun (Rp)", min_value=0, value=10000000)
        
        st.markdown("---")
        c5, c6, c7, c8 = st.columns(4)
        pic = c5.text_input("PIC Lapangan")
        penghuni_max = c6.number_input("Kapasitas Penghuni", min_value=1, value=1)
        kondisi = c7.selectbox("Kondisi Unit", ["Baik", "Perlu Perbaikan", "Perlu Renovasi"])
        prio = c8.selectbox("Prioritas Penanganan", ["Rendah", "Sedang", "Tinggi"])
        
        sub_btn = st.form_submit_button("💾 Simpan Data Sensus Unit", use_container_width=True)
        if sub_btn and kode and nama:
            ins_data = {
                "kode": kode, "nama": nama, "jenis": jenis, "status": status_hak, 
                "alamat": alamat, "pic": pic, "penghuni": penghuni_max, 
                "kondisi": kondisi, "prioritas": prio,
                "biaya_sewa_tahun": biaya if status_hak == "Sewa" else 0,
                "subsidi_yayasan": subsidi if status_hak == "Sewa" else 0
            }
            supabase.table('rekap_tempat_tinggal').insert(ins_data).execute()
            st.success("✅ Data unit berhasil disimpan!")
            st.rerun()

# -------------------------------------------------------------
# MENU 4: REKAP TEMPAT TINGGAL (DENGAN CRUD)
# -------------------------------------------------------------
elif menu == "🏢 Rekap Unit & Subsidi":
    st.markdown('<div class="section-title">🏢 Rekap Unit & Aksi Kelola</div>', unsafe_allow_html=True)
    
    if not df_rekap.empty:
        df_display = df_rekap.copy()
        df_display['biaya_sewa_tahun'] = df_display['biaya_sewa_tahun'].apply(lambda x: f"Rp {x:,.0f}")
        df_display['subsidi_yayasan'] = df_display['subsidi_yayasan'].apply(lambda x: f"Rp {x:,.0f}")
        if 'sisa_tanggungan_pegawai' in df_display:
            df_display['sisa_tanggungan_pegawai'] = df_display['sisa_tanggungan_pegawai'].apply(lambda x: f"Rp {x:,.0f}")
            
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("##### ⚙️ Aksi Kelola Unit (View, Edit, Delete)")
        
        unit_opts = {f"{row['kode']} - {row['nama']}": row['id'] for _, row in df_rekap.iterrows()}
        sel_unit_lbl = st.selectbox("Pilih Unit Tempat Tinggal", list(unit_opts.keys()), key="sel_unit")
        sel_unit_id = unit_opts[sel_unit_lbl]
        row_u = df_rekap[df_rekap['id'] == sel_unit_id].iloc[0]

        u_col1, u_col2, u_col3 = st.columns(3)
        
        # VIEW
        with u_col1:
            with st.expander("👁️ View Detail Unit", expanded=False):
                st.write(f"**Kode:** {row_u['kode']}")
                st.write(f"**Nama:** {row_u['nama']}")
                st.write(f"**Jenis:** {row_u['jenis']}")
                st.write(f"**Status:** {row_u['status']}")
                st.write(f"**Alamat:** {row_u['alamat']}")
                st.write(f"**PIC:** {row_u['pic']}")
                st.write(f"**Kondisi:** {row_u['kondisi']}")
                st.write(f"**Biaya Sewa:** Rp {row_u['biaya_sewa_tahun']:,.0f}")
                st.write(f"**Subsidi:** Rp {row_u['subsidi_yayasan']:,.0f}")

        # EDIT
        with u_col2:
            with st.expander("✏️ Edit Unit", expanded=False):
                with st.form(f"f_edit_u_{sel_unit_id}"):
                    eu_kode = st.text_input("Kode Unit", value=str(row_u['kode']))
                    eu_nama = st.text_input("Nama Unit", value=str(row_u['nama']))
                    eu_jenis = st.selectbox("Jenis", ["Rumah Sewa", "Rumah Dinas", "Wisma", "Asrama", "Rumah Pribadi"], index=0)
                    eu_status = st.selectbox("Status Hak", ["Sewa", "Milik Sendiri", "Milik Yayasan"], index=0)
                    eu_alamat = st.text_area("Alamat", value=str(row_u['alamat']))
                    eu_pic = st.text_input("PIC Lapangan", value=str(row_u['pic']))
                    eu_sewa = st.number_input("Biaya Sewa / Thn", value=float(row_u['biaya_sewa_tahun']))
                    eu_subsidi = st.number_input("Subsidi / Thn", value=float(row_u['subsidi_yayasan']))
                    eu_kondisi = st.selectbox("Kondisi Unit", ["Baik", "Perlu Perbaikan", "Perlu Renovasi"])

                    btn_up_u = st.form_submit_button("Update Data Unit")
                    if btn_up_u:
                        supabase.table('rekap_tempat_tinggal').update({
                            "kode": eu_kode, "nama": eu_nama, "jenis": eu_jenis,
                            "status": eu_status, "alamat": eu_alamat, "pic": eu_pic,
                            "biaya_sewa_tahun": eu_sewa, "subsidi_yayasan": eu_subsidi,
                            "kondisi": eu_kondisi
                        }).eq('id', sel_unit_id).execute()
                        st.success("✅ Data Unit diperbarui!")
                        st.rerun()

        # DELETE
        with u_col3:
            with st.expander("🗑️ Hapus Unit", expanded=False):
                st.warning("Hapus unit ini secara permanen?")
                if st.button("🔴 Konfirmasi Hapus Unit", key=f"del_u_{sel_unit_id}"):
                    supabase.table('rekap_tempat_tinggal').delete().eq('id', sel_unit_id).execute()
                    st.success("🗑️ Unit berhasil dihapus!")
                    st.rerun()

# -------------------------------------------------------------
# MENU 5: DATA PENGHUNI (DENGAN CRUD)
# -------------------------------------------------------------
elif menu == "👥 Plotting Penghuni":
    st.markdown('<div class="section-title">👥 Penempatan & Plotting Penghuni</div>', unsafe_allow_html=True)
    
    list_kode = df_rekap["kode"].tolist() if not df_rekap.empty else ["-"]
    list_pegawai = df_pegawai["nama"].tolist() if not df_pegawai.empty else []
    
    with st.expander("➕ Form Plotting Penghuni Baru", expanded=False):
        with st.form("f_penghuni_add", clear_on_submit=True):
            c1, c2 = st.columns(2)
            kode_r = c1.selectbox("Kode Unit Rumah", list_kode)
            nama_p = c2.selectbox("Nama Pegawai", list_pegawai) if list_pegawai else c2.text_input("Nama Penghuni")
                
            c3, c4, c5 = st.columns(3)
            status_p = c3.text_input("Status", value="Pegawai Tetap")
            jab = c4.text_input("Jabatan")
            unit = c5.text_input("Unit Kerja")
            hp = st.text_input("No. HP / WA Active")
            
            btn_submit = st.form_submit_button("💾 Plotting Penghuni")
            if btn_submit and nama_p:
                p_data = {"kode_rumah": kode_r, "nama": nama_p, "status": status_p, "jabatan": jab, "unit": unit, "no_hp": hp, "mulai_menempati": str(date.today())}
                supabase.table('data_penghuni').insert(p_data).execute()
                st.success("✅ Penghuni ditambahkan!")
                st.rerun()

    st.dataframe(df_penghuni, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("##### ⚙️ Aksi Kelola Penghuni (View, Edit, Delete)")
    
    if not df_penghuni.empty:
        penghuni_opts = {f"{row['kode_rumah']} - {row['nama']}": row['id'] for _, row in df_penghuni.iterrows()}
        sel_p_lbl = st.selectbox("Pilih Penghuni", list(penghuni_opts.keys()), key="sel_penghuni")
        sel_p_id = penghuni_opts[sel_p_lbl]
        row_p = df_penghuni[df_penghuni['id'] == sel_p_id].iloc[0]

        p_col1, p_col2, p_col3 = st.columns(3)
        
        # VIEW
        with p_col1:
            with st.expander("👁️ View Detail Penghuni", expanded=False):
                st.write(f"**Kode Unit:** {row_p['kode_rumah']}")
                st.write(f"**Nama:** {row_p['nama']}")
                st.write(f"**Status:** {row_p['status']}")
                st.write(f"**Jabatan:** {row_p['jabatan']}")
                st.write(f"**Unit Kerja:** {row_p['unit']}")
                st.write(f"**No HP:** {row_p['no_hp']}")
                st.write(f"**Mulai Menempati:** {row_p['mulai_menempati']}")

        # EDIT
        with p_col2:
            with st.expander("✏️ Edit Data Penghuni", expanded=False):
                with st.form(f"f_edit_p_{sel_p_id}"):
                    ep_kode = st.selectbox("Kode Unit Rumah", list_kode, index=list_kode.index(row_p['kode_rumah']) if row_p['kode_rumah'] in list_kode else 0)
                    ep_nama = st.text_input("Nama Penghuni", value=str(row_p['nama']))
                    ep_status = st.text_input("Status", value=str(row_p['status']))
                    ep_jab = st.text_input("Jabatan", value=str(row_p['jabatan']))
                    ep_unit = st.text_input("Unit", value=str(row_p['unit']))
                    ep_hp = st.text_input("No HP", value=str(row_p['no_hp']))
                    
                    btn_up_p = st.form_submit_button("Update Data Penghuni")
                    if btn_up_p:
                        supabase.table('data_penghuni').update({
                            "kode_rumah": ep_kode, "nama": ep_nama, "status": ep_status,
                            "jabatan": ep_jab, "unit": ep_unit, "no_hp": ep_hp
                        }).eq('id', sel_p_id).execute()
                        st.success("✅ Data Penghuni diperbarui!")
                        st.rerun()

        # DELETE
        with p_col3:
            with st.expander("🗑️ Hapus Penghuni", expanded=False):
                st.warning("Keluarkan/Hapus data penghuni ini?")
                if st.button("🔴 Konfirmasi Hapus Penghuni", key=f"del_p_{sel_p_id}"):
                    supabase.table('data_penghuni').delete().eq('id', sel_p_id).execute()
                    st.success("🗑️ Penghuni berhasil dihapus!")
                    st.rerun()

# -------------------------------------------------------------
# MENU 6: INVENTARIS ASET (DENGAN CRUD)
# -------------------------------------------------------------
elif menu == "📦 Inventaris & Aset":
    st.markdown('<div class="section-title">📦 Inventaris & Aset Unit</div>', unsafe_allow_html=True)
    
    list_kode = df_rekap["kode"].tolist() if not df_rekap.empty else ["-"]
    
    with st.expander("➕ Registrasi Aset Inventaris Baru", expanded=False):
        with st.form("f_inv_add", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            kode_r = c1.selectbox("Kode Unit", list_kode)
            nama_b = c2.text_input("Nama Barang / Aset*")
            jumlah = c3.number_input("Jumlah Unit", min_value=1, value=1)
            
            c4, c5 = st.columns(2)
            kondisi_b = c4.selectbox("Kondisi", ["Baik", "Rusak Ringan", "Rusak Berat"])
            catatan_b = c5.text_input("Catatan Tambahan")
            
            btn_inv = st.form_submit_button("💾 Simpan Aset")
            if btn_inv and nama_b:
                inv_data = {"kode_rumah": kode_r, "barang": nama_b, "jumlah": jumlah, "kondisi": kondisi_b, "catatan": catatan_b}
                supabase.table('inventaris_aset').insert(inv_data).execute()
                st.success("✅ Aset didaftarkan!")
                st.rerun()

    st.dataframe(df_inventaris, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("##### ⚙️ Aksi Kelola Inventaris (View, Edit, Delete)")
    
    if not df_inventaris.empty:
        inv_opts = {f"{row['kode_rumah']} - {row['barang']}": row['id'] for _, row in df_inventaris.iterrows()}
        sel_inv_lbl = st.selectbox("Pilih Barang Inventaris", list(inv_opts.keys()), key="sel_inv")
        sel_inv_id = inv_opts[sel_inv_lbl]
        row_i = df_inventaris[df_inventaris['id'] == sel_inv_id].iloc[0]

        i_col1, i_col2, i_col3 = st.columns(3)
        
        # VIEW
        with i_col1:
            with st.expander("👁️ View Detail Aset", expanded=False):
                st.write(f"**Kode Rumah:** {row_i['kode_rumah']}")
                st.write(f"**Nama Barang:** {row_i['barang']}")
                st.write(f"**Jumlah Unit:** {row_i['jumlah']}")
                st.write(f"**Kondisi:** {row_i['kondisi']}")
                st.write(f"**Catatan:** {row_i['catatan']}")

        # EDIT
        with i_col2:
            with st.expander("✏️ Edit Aset", expanded=False):
                with st.form(f"f_edit_inv_{sel_inv_id}"):
                    ei_kode = st.selectbox("Kode Rumah", list_kode, index=list_kode.index(row_i['kode_rumah']) if row_i['kode_rumah'] in list_kode else 0)
                    ei_barang = st.text_input("Nama Barang", value=str(row_i['barang']))
                    ei_jumlah = st.number_input("Jumlah", value=int(row_i['jumlah']), min_value=1)
                    ei_kondisi = st.selectbox("Kondisi", ["Baik", "Rusak Ringan", "Rusak Berat"])
                    ei_catatan = st.text_input("Catatan", value=str(row_i['catatan']))
                    
                    btn_up_inv = st.form_submit_button("Update Data Aset")
                    if btn_up_inv:
                        supabase.table('inventaris_aset').update({
                            "kode_rumah": ei_kode, "barang": ei_barang,
                            "jumlah": ei_jumlah, "kondisi": ei_kondisi, "catatan": ei_catatan
                        }).eq('id', sel_inv_id).execute()
                        st.success("✅ Aset diperbarui!")
                        st.rerun()

        # DELETE
        with i_col3:
            with st.expander("🗑️ Hapus Aset", expanded=False):
                st.warning("Hapus inventaris ini?")
                if st.button("🔴 Konfirmasi Hapus Aset", key=f"del_inv_{sel_inv_id}"):
                    supabase.table('inventaris_aset').delete().eq('id', sel_inv_id).execute()
                    st.success("🗑️ Aset dihapus!")
                    st.rerun()

# -------------------------------------------------------------
# MENU 7: LOG MAINTENANCE (DENGAN CRUD)
# -------------------------------------------------------------
elif menu == "🛠️ Log Maintenance":
    st.markdown('<div class="section-title">🛠️ Pemeliharaan & Perbaikan Unit</div>', unsafe_allow_html=True)
    
    list_kode = df_rekap["kode"].tolist() if not df_rekap.empty else ["-"]
    
    with st.expander("➕ Catat Task Maintenance Baru", expanded=False):
        with st.form("f_maint_add", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            tgl = c1.date_input("Tanggal Perbaikan", value=date.today())
            kode_r = c2.selectbox("Kode Unit", list_kode)
            jenis_p = c3.text_input("Jenis Perbaikan/Kerusakan*")
            
            c4, c5, c6 = st.columns(3)
            biaya = c4.number_input("Estimasi/Realisasi Biaya (Rp)", min_value=0, value=0)
            vendor = c5.text_input("Vendor / Teknisi")
            pic_m = c6.text_input("PIC Lapangan")
            
            status_m = st.selectbox("Status", ["Pending", "Diproses", "Selesai"])
            
            btn_maint = st.form_submit_button("💾 Catat Maintenance")
            if btn_maint and jenis_p:
                m_data = {"tanggal": str(tgl), "kode_rumah": kode_r, "jenis_perbaikan": jenis_p, "biaya": biaya, "vendor": vendor, "pic": pic_m, "status": status_m}
                supabase.table('maintenance_log').insert(m_data).execute()
                st.success("✅ Log maintenance disimpan!")
                st.rerun()

    if not df_maint.empty:
        df_maint_disp = df_maint.copy()
        if 'biaya' in df_maint_disp:
            df_maint_disp['biaya'] = df_maint_disp['biaya'].apply(lambda x: f"Rp {x:,.0f}")
        st.dataframe(df_maint_disp, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("##### ⚙️ Aksi Kelola Maintenance (View, Edit, Delete)")
        
        maint_opts = {f"[{row['tanggal']}] {row['kode_rumah']} - {row['jenis_perbaikan']}": row['id'] for _, row in df_maint.iterrows()}
        sel_m_lbl = st.selectbox("Pilih Log Maintenance", list(maint_opts.keys()), key="sel_maint")
        sel_m_id = maint_opts[sel_m_lbl]
        row_m = df_maint[df_maint['id'] == sel_m_id].iloc[0]

        m_col1, m_col2, m_col3 = st.columns(3)
        
        # VIEW
        with m_col1:
            with st.expander("👁️ View Detail Maintenance", expanded=False):
                st.write(f"**Tanggal:** {row_m['tanggal']}")
                st.write(f"**Kode Unit:** {row_m['kode_rumah']}")
                st.write(f"**Perbaikan:** {row_m['jenis_perbaikan']}")
                st.write(f"**Biaya:** Rp {row_m['biaya']:,.0f}")
                st.write(f"**Vendor:** {row_m['vendor']}")
                st.write(f"**PIC:** {row_m['pic']}")
                st.write(f"**Status:** {row_m['status']}")

        # EDIT
        with m_col2:
            with st.expander("✏️ Edit Status / Data", expanded=False):
                with st.form(f"f_edit_m_{sel_m_id}"):
                    em_kode = st.selectbox("Kode Unit", list_kode, index=list_kode.index(row_m['kode_rumah']) if row_m['kode_rumah'] in list_kode else 0)
                    em_jenis = st.text_input("Jenis Perbaikan", value=str(row_m['jenis_perbaikan']))
                    em_biaya = st.number_input("Biaya (Rp)", value=float(row_m['biaya']))
                    em_vendor = st.text_input("Vendor", value=str(row_m['vendor']))
                    em_pic = st.text_input("PIC", value=str(row_m['pic']))
                    em_status = st.selectbox("Status", ["Pending", "Diproses", "Selesai"])
                    
                    btn_up_m = st.form_submit_button("Update Log Maintenance")
                    if btn_up_m:
                        supabase.table('maintenance_log').update({
                            "kode_rumah": em_kode, "jenis_perbaikan": em_jenis,
                            "biaya": em_biaya, "vendor": em_vendor, "pic": em_pic, "status": em_status
                        }).eq('id', sel_m_id).execute()
                        st.success("✅ Log Maintenance diperbarui!")
                        st.rerun()

        # DELETE
        with m_col3:
            with st.expander("🗑️ Hapus Maintenance", expanded=False):
                st.warning("Hapus log perbaikan ini?")
                if st.button("🔴 Konfirmasi Hapus Maintenance", key=f"del_m_{sel_m_id}"):
                    supabase.table('maintenance_log').delete().eq('id', sel_m_id).execute()
                    st.success("🗑️ Log perbaikan dihapus!")
                    st.rerun()

# -------------------------------------------------------------
# MENU 8: EXPORT CENTER
# -------------------------------------------------------------
elif menu == "📥 Export Center":
    st.markdown('<div class="section-title">📥 Export Master Laporan Excel</div>', unsafe_allow_html=True)
    
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
        file_name=f"Laporan_Master_Insan_Madani_{date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )