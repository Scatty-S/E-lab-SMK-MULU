import streamlit as st
import importlib
import inspect
import traceback

# 1. Set konfigurasi halaman wajib di paling atas script
st.set_page_config(
    page_title="E-Lab SMK Muhammadiyah Lumajang",
    page_icon="🧪",
    layout="wide"
)

# SUNTIKAN CUSTOM CSS KHUSUS SIDEBAR NAVIGASI MODERN (HOVER STYLE)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=400;500;600;700;800&display=swap');
    
    /* Setup Font Global untuk Sidebar */
    [data-testid="stSidebar"] * {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* GAYA KUSTOM UNTUK TOMBOL NAVIGASI DI SIDEBAR */
    div[data-testid="stSidebar"] div.stButton > button {
        text-align: left !important;
        align-items: center !important;
        justify-content: flex-start !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        height: auto !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        margin-bottom: 6px !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
    }
    
    /* Tombol Menu yang sedang TIDAK AKTIF (Secondary) */
    div[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
        background-color: transparent !important;
        color: #475569 !important; /* Warna teks abu-abu elegan */
    }
    
    /* EFEK HOVER: Saat kursor berada di atas menu yang tidak aktif */
    div[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
        background-color: #f1f5f9 !important; /* Latar belakang abu-abu soft */
        color: #0f172a !important; /* Teks berubah menjadi hitam pekat */
        padding-left: 20px !important; /* Efek bergeser sedikit ke kanan saat dihover */
    }
    
    /* Tombol Menu yang sedang AKTIF (Primary) */
    div[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15) !important;
    }
    
    /* Memastikan teks icon & label di tombol aktif berwarna putih bersih */
    div[data-testid="stSidebar"] div.stButton > button[kind="primary"] p,
    div[data-testid="stSidebar"] div.stButton > button[kind="primary"] span {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)


# FUNGSI SAKTI: Otomatis mendeteksi fungsi render halaman dan menampilkan error detail langsung di UI web
def auto_load_view(nama_modul):
    try:
        mod = importlib.import_module(f"views.{nama_modul}")
        fungsi_list = [
            obj for name, obj in inspect.getmembers(mod, inspect.isfunction)
            if obj.__module__ == mod.__name__ and not name.startswith('_')
        ]
        
        if not fungsi_list:
            fungsi_list = [obj for name, obj in inspect.getmembers(mod, inspect.isfunction) if not name.startswith('_')]
        
        if fungsi_list:
            for f in fungsi_list:
                nama_f = f.__name__.lower()
                if 'render' in nama_f or nama_modul.replace('_', '') in nama_f or nama_f in ['main', 'proses', 'dashboard']:
                    return f
            return fungsi_list[0]
        else:
            return lambda: st.error(f"⚠️ Sistem tidak menemukan fungsi apa pun di dalam file `views/{nama_modul}.py`.")
    except Exception as e:
        # Mengambil pesan error mendalam (Traceback) dari file views yang rusak
        error_detail = traceback.format_exc()
        
        # Membuat fungsi darurat yang akan memunculkan detail kerusakannya langsung di layar browser
        def tampilkan_error_di_layar():
            st.error(f"❌ Gagal memuat file `views/{nama_modul}.py` karena ada error di dalam file tersebut.")
            st.subheader("🔍 Detail Kerusakan Internal File:")
            st.info("Buka file tersebut di text editor Anda, lihat baris yang ditunjukkan di bawah ini, lalu perbaiki kodenya.")
            st.code(error_detail, language="python")
            
        return tampilkan_error_di_layar

# Memuat halaman secara dinamis
render_login = auto_load_view("login")
render_dashboard_analis = auto_load_view("dashboard_analis")
render_registrasi_pasien = auto_load_view("registrasi_pasien")
render_proses_lab = auto_load_view("proses_lab")
render_ubah_pasien = auto_load_view("ubah_pasien")
render_dashboard_admin = auto_load_view("dashboard_admin")
render_riwayat_hapus = auto_load_view("riwayat_hapus")


# 2. INISIALISASI SESSION STATE
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "Login"
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = None


# 3. LOGIKA GERBANG LOGIN
if not st.session_state.is_logged_in:
    render_login()
else:
    # TAMPILAN SIDEBAR NAVIGASI
    st.sidebar.markdown("### 🧪 E-Lab System")
    st.sidebar.write(f"Selamat Datang, **{st.session_state.username}**")
    st.sidebar.caption(f"Hak Akses: `{st.session_state.role.upper()}`")
    st.sidebar.markdown("---")
    
    # --- HUB NAVIGASI KUSTOM (HOVER & BUTTON STYLE) ---
    
    # Menu Navigasi Berdasarkan Role Pengguna (Analis)
    if st.session_state.role == "analis":
        if st.session_state.current_page == "Ubah Pasien":
            st.sidebar.warning("⚠️ Sedang Mengubah Data Pasien")
            if st.sidebar.button("⬅️ Kembali ke Dashboard", use_container_width=True, type="primary"):
                st.session_state.current_page = "Dashboard Analis"
                st.rerun()
        else:
            st.sidebar.markdown("<p style='font-size:11px; font-weight:700; color:#64748b; letter-spacing:0.5px; margin-bottom:10px;'>NAVIGASI ANALIS</p>", unsafe_allow_html=True)
            
            # Menu 1: Dashboard Pasien
            m1_type = "primary" if st.session_state.current_page == "Dashboard Analis" else "secondary"
            if st.sidebar.button("📊 Dashboard Pasien", type=m1_type, use_container_width=True):
                st.session_state.current_page = "Dashboard Analis"
                st.rerun()
                
            # Menu 2: Registrasi Pasien Baru
            m2_type = "primary" if st.session_state.current_page == "Registrasi Pasien" else "secondary"
            if st.sidebar.button("📝 Registrasi Pasien Baru", type=m2_type, use_container_width=True):
                st.session_state.current_page = "Registrasi Pasien"
                st.rerun()
                
            # Menu 3: Input Hasil Lab
            m3_type = "primary" if st.session_state.current_page == "Proses Lab" else "secondary"
            if st.sidebar.button("🔬 Input Hasil Lab", type=m3_type, use_container_width=True):
                st.session_state.current_page = "Proses Lab"
                st.rerun()
            
    # Menu Navigasi Berdasarkan Role Pengguna (Admin)
    elif st.session_state.role == "admin":
        st.sidebar.markdown("<p style='font-size:11px; font-weight:700; color:#64748b; letter-spacing:0.5px; margin-bottom:10px;'>NAVIGASI ADMIN</p>", unsafe_allow_html=True)
        
        # Menu 1: Manajemen Akun
        a1_type = "primary" if st.session_state.current_page == "Dashboard Admin" else "secondary"
        if st.sidebar.button("👑 Manajemen Akun", type=a1_type, use_container_width=True):
            st.session_state.current_page = "Dashboard Admin"
            st.rerun()
            

    # Tombol Keluar (Logout)
    st.sidebar.markdown("---")
    if st.sidebar.button("Keluar / Logout", type="secondary", use_container_width=True):
        st.session_state.is_logged_in = False
        st.session_state.current_page = "Login"
        st.session_state.username = ""
        st.session_state.role = None
        st.rerun()

    # 4. ROUTING / RENDER HALAMAN YANG SEDANG AKTIF
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.current_page == "Dashboard Analis":
        render_dashboard_analis()
    elif st.session_state.current_page == "Registrasi Pasien":
        render_registrasi_pasien()
    elif st.session_state.current_page == "Proses Lab":
        render_proses_lab()
    elif st.session_state.current_page == "Ubah Pasien":
        render_ubah_pasien()
    elif st.session_state.current_page == "Dashboard Admin":
        render_dashboard_admin()
