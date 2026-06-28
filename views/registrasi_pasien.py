import streamlit as st
import datetime
import random
import time  # <-- Ditambahkan untuk jeda refresh halaman
from utils.db import supabase

# Inisialisasi Zona Waktu Asia/Jakarta (WIB = UTC+7)
TZ_WIB = datetime.timezone(datetime.timedelta(hours=7))

def generate_no_rm():
    # Membuat No RM otomatis berdasarkan tanggal hari ini di zona waktu WIB
    now = datetime.datetime.now(TZ_WIB)
    date_str = now.strftime("%d%m%y")
    rand_num = random.randint(10000, 99999)
    return f"RM{date_str}{rand_num}"

def render_registrasi_pasien():
    # ============================================================
    # 1. SUNTIKAN CUSTOM CSS – SAMA DENGAN DASHBOARD & UBAH PASIEN
    # ============================================================
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=400;500;600;700;800&display=swap');
        
        /* Reset Font Global & Latar Belakang Aplikasi */
        html, body, [class*="css"], .stApp {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
        }
        
        /* Desain Header Utama (Hitam Pekat & Elegan) */
        .main-title {
            font-size: 32px;
            font-weight: 800;
            color: #000000 !important;
            margin-bottom: 2px;
            letter-spacing: -0.5px;
        }
        .sub-title {
            font-size: 14px;
            color: #000000 !important;
            opacity: 0.8;
            margin-bottom: 25px;
        }
        
        /* Mengubah Container Form Menjadi Kartu Putih Elegan (SaaS Style) */
        div[data-testid="stForm"] {
            background: #ffffff !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.04), 0 8px 10px -6px rgba(15, 23, 42, 0.04) !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
        }

        /* Teks di dalam Input Field, Dropdown, Date Input & Textarea */
        .stTextInput input, .stSelectbox div, .stTextArea textarea, div[data-testid="stDateInput"] input {
            color: #000000 !important;
            border-radius: 10px !important;
            background-color: #f8fafc !important;
            font-weight: 600 !important;
        }
        
        /* Gaya Label Form */
        label[data-testid="stWidgetLabel"] {
            color: #000000 !important;
            font-weight: 700 !important;
            font-size: 13px !important;
            margin-bottom: 6px !important;
        }

        /* WORKAROUND KHUSUS UNTUK TOMBOL SUBMIT FORM */
        div.stFormSubmitButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            height: 46px !important;
            background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%) !important;
            color: #ffffff !important;
            border: none !important;
            transition: all 0.2s ease !important;
        }
        
        /* Paksa teks tombol form submit agar tetap putih pekat */
        div.stFormSubmitButton > button p,
        div.stFormSubmitButton > button span {
            color: #ffffff !important;
        }

        /* Paksa seluruh teks judul di area utama agar menjadi hitam */
        [data-testid="stMainBlockContainer"] h3 {
            color: #000000 !important;
            font-weight: 800 !important;
            margin-bottom: 20px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. HEADER UTAMA ---
    st.markdown('<p class="main-title">➕ Registrasi Pasien Baru</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Daftarkan data rekam medis pasien baru ke dalam sistem antrean laboratorium secara real-time</p>', unsafe_allow_html=True)

    # --- 3. AMBIL DATA DOKTER SECARA AMAN (ANTI-CRASH) ---
    list_dokter = []
    try:
        dokter_response = supabase.table("doctors").select("nama_dokter").execute()
        if dokter_response.data:
            list_dokter = [d['nama_dokter'] for d in dokter_response.data]
    except Exception:
        # Jika tabel 'doctors' tidak ditemukan (PGRST205) atau error lain, list dikosongkan secara aman
        list_dokter = []

    # Inisialisasi nomor RM otomatis di session state menggunakan zona waktu WIB
    if "temp_no_rm" not in st.session_state:
        st.session_state.temp_no_rm = generate_no_rm()

    # --- 4. PANEL FORM REGISTRASI (SAAS CARD STYLE) ---
    with st.form("form_registrasi", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Nomor Rekam Medis (RM) - Otomatis", value=st.session_state.temp_no_rm, disabled=True)
            nama_pasien = st.text_input("Nama Lengkap Pasien *", placeholder="Masukkan nama lengkap pasien...")
            tgl_lahir = st.date_input("Tanggal Lahir", value=datetime.date(2000, 1, 1))
            gender = st.selectbox("Jenis Kelamin", ["laki-laki", "perempuan"])
            gol_darah = st.selectbox("Golongan Darah", ["A", "B", "AB", "O", "-"])
            
        with col2:
            # FITUR DINAMIS: Jika ada data di tabel doctors pakai selectbox, jika tidak ada/error pakai text_input biasa
            if list_dokter:
                dokter = st.selectbox("Dokter Pengirim / Pengirim *", options=list_dokter)
            else:
                dokter = st.text_input("Dokter Pengirim / Pengirim *", value="dr. Anggraeni Zaenab", placeholder="Ketik nama dokter pengirim...")
                
            kategori_pasien = st.selectbox("Kategori Pasien", ["UMUM", "BPJS", "KERJASAMA", "GRATIS"])
            telepon = st.text_input("Nomor Telepon/HP", placeholder="Contoh: 081234xxxxxx")
            alamat = st.text_area("Alamat Tinggal Pasien", placeholder="Tuliskan alamat lengkap domisili...")

        st.markdown("<p style='color: #dc2626; font-size: 12px; font-weight: 600;'>* Wajib diisi</p>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("Daftarkan & Simpan Pasien", use_container_width=True)

        if submit_btn:
            if not nama_pasien.strip() or not dokter.strip():
                st.error("⚠️ Nama Pasien dan Dokter Pengirim tidak boleh dibiarkan kosong!")
            else:
                try:
                    # Ambil waktu registrasi saat ini tepat di Zona Waktu WIB (Jam, Menit, Detik Indonesia)
                    waktu_sekarang_wib = datetime.datetime.now(TZ_WIB)
                    string_tgl_registrasi = waktu_sekarang_wib.strftime("%Y-%m-%d %H:%M:%S")

                    # Siapkan payload data untuk dimasukkan ke tabel 'patients' Supabase
                    patient_data = {
                        "no_rm": st.session_state.temp_no_rm,
                        "nama_pasien": nama_pasien,
                        "tgl_lahir": str(tgl_lahir),
                        "gender": gender,
                        "gol_darah": gol_darah,
                        "dokter": dokter,
                        "kategori_pasien": kategori_pasien,
                        "telepon": telepon,
                        "alamat": alamat,
                        "status": "Mengantri",
                        "tgl_registrasi": string_tgl_registrasi, # Mengirimkan waktu WIB akurat ke database
                        "is_deleted": False,
                        # CRITICAL FIX: Mengunci kepemilikan pasien berdasarkan siapa akun analis yang mendaftarkannya
                        "created_by": st.session_state.get('username', 'Analis')
                    }
                    
                    # Insert data ke database Supabase
                    supabase.table("patients").insert(patient_data).execute()
                    
                    # 1. Mengeluarkan NOTIFIKASI/NOTE Berhasil yang Jelas di Layar
                    st.success(f"🎉 **Registrasi Berhasil!** Pasien bernama **{nama_pasien}** telah terdaftar dengan Nomor **{st.session_state.temp_no_rm}**.")
                    
                    # Reset nomor RM baru untuk antrean pasien selanjutnya (siap digunakan nanti)
                    st.session_state.temp_no_rm = generate_no_rm()
                    
                    # 2. Mengubah target halaman session state menjadi Dashboard Analis
                    st.session_state.current_page = "Dashboard Analis"
                    
                    # 3. Beri jeda waktu 1.5 detik agar pengguna sempat membaca Note Sukses di atas
                    time.sleep(1.5)
                    
                    # 4. Trigger Rerun untuk mengalihkan halaman secara otomatis
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Gagal menyimpan data ke database: {str(e)}")