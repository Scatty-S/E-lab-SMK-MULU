import streamlit as st
from utils.db import supabase

def render_login():
    # ============================================================
    # 1. CSS KUSTOM FIXED – PAKSA LIGHT THEME SAMPAI KE LAPISAN DALAM KOTAK
    # ============================================================
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
        
        /* Reset font global aplikasi & Background luar */
        html, body, [class*="css"], .stApp {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
        }

        /* Kartu Form Login */
        div[data-testid="stForm"] {
            background: #ffffff !important;
            border-radius: 24px !important;
            padding: 2.5rem 2rem !important;
            box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.08) !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
            max-width: 420px;
            margin: 0 auto;
        }

        /* Desain Logo Brand */
        .company-logo {
            text-align: center;
            margin-bottom: 0.8rem;
        }
        .company-logo span {
            font-size: 2.2rem;
            font-weight: 700;
            color: #000000 !important;
            background: #f1f5f9;
            padding: 0.4rem 1.2rem;
            border-radius: 50px;
            display: inline-block;
        }

        /* Header Teks Login */
        .login-header {
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .login-header h1 {
            font-size: 1.8rem;
            font-weight: 700;
            color: #000000 !important;
            margin: 0;
        }
        .login-header p {
            font-size: 0.85rem;
            color: #334155 !important;
            margin-top: 0.3rem;
        }

        /* Label Input (Username, Password, Hak Akses) */
        div[data-testid="stForm"] label p {
            color: #000000 !important;
            font-weight: 600 !important;
        }

        /* Teks di dalam Kotak Input Teks (Username & Password) */
        .stTextInput input {
            color: #000000 !important;
            border-radius: 12px !important;
            border: 1.5px solid #cbd5e1 !important;
            background-color: #f8fafc !important;
            transition: all 0.2s ease;
        }
        .stTextInput input:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1) !important;
        }

        /* ============================================================
           FIX ENGINE UTAMA: KOTAK SELECTBOX (KULIT LUAR & LAPISAN DALAM)
           ============================================================ */
        /* 1. Mengatur kulit luar kotak selectbox */
        .stSelectbox div[data-baseweb="select"] {
            border-radius: 12px !important;
            border: 1.5px solid #cbd5e1 !important;
            background-color: #f8fafc !important;
        }
        
        /* 2. FIX: Mengatur komponen internal div (lapisan dalam) yang biasanya jadi hitam */
        .stSelectbox div[data-baseweb="select"] > div {
            background-color: #f8fafc !important; /* Paksa lapisan dalam jadi putih terang */
            border: none !important;
        }
        
        /* 3. Paksa seluruh teks yang berada di dalam kotak tertutup menjadi HITAM PEKAT */
        .stSelectbox div[data-baseweb="select"] div,
        .stSelectbox div[data-baseweb="select"] span,
        .stSelectbox div[data-baseweb="select"] p {
            color: #000000 !important;
            font-weight: 600 !important;
        }
        
        /* 4. Warnai ulang ikon panah kecil dropdown menjadi hitam */
        .stSelectbox div[data-baseweb="select"] svg {
            color: #000000 !important;
            fill: #000000 !important;
        }

        /* ============================================================
           POPOVER LIST (PILIHAN DROPDOWN SAAT DIKLIK)
           ============================================================ */
        div[data-baseweb="popover"] {
            background-color: #ffffff !important;
        }
        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li,
        div[data-baseweb="popover"] div {
            background: #ffffff !important; 
            color: #000000 !important;      
        }
        div[data-baseweb="popover"] li:hover,
        div[data-baseweb="popover"] div:hover {
            background: #e2e8f0 !important; 
            color: #000000 !important;
        }
        /* ============================================================ */

        /* Teks Checkbox (Ingat saya) */
        div[data-testid="stCheckbox"] label p {
            color: #000000 !important;
            font-weight: 500 !important;
        }

        /* Tombol Login Utama */
        div[data-testid="stFormSubmitButton"] button {
            border-radius: 12px !important;
            padding: 0.7rem 1.5rem !important;
            font-weight: 600 !important;
            background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%) !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25) !important;
            transition: all 0.2s ease-in-out !important;
            width: 100% !important;
        }
        div[data-testid="stFormSubmitButton"] button p,
        div[data-testid="stFormSubmitButton"] button span {
            color: #ffffff !important;
        }
        
        div[data-testid="stFormSubmitButton"] button:hover {
            background: linear-gradient(135deg, #4338ca 0%, #312e81 100%) !important;
            color: #ffffff !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 8px 20px rgba(79, 70, 229, 0.35) !important;
        }
        div[data-testid="stFormSubmitButton"] button:hover p,
        div[data-testid="stFormSubmitButton"] button:hover span {
            color: #ffffff !important;
        }

        /* Footer */
        .login-footer {
            text-align: center;
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 1px solid #e2e8f0;
            font-size: 0.75rem;
            color: #475569 !important;
            line-height: 1.5;
        }
        .login-footer span {
            color: #64748b !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ============================================================
    # 2. TATA LETAK & FORM LOGIN
    # ============================================================
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown('<div style="height: 5vh;"></div>', unsafe_allow_html=True)
        
        with st.form("form_login"):
            st.markdown('<div class="company-logo"><span>E-Lab</span></div>', unsafe_allow_html=True)
            st.markdown(
                """
                <div class="login-header">
                    <h1>Selamat Datang</h1>
                    <p>Sistem Informasi & Manajemen Laboratorium SMK MUHAMMADIYAH LUMAJANG</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Input Fields
            username_input = st.text_input("Username", placeholder="Masukkan username Anda...").strip()
            password_input = st.text_input("Password", type="password", placeholder="Masukkan password Anda...").strip()
            
            role_input = st.selectbox(
                "Hak Akses Sistem",
                ["Analis", "Admin"],
                help="Pilih peran sesuai dengan jabatan Anda"
            )
            
            remember_me = st.checkbox("Ingat saya di perangkat ini", value=False)
            
            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
            
            # Tombol Submit Form
            submit_btn = st.form_submit_button("MASUK KE SISTEM", use_container_width=True)

            # Logika Aksi Supabase (Tetap utuh)
            if submit_btn:
                if not username_input or not password_input:
                    st.error("Username dan Password tidak boleh kosong!")
                else:
                    try:
                        role_value = role_input.lower()
                        check_empty = supabase.table("users").select("id", count="exact").limit(1).execute()

                        if not check_empty.data:
                            default_users = [
                                {"username": "Ahmad Dani", "password": "analis123", "role": "analis"},
                                {"username": "Admin Lab", "password": "admin123", "role": "admin"},
                            ]
                            supabase.table("users").insert(default_users).execute()

                        response = (
                            supabase.table("users")
                            .select("*")
                            .ilike("username", username_input)
                            .eq("password", password_input)
                            .eq("role", role_value)
                            .execute()
                        )

                        user_data = response.data

                        if user_data:
                            st.session_state.is_logged_in = True
                            st.session_state.username = user_data[0]["username"]
                            st.session_state.role = user_data[0]["role"]

                            if st.session_state.role == "analis":
                                st.session_state.current_page = "Dashboard Analis"
                            elif st.session_state.role == "admin":
                                st.session_state.current_page = "Dashboard Admin"

                            st.success(f"Login Berhasil! Selamat bekerja, {st.session_state.username}.")
                            st.rerun()
                        else:
                            st.error("Akses Ditolak! Kombinasi Akun dan Peran tidak terdaftar.")

                    except Exception as e:
                        st.error(f"Kendala Database: {str(e)}")

            # Footer
            st.markdown(
                """
                <div class="login-footer">
                    E-Lab System by FadhG7<br>
                    <span>Seluruh aktivitas log disinkronisasi demi keamanan data pasien.</span>
                </div>
                """, 
                unsafe_allow_html=True
            )