import streamlit as st
from utils.db import supabase

def render_ubah_pasien():
    # ============================================================
    # 1. SUNTIKAN CUSTOM CSS – SAMA DENGAN THEME DASHBOARD ANALIS
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
        div[data-testid="stContainer"] {
            background: #ffffff !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.04), 0 8px 10px -6px rgba(15, 23, 42, 0.04) !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
        }

        /* Teks di dalam Input Field, Dropdown, & Textarea */
        .stTextInput input, .stSelectbox div, .stTextArea textarea {
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

        /* FIX WORKAROUND UNTUK UTAMA TOMBOL */
        div.stButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            height: 46px !important;
            transition: all 0.2s ease !important;
        }
        /* Tombol Utama / Primary (Simpan) */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%) !important;
            color: #ffffff !important;
            border: none !important;
        }
        /* Tombol Biasa / Secondary (Batal) */
        div.stButton > button[kind="secondary"] {
            background-color: #f1f5f9 !important;
            color: #000000 !important;
            border: 1px solid #cbd5e1 !important;
        }
        
        /* Paksa teks tombol primary agar tetap putih */
        div.stButton > button[kind="primary"] p,
        div.stButton > button[kind="primary"] span {
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
    st.markdown('<p class="main-title">✏️ Modifikasi Data Pasien</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Perbarui data profil rekam medis pasien secara valid langsung ke dalam core database</p>', unsafe_allow_html=True)

    # --- 3. AMBIL ID PASIEN DARI SESSION STATE ---
    patient_id = st.session_state.get('selected_patient_id', None)
    
    if not patient_id:
        st.warning("⚠️ Tidak ada data pasien yang dipilih untuk diubah. Silakan kembali ke Dashboard.")
        if st.button("⬅️ Kembali ke Dashboard Analis", type="secondary"):
            st.session_state.current_page = "Dashboard Analis"
            st.rerun()
        return

    # --- 4. TARIK DATA LAMA DARI SUPABASE ---
    try:
        response = supabase.table("patients").select("*").eq("id", patient_id).execute()
        if not response.data:
            st.error("❌ Data pasien tidak ditemukan di dalam database atau sudah terhapus.")
            if st.button("⬅️ Kembali ke Dashboard", type="secondary"):
                st.session_state.current_page = "Dashboard Analis"
                st.rerun()
            return
        
        patient_data = response.data[0]
    except Exception as e:
        st.error(f"❌ Gagal mengambil data pasien dari database: {e}")
        return

    # --- 5. PANEL FORM DATA (BUNGKUS DENGAN CONTAINER AGAR KELUAR CARD PUTIH) ---
    with st.container():
        st.markdown("### 📋 Formulir Perubahan")
        
        col_kiri, col_kanan = st.columns(2)
        
        with col_kiri:
            # No RM sengaja didisable (read-only) karena idealnya No RM bersifat permanen & tidak diubah
            no_rm = st.text_input("Nomor Rekam Medis (RM):", value=patient_data.get('no_rm', ''), disabled=True)
            
            nama_pasien = st.text_input("Nama Lengkap Pasien:", value=patient_data.get('nama_pasien', ''))
            
            # Deteksi Kategori Lama untuk Default Index Dropdown
            kat_opsi = ["Umum", "BPJS"]
            kat_awal = str(patient_data.get('kategori_pasien', 'Umum')).capitalize()
            idx_kat = kat_opsi.index(kat_awal) if kat_awal in kat_opsi else 0
            kategori_pasien = st.selectbox("Kategori Pasien:", options=kat_opsi, index=idx_kat)

        with col_kanan:
            # Deteksi Gender Lama
            jk_opsi = ["Laki-laki", "Perempuan"]
            jk_awal = str(patient_data.get('jenis_kelamin', patient_data.get('gender', 'Laki-laki'))).strip()
            idx_jk = 1 if jk_awal.lower() in ["perempuan", "p"] else 0
            jenis_kelamin = st.selectbox("Jenis Kelamin Pasien:", options=jk_opsi, index=idx_jk)
            
            # Deteksi Golongan Darah Lama
            gol_opsi = ["-", "A", "B", "AB", "O"]
            gol_awal = str(patient_data.get('gol_darah', '-')).upper().strip()
            idx_gol = gol_opsi.index(gol_awal) if gol_awal in gol_opsi else 0
            gol_darah = st.selectbox("Golongan Darah:", options=gol_opsi, index=idx_gol)
            
            # Deteksi Status Lama
            status_opsi = ["Mengantri", "Selesai", "Belum Lunas", "Sudah Lunas"]
            status_awal = patient_data.get('status', 'Mengantri')
            idx_status = status_opsi.index(status_awal) if status_awal in status_opsi else 0
            status_pasien = st.selectbox("Status Tagihan/Antrean:", options=status_opsi, index=idx_status)

        # Input Alamat (Baris Penuh)
        alamat = st.text_area("Alamat Tempat Tinggal:", value=patient_data.get('alamat', ''))
        
        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
        
        # --- 6. TOMBOL AKSI BAWAH FORM ---
        col_btn_batal, col_btn_simpan = st.columns(2)
        
        with col_btn_batal:
            if st.button("❌ Batal & Kembali", type="secondary", use_container_width=True):
                # Bersihkan session ID pasien & balik ke dashboard utama
                st.session_state.selected_patient_id = None
                st.session_state.current_page = "Dashboard Analis"
                st.rerun()
                
        with col_btn_simpan:
            if st.button("💾 Simpan Perubahan", type="primary", use_container_width=True):
                if not nama_pasien.strip():
                    st.warning("⚠️ Kolom Nama Pasien tidak boleh dibiarkan kosong!")
                    return
                
                # Bungkus data yang akan diupdate ke tabel Supabase
                payload_update = {
                    "nama_pasien": nama_pasien,
                    "kategori_pasien": kategori_pasien,
                    "gol_darah": gol_darah,
                    "status": status_pasien,
                    "alamat": alamat
                }
                
                # Amankan nama kolom gender berdasarkan skema database kamu
                if 'jenis_kelamin' in patient_data:
                    payload_update["jenis_kelamin"] = jenis_kelamin
                if 'gender' in patient_data:
                    payload_update["gender"] = jenis_kelamin

                try:
                    # Jalankan eksekusi Update query ke tabel patients
                    supabase.table("patients").update(payload_update).eq("id", patient_id).execute()
                    
                    st.toast(f"🎉 Sukses! Data profil {nama_pasien} berhasil diperbarui.", icon="✅")
                    
                    # Reset session halaman dan balik ke list antrean utama
                    st.session_state.selected_patient_id = None
                    st.session_state.current_page = "Dashboard Analis"
                    st.rerun()
                except Exception as error_update:
                    st.error(f"❌ Gagal menyimpan pembaruan data ke database: {error_update}")