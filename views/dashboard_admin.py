import streamlit as st
from utils.db import supabase

def render_dashboard_admin():
    # ============================================================
    # SUNTIKAN CUSTOM CSS FIXED – PAKSA LIGHT THEME HIGH CONTRAST (SCOPED)
    # ============================================================
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=400;500;600;700;800&display=swap');
        
        /* 1. Paksa Background Utama Hanya pada Area Kerja Utama */
        [data-testid="stMainBlockContainer"] {
            background-color: #f8fafc !important;
        }
        
        /* Fix Top Header Streamlit */
        [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        
        /* 2. Paksa Semua Jenis Tulisan Konten Utama Menjadi Hitam Pekat */
        [data-testid="stMainBlockContainer"] h1, 
        [data-testid="stMainBlockContainer"] h2, 
        [data-testid="stMainBlockContainer"] h3, 
        [data-testid="stMainBlockContainer"] h4, 
        [data-testid="stMainBlockContainer"] h5, 
        [data-testid="stMainBlockContainer"] h6, 
        [data-testid="stMainBlockContainer"] label, 
        [data-testid="stMainBlockContainer"] p, 
        [data-testid="stMainBlockContainer"] span, 
        [data-testid="stMainBlockContainer"] strong, 
        [data-testid="stMainBlockContainer"] small {
            color: #0f172a !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        
        /* 3. Kartu Putih Kontainer Premium */
        [data-testid="stMainBlockContainer"] div[data-testid="stContainer"] {
            background-color: #ffffff !important;
            border-radius: 14px !important;
            padding: 1.5rem !important;
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.05) !important;
            border: 1px solid #e2e8f0 !important;
            margin-bottom: 16px !important;
        }
        
        /* 4. Desain Kolom Input Teks & Angka & Selectbox */
        [data-testid="stMainBlockContainer"] .stTextInput input, 
        [data-testid="stMainBlockContainer"] .stSelectbox div[data-baseweb="select"] {
            color: #0f172a !important;
            font-weight: 600 !important;
            background-color: #f1f5f9 !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
        }
        
        /* ============================================================
           5. HOVER ENGINE BUTTON (FIXED ANTI BENTROK WARNA)
           ============================================================ */
        /* Kondisi Awal Tombol Biasa - Latar Terang & Teks Hitam Pekat */
        [data-testid="stMainBlockContainer"] .stButton > button {
            color: #0f172a !important;            /* Teks: Hitam */
            background-color: #f1f5f9 !important; /* Latar: Abu-abu Terang */
            border: 2px solid #cbd5e1 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease-in-out !important;
        }
        /* Pastikan teks inner bunderan/span ikut hitam */
        [data-testid="stMainBlockContainer"] .stButton > button p,
        [data-testid="stMainBlockContainer"] .stButton > button span {
            color: #0f172a !important;
        }

        /* Kondisi Saat Hover Tombol Biasa - Teks Tetap Hitam, Hanya BG Berubah */
        [data-testid="stMainBlockContainer"] .stButton > button:hover {
            color: #0f172a !important;            /* Teks: Tetap Hitam */
            background-color: #e2e8f0 !important; /* Latar: Berubah sedikit gelap */
            border: 2px solid #94a3b8 !important;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.1) !important;
        }
        [data-testid="stMainBlockContainer"] .stButton > button:hover p,
        [data-testid="stMainBlockContainer"] .stButton > button:hover span {
            color: #0f172a !important;
        }
        
        /* Kondisi Awal Tombol Hapus (Danger) - Latar Merah Terang & Teks Merah Tua */
        .btn-danger > div > button {
            background-color: #fee2e2 !important; /* Latar: Merah sangat muda */
            color: #991b1b !important;            /* Teks: Merah Tua Kontras */
            border: 2px solid #fca5a5 !important;
        }
        .btn-danger > div > button p,
        .btn-danger > div > button span {
            color: #991b1b !important;
        }
        
        /* Kondisi Saat Hover Tombol Hapus - Teks Tetap, Hanya BG Berubah */
        .btn-danger > div > button:hover {
            background-color: #fecaca !important; /* Latar: Merah agak gelap */
            color: #991b1b !important;            /* Teks: Tetap Merah Tua */
            border: 2px solid #f87171 !important;
        }
        .btn-danger > div > button:hover p,
        .btn-danger > div > button:hover span {
            color: #991b1b !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2>⚙️ Panel Kendali Utama Admin</h2>", unsafe_allow_html=True)
    st.caption("Selamat datang di sistem manajemen pusat. Kontrol hak akses, data dokter, dan pantau performa lab.")
    
    tab_ringkasan, tab_user, tab_dokter = st.tabs([
        "📊 Ringkasan & Pendapatan", 
        "👥 Manajemen Pengguna (Login)", 
        "🩻 Manajemen Dokter Pengirim"
    ])

    # ============================================================
    # TAB 1: RINGKASAN & PENDAPATAN CLINIC REAL-TIME
    # ============================================================
    with tab_ringkasan:
        st.markdown("### 📈 Performa & Pendapatan Laboratorium")
        
        try:
            res_patients = supabase.table("patients").select("id", "status").execute()
            res_lab = supabase.table("pemeriksaan_lab").select("tarif").execute()
            res_users = supabase.table("users").select("id").execute()
            
            total_pasien = len(res_patients.data) if res_patients.data else 0
            total_selesai = len([p for p in res_patients.data if p.get("status") == "Selesai"]) if res_patients.data else 0
            total_user_sistem = len(res_users.data) if res_users.data else 0
            total_omset = sum([float(item.get("tarif", 0)) for item in res_lab.data]) if res_lab.data else 0.0
            
            with st.container(border=True):
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    st.metric("Total Registrasi Pasien", f"{total_pasien} Orang")
                with m_col2:
                    st.metric("Pemeriksaan Selesai (Clear)", f"{total_selesai} Kasus")
                with m_col3:
                    st.metric("Total Akun Staf Aktif", f"{total_user_sistem} Akun")
            
            with st.container(border=True):
                st.metric(
                    label="💰 Total Pendapatan Kotor Laboratorium (Real-time)", 
                    value=f"Rp {int(total_omset):,}".replace(",", ".")
                )
                st.caption("Seluruh perhitungan tarif diakumulasikan secara otomatis berdasarkan parameter pemeriksaan yang aktif di database.")
                
        except Exception as e:
            st.error(f"Gagal memuat ringkasan statistik database: {e}")

    # ============================================================
    # TAB 2: MANAJEMEN AKUN PENGGUNA (FIXED CRASH)
    # ============================================================
    with tab_user:
        st.markdown("### 👥 Kontrol Hak Akses Akun Pengguna")
        
        with st.container(border=True):
            st.markdown("#### ➕ Buat Kredensial Akun Baru")
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                new_username = st.text_input("Username Baru", placeholder="Ketik username...", key="new_username")
                new_password = st.text_input("Password", type="password", placeholder="Ketik password rahasia...", key="new_password")
            with col_u2:
                new_role = st.selectbox("Hak Akses (Role)", ["analis", "admin"], key="new_role")
            
            if st.button("💾 Simpan Akun Permanen", use_container_width=True):
                if not new_username or not new_password:
                    st.warning("⚠️ Username dan Password wajib diisi.")
                else:
                    try:
                        check_user = supabase.table("users").select("*").eq("username", new_username).execute()
                        if check_user.data:
                            st.error("❌ Username tersebut sudah terdaftar!")
                        else:
                            payload = {"username": new_username, "password": new_password, "role": new_role}
                            supabase.table("users").insert(payload).execute()
                            st.success(f"🎉 Akun {new_role} berhasil dibuat!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Koneksi database bermasalah: {e}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📋 Daftar Pengguna Sistem Saat Ini")
        
        try:
            users_resp = supabase.table("users").select("*").order("created_at", desc=True).execute()
            if users_resp.data:
                for idx, u in enumerate(users_resp.data):
                    with st.container(border=True):
                        col_show1, col_show2, col_show3 = st.columns([2, 2, 1])
                        with col_show1:
                            st.markdown(f"**Username:** `{u['username']}`")
                        with col_show2:
                            role_badge = "🛡️ Admin Utama" if u['role'] == "admin" else "🔬 Analis Laboratorium"
                            st.markdown(f"**Role:** {role_badge}")
                        with col_show3:
                            st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                            if st.button("🗑️ Hapus", key=f"del_user_{u['id']}_{idx}", use_container_width=True):
                                supabase.table("users").delete().eq("id", u['id']).execute()
                                st.success(f"Akun '{u['username']}' telah dihapus!")
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Belum ada akun pengguna yang terdaftar.")
        except Exception as e:
            st.error(f"Gagal mengambil daftar pengguna: {e}")

    # ============================================================
    # TAB 3: MANAJEMEN DATA DOKTER PENGIRIM (FIXED CRASH)
    # ============================================================
    with tab_dokter:
        st.markdown("### 🩻 Manajemen Master Data Dokter")
        
        with st.container(border=True):
            st.markdown("#### ➕ Daftarkan Dokter Pengirim Baru")
            col_d1, col_d2 = st.columns([3, 1])
            with col_d1:
                input_nama_dr = st.text_input("Nama Lengkap Dokter", placeholder="Contoh: dr. Anggraeni, Sp.PK", key="input_nama_dr")
            with col_d2:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                btn_simpan_dr = st.button("➕ Tambah Dokter", use_container_width=True)
                
            if btn_simpan_dr:
                if not input_nama_dr:
                    st.warning("⚠️ Masukkan nama dokter terlebih dahulu.")
                else:
                    try:
                        supabase.table("doctors").insert({"nama_dokter": input_nama_dr}).execute()
                        st.success(f"✅ Master data '{input_nama_dr}' berhasil ditambahkan!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menyimpan data dokter: {e}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📋 Database Relasi Dokter Aktif")
        
        try:
            doc_resp = supabase.table("doctors").select("*").order("nama_dokter", desc=False).execute()
            if doc_resp.data:
                for idx, doc in enumerate(doc_resp.data):
                    with st.container(border=True):
                        edit_mode_key = f"edit_mode_{doc['id']}"
                        if edit_mode_key not in st.session_state:
                            st.session_state[edit_mode_key] = False
                            
                        if not st.session_state[edit_mode_key]:
                            col_r1, col_r2, col_r3 = st.columns([3, 1, 1])
                            with col_r1:
                                st.markdown(f"🩺 **{doc['nama_dokter']}**")
                            with col_r2:
                                if st.button("📝 Ubah Nama", key=f"edit_btn_{doc['id']}_{idx}", use_container_width=True):
                                    st.session_state[edit_mode_key] = True
                                    st.rerun()
                            with col_r3:
                                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                                if st.button("🗑️ Hapus", key=f"del_doc_{doc['id']}_{idx}", use_container_width=True):
                                    supabase.table("doctors").delete().eq("id", doc['id']).execute()
                                    st.success(f"Data '{doc['nama_dokter']}' berhasil dihapus!")
                                    st.rerun()
                                st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            col_edit1, col_edit2, col_edit3 = st.columns([3, 1, 1])
                            with col_edit1:
                                txt_update_nama = st.text_input("Perbarui Nama Dokter", value=doc['nama_dokter'], key=f"txt_up_{doc['id']}")
                            with col_edit2:
                                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                                if st.button("✅ Oke", key=f"ok_up_{doc['id']}", use_container_width=True):
                                    if txt_update_nama:
                                        supabase.table("doctors").update({"nama_dokter": txt_update_nama}).eq("id", doc['id']).execute()
                                        st.session_state[edit_mode_key] = False
                                        st.rerun()
                            with col_edit3:
                                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                                if st.button("❌ Batal", key=f"cancel_up_{doc['id']}", use_container_width=True):
                                    st.session_state[edit_mode_key] = False
                                    st.rerun()
            else:
                st.info("Belum ada nama dokter pengirim yang terdata.")
        except Exception as e:
            st.error(f"Gagal mengambil list dokter dari database: {e}")