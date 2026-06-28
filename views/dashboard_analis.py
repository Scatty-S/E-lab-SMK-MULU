import streamlit as st
import pandas as pd
from utils.db import supabase

def render_dashboard_analis():
    # Ambil username dari session state yang sedang login saat ini
    current_user = st.session_state.get('username', 'Analis')

    # ============================================================
    # 1. SUNTIKAN CUSTOM CSS – ANTI-THETA OVERRIDE FORCED BLACK
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
        
        /* Mengubah Container Border Menjadi Kartu Putih Elegan (SaaS Style) */
        div[data-testid="stContainer"] {
            background: #ffffff !important;
            border-radius: 16px !important;
            padding: 1.5rem !important;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.04), 0 8px 10px -6px rgba(15, 23, 42, 0.04) !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
        }

        /* Modifikasi Tampilan Nilai Ringkasan (Metrics) */
        div[data-testid="stMetricValue"] {
            font-size: 28px !important;
            font-weight: 800 !important;
            color: #000000 !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 11px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.7px !important;
            color: #000000 !important;
            opacity: 0.6;
            font-weight: 700 !important;
        }
        
        /* Teks di dalam Dropdown & Input Field Search */
        .stTextInput input {
            color: #000000 !important;
            border-radius: 10px !important;
            background-color: #f8fafc !important;
            font-weight: 600 !important;
        }

        /* FIX WORKAROUND UNTUK UTAMA TOMBOL */
        div.stButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }
        /* Tombol Utama / Primary */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%) !important;
            color: #ffffff !important;
            border: none !important;
        }
        /* Tombol Biasa / Secondary (Ubah & Hapus) */
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

        /* Paksa seluruh teks paragraf, heading, dan label di area utama agar menjadi hitam */
        [data-testid="stMainBlockContainer"] p,
        [data-testid="stMainBlockContainer"] h1,
        [data-testid="stMainBlockContainer"] h2,
        [data-testid="stMainBlockContainer"] h3,
        [data-testid="stMainBlockContainer"] h4,
        [data-testid="stMainBlockContainer"] label {
            color: #000000 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. HEADER UTAMA ---
    st.markdown(f'<p class="main-title">📊 Analis Workspace ({current_user})</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Sistem Pemrosesan Hasil Laboratorium & Manajemen Antrean Pasien Terintegrasi</p>', unsafe_allow_html=True)

    # --- 3. AMBIL DATA PASIEN (DI-FILTER BERDASARKAN USER LOGIN) ---
    try:
        # CRITICAL FIX: Menambahkan .eq("created_by", current_user) agar data terisolasi per akun
        response = supabase.table("patients")\
            .select("*")\
            .eq("created_by", current_user)\
            .order("tgl_registrasi", desc=True)\
            .execute()
        raw_data = response.data
    except Exception as e:
        st.error(f"❌ Gagal memuat data database: {e}")
        return

    if not raw_data:
        st.info(f"💡 Belum ada data pasien aktif untuk akun '{current_user}'. Silakan masuk ke menu 'Registrasi Pasien Baru'.")
        return

    df = pd.DataFrame(raw_data)
    
    # --- 4. RINGKASAN METRICS (Otomatis terhitung hanya untuk pasien milik akun ini) ---
    total_pasien = len(df)
    kategori_counts = df['kategori_pasien'].value_counts() if 'kategori_pasien' in df.columns else {}
    bpjs_count = kategori_counts.get('BPJS', 0) if isinstance(kategori_counts, pd.Series) else 0
    umum_count = kategori_counts.get('Umum', 0) if isinstance(kategori_counts, pd.Series) else 0

    with st.container():
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric(label="Total Antrean Anda", value=f"{total_pasien} Pasien")
        with col_m2:
            st.metric(label="Pasien BPJS Anda", value=f"{bpjs_count} Orang")
        with col_m3:
            st.metric(label="Pasien Umum Anda", value=f"{umum_count} Orang")

    st.markdown("###") # Spacer Space

    # --- 5. INPUT PENCARIAN & DAFTAR ANTREAN UTAMA ---
    st.markdown("<h4>📋 Antrean Pasien Kelolaan Anda</h4>", unsafe_allow_html=True)
    search_query = st.text_input("", placeholder="🔍 Cari nama pasien atau nomor RM kelolaan Anda...", label_visibility="collapsed")
    
    if search_query:
        df_filtered = df[df['nama_pasien'].str.contains(search_query, case=False, na=False) | 
                         df['no_rm'].str.contains(search_query, case=False, na=False)]
    else:
        df_filtered = df.copy()

    st.markdown("---")

    if df_filtered.empty:
        st.warning("⚠️ Data pasien tidak ditemukan berdasarkan kata kunci tersebut.")
    else:
        for idx, row in df_filtered.iterrows():
            with st.container():
                col_kiri_aksi, col_kanan_info = st.columns([1.8, 4])
                
                # ----------------- PANEL SEBELAH KIRI (AKSI DI ANTREAN) -----------------
                with col_kiri_aksi:
                    st.markdown("<p style='margin-bottom:4px; font-weight:bold; color:#4f46e5; font-size:12px;'>AKSI ANALIS</p>", unsafe_allow_html=True)
                    
                    # Tombol PROSES LAB
                    if st.button("👁️ Proses Lab", key=f"action_proses_{row['id']}", type="primary", use_container_width=True):
                        st.session_state.selected_patient_id = row['id']
                        st.session_state.current_page = "Proses Lab"
                        st.toast(f"Membuka lembar kerja laboratorium untuk {row['nama_pasien']}...")
                        st.rerun()
                    
                    col_sub1, col_sub2 = st.columns(2)
                    with col_sub1:
                        if st.button("📝 Ubah", key=f"action_edit_{row['id']}", use_container_width=True):
                            st.session_state.selected_patient_id = row['id']
                            st.session_state.current_page = "Ubah Pasien"
                            st.rerun()
                    with col_sub2:
                        if st.button("🗑️ Hapus", key=f"action_delete_{row['id']}", use_container_width=True):
                            try:
                                p_id = row['id']
                                
                                # Simpan riwayat hapus secara aman
                                try:
                                    log_data = {
                                        "patient_id": p_id,
                                        "no_rm": row["no_rm"],
                                        "nama_pasien": row["nama_pasien"],
                                        "dihapus_oleh": current_user
                                    }
                                    supabase.table("riwayat_hapus").insert(log_data).execute()
                                except Exception:
                                    pass
                                
                                # HARD DELETE BERANTAI
                                supabase.table("pemeriksaan_lab").delete().eq("patient_id", p_id).execute()
                                supabase.table("patients").delete().eq("id", p_id).execute()
                                
                                st.toast(f"✅ Data {row['nama_pasien']} berhasil dibersihkan total!", icon="🗑️")
                                st.rerun()
                            except Exception as delete_error:
                                st.error(f"❌ Gagal memproses penghapusan: {delete_error}")

                # ----------------- PANEL SEBELAH KANAN (INFO DETAIL PASIEN) -----------------
                with col_kanan_info:
                    st.markdown(f"""
                        <h3 style='color: #000000 !important; margin-top: 0px; margin-bottom: 15px; font-family: sans-serif; font-weight: 700;'>
                            {row['nama_pasien']} 
                            <span style='font-size: 14px; color: #64748b !important; font-weight: normal;'>({row['no_rm']})</span>
                        </h3>
                    """, unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown(f"""
                            <p style='color: #000000 !important; margin: 0px; font-size: 14px;'>
                                <b style='color: #000000 !important;'>Kategori:</b> 
                                <span style='background-color: #1e1b4b; color: #ffffff !important; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 700;'>{str(row['kategori_pasien']).upper()}</span>
                            </p>
                            <p style='color: #000000 !important; margin-top: 8px; margin-bottom: 0px; font-size: 14px;'>
                                <b style='color: #000000 !important;'>Gender:</b> {row.get('jenis_kelamin', row.get('gender', '-'))}
                            </p>
                        """, unsafe_allow_html=True)
                    with c2:
                        db_status = row.get('status', 'Mengantri')
                        if db_status in ["Selesai", "Lunas", "Sudah Lunas"]:
                            status_badge = "<span style='color: #16a34a !important; font-weight: 700;'>🟢 Sudah Lunas</span>"
                        else:
                            status_badge = "<span style='color: #dc2626 !important; font-weight: 700;'>🔴 Belum Lunas</span>"

                        st.markdown(f"""
                            <p style='color: #000000 !important; margin: 0px; font-size: 14px;'>
                                <b style='color: #000000 !important;'>Gol. Darah:</b> <span style='background-color: #f1f5f9; color: #000000 !important; padding: 1px 5px; border-radius: 4px; font-weight: bold;'>{row.get('gol_darah', '-')}</span>
                            </p>
                            <p style='color: #000000 !important; margin-top: 8px; margin-bottom: 0px; font-size: 14px;'>
                                <b style='color: #000000 !important;'>Status:</b> {status_badge}
                            </p>
                        """, unsafe_allow_html=True)
                    with c3:
                        tgl_raw = row.get('tgl_registrasi', row.get('tanggal_registrasi', '-'))
                        tgl_bersih = str(tgl_raw).replace("T", " ")[:19] if tgl_raw else "-"
                        
                        st.markdown(f"""
                            <p style='color: #000000 !important; margin: 0px; font-size: 14px; line-height: 1.4;'>
                                <b style='color: #000000 !important;'>Tgl. Reg:</b><br>
                                <code style='background-color: #f1f5f9; color: #0f172a !important; padding: 2px 4px; border-radius: 4px; font-size: 12px; font-weight: 600;'>{tgl_bersih}</code>
                            </p>
                        """, unsafe_allow_html=True)
                        
            st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)