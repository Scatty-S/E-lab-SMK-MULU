import streamlit as st
from utils.db import supabase
from utils.pdf_engine import generate_kuitansi_pdf, generate_hasil_lab_pdf

# ============================================================
# CALLBACK SAKTI: Sinkronisasi Paket Centang dengan Cache Memory
# ============================================================
def toggle_all_paket(bidang, main, items, patient_id):
    all_key = f"all_{bidang}_{main}".replace(" ", "_")
    is_all_checked = st.session_state[all_key]
    for item in items:
        safe_key = f"{item['bidang']}_{item['main']}_{item['sub']}".replace(" ", "_").replace("/", "_").replace("-", "_")
        chk_key = f"chk_{safe_key}"
        # Set nilai langsung ke session state aktif & master cache
        st.session_state[chk_key] = is_all_checked
        st.session_state[f"lab_cache_{patient_id}"][chk_key] = is_all_checked

def render_proses_lab():
    if "selected_patient_id" not in st.session_state:
        st.warning("Silakan pilih pasien terlebih dahulu dari Dashboard.")
        if st.button("Kembali ke Dashboard"):
            st.session_state.current_page = "Dashboard Analis"
            st.rerun()
        return

    patient_id = st.session_state.selected_patient_id
    
    # Inisialisasi state pelacak dokumen agar aman saat halaman reload
    if f"saved_{patient_id}" not in st.session_state:
        st.session_state[f"saved_{patient_id}"] = False
    if f"pdf_kuitansi_{patient_id}" not in st.session_state:
        st.session_state[f"pdf_kuitansi_{patient_id}"] = None
    if f"pdf_hasil_{patient_id}" not in st.session_state:
        st.session_state[f"pdf_hasil_{patient_id}"] = None
    
    # 1. AMBIL DETAIL DATA PASIEN DARI DATABASE
    try:
        p_resp = supabase.table("patients").select("*").eq("id", patient_id).execute()
        if not p_resp.data:
            st.error("Data pasien tidak ditemukan.")
            return
        patient = p_resp.data[0]
    except Exception as e:
        st.error(f"Gagal mengambil data pasien: {e}")
        return
    
    # ============================================================
    # ANTI-RESET ENGINE: Load Cache Pengisian Pasien Jika Ada
    # ============================================================
    if f"lab_cache_{patient_id}" not in st.session_state:
        st.session_state[f"lab_cache_{patient_id}"] = {}
        # Tarik cadangan dari database jika data pengujian ternyata sudah pernah disimpan sebelumnya
        try:
            existing_lab = supabase.table("pemeriksaan_lab").select("*").eq("patient_id", patient_id).execute()
            if existing_lab.data:
                for row in existing_lab.data:
                    s_key = f"{row['bidang_periksa']}_{row['pemeriksaan']}_{row['sub_periksa']}".replace(" ", "_").replace("/", "_").replace("-", "_")
                    st.session_state[f"lab_cache_{patient_id}"][f"chk_{s_key}"] = True
                    st.session_state[f"lab_cache_{patient_id}"][f"hasil_in_{s_key}"] = row['hasil_pemeriksaan']
                    st.session_state[f"lab_cache_{patient_id}"][f"norm_in_{s_key}"] = row['nilai_normal']
                    st.session_state[f"lab_cache_{patient_id}"][f"sat_in_{s_key}"] = row['satuan']
                    st.session_state[f"lab_cache_{patient_id}"][f"trf_in_{s_key}"] = int(row['tarif'])
                    st.session_state[f"lab_cache_{patient_id}"][f"bdg_in_{s_key}"] = row['bidang_periksa']
                    st.session_state[f"lab_cache_{patient_id}"][f"main_in_{s_key}"] = row['pemeriksaan']
                    st.session_state[f"lab_cache_{patient_id}"][f"sub_in_{s_key}"] = row['sub_periksa']
        except Exception:
            pass

    # CRITICAL FIX: Suntikkan cache HANYA jika key belum ada di session state utama.
    # Ini mencegah data baru yang sedang diketik user ter-overwrite/terhapus secara tidak sengaja.
    for k, v in st.session_state[f"lab_cache_{patient_id}"].items():
        if k not in st.session_state:
            st.session_state[k] = v

    # ============================================================
    # SUNTIKAN CUSTOM CSS FIXED – PAKSA LIGHT THEME HIGH CONTRAST (SCOPED)
    # ============================================================
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=400;500;600;700;800&display=swap');
        
        /* 1. Paksa Background Utama Hanya pada Area Kerja Utama (Sidebar Tetap Normal) */
        [data-testid="stMainBlockContainer"] {
            background-color: #f8fafc !important;
        }
        
        /* Fix Top Header Streamlit biar gak belang */
        [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        
        /* 2. Paksa Semua Jenis Tulisan Konten Utama Menjadi Hitam Pekat Sleek */
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
        
        /* 4. Kotak Expander Pengujian Form */
        [data-testid="stMainBlockContainer"] div[data-testid="stExpander"] {
            background-color: #ffffff !important;
            border-radius: 12px !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
            margin-bottom: 12px !important;
        }
        
        /* 5. Desain Kolom Input Teks & Angka */
        [data-testid="stMainBlockContainer"] .stTextInput input, 
        [data-testid="stMainBlockContainer"] .stNumberInput input {
            color: #0f172a !important;
            font-weight: 600 !important;
            background-color: #f1f5f9 !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
        }
        
        /* Gaya Teks Placeholder */
        [data-testid="stMainBlockContainer"] .stTextInput input::placeholder {
            color: #94a3b8 !important;
        }

        /* 6. HOVER ENGINE BUTTON: Default Solid Hitam, Hover Putih Cerah */
        [data-testid="stMainBlockContainer"] .stButton > button {
            color: #ffffff !important;
            background-color: #0f172a !important;
            border: 2px solid #0f172a !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease-in-out !important;
        }

        [data-testid="stMainBlockContainer"] .stButton > button:hover {
            color: #0f172a !important;
            background-color: #ffffff !important;
            border: 2px solid #0f172a !important;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Bersihkan format tanggal registrasi (hilangkan huruf 'T' bawaan ISO)
    tgl_raw = patient.get('tgl_registrasi') or patient.get('tanggal_registrasi') or patient.get('created_at') or ""
    tgl_formatted = tgl_raw.replace("T", " ").split(".")[0] if "T" in tgl_raw else tgl_raw

    st.markdown(f"<h2>🧪 Input Hasil Lab & Cetak: {patient.get('nama_pasien', '')}</h2>", unsafe_allow_html=True)
    
    if st.button("⬅️ Kembali ke Dashboard Pasien"):
        st.session_state.current_page = "Dashboard Analis"
        st.rerun()
        
    # TAMPILAN INFORMASI PATIENT HEADER
    with st.container(border=True):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f"**Kode Registrasi:** `{patient.get('no_rm', '-')}`")
            st.markdown(f"**Nama Pasien:** {patient.get('nama_pasien', '-')}")
            st.markdown(f"**Kategori Pasien:** {patient.get('kategori_pasien', 'UMUM')}")
            st.markdown(f"**Jenis Kelamin:** {patient.get('jenis_kelamin', patient.get('gender', '-'))}")
        with col_p2:
            st.markdown(f"**Tanggal Registrasi:** {tgl_formatted}")
            st.markdown(f"**Dokter Pengirim:** {patient.get('dokter', patient.get('dokter_pengirim', '-'))}")
            st.markdown(f"**Alamat:** {patient.get('alamat', '-')}")
            st.markdown(f"**Golongan Darah:** {patient.get('gol_darah', patient.get('golongan_darah', '-'))}")

    st.markdown("---")

    # 2. MASTER DATA PARAMETER LAB LENGKAP
    master_parameters = [
        # --- HISTOPATOLOGI ---
        {"bidang": "HISTOPATOLOGI", "main": "Makroskopis", "sub": "Panjang", "normal": "--", "satuan": "", "tarif": 10000},
        {"bidang": "HISTOPATOLOGI", "main": "Makroskopis", "sub": "Lebar", "normal": "--", "satuan": "", "tarif": 10000},
        {"bidang": "HISTOPATOLOGI", "main": "Makroskopis", "sub": "Tinggi/Tebal", "normal": "--", "satuan": "", "tarif": 10000},
        {"bidang": "HISTOPATOLOGI", "main": "Makroskopis", "sub": "Bentuk", "normal": "--", "satuan": "", "tarif": 10000},
        {"bidang": "HISTOPATOLOGI", "main": "Makroskopis", "sub": "Warna", "normal": "--", "satuan": "", "tarif": 10000},
        {"bidang": "HISTOPATOLOGI", "main": "Makroskopis", "sub": "Konsistensi", "normal": "--", "satuan": "", "tarif": 10000},
        
        # --- KIMIA KLINIK ---
        {"bidang": "KIMIA KLINIK", "main": "Gula Darah", "sub": "Gula Darah Acak", "normal": "< 200 mg/dl", "satuan": "mg/dl", "tarif": 10000},
        
        # --- HEMATOLOGI (Darah Lengkap) ---
        {"bidang": "HEMATOLOGI", "main": "Darah Lengkap", "sub": "Hemoglobin", "normal": "13,8 - 17,2 g/dl", "satuan": "g/dl", "tarif": 10000},
        {"bidang": "HEMATOLOGI", "main": "Darah Lengkap", "sub": "LED (Laju Endap Darah)", "normal": "0-20 mm/jam", "satuan": "mm/jam", "tarif": 10000},
        {"bidang": "HEMATOLOGI", "main": "Darah Lengkap", "sub": "Jumlah Leukosit", "normal": "4.000-11.000 Sel / µl", "satuan": "Sel / µl", "tarif": 10000},
        {"bidang": "HEMATOLOGI", "main": "Darah Lengkap", "sub": "Hematokrit", "normal": "34-50%", "satuan": "%", "tarif": 10000},
        
        # --- HEMATOLOGI (Hitung Jenis Leukosit) ---
        {"bidang": "HEMATOLOGI", "main": "Hitung Jenis Leukosit", "sub": "Eosinofil", "normal": "1-4%", "satuan": "%", "tarif": 10000},
        {"bidang": "HEMATOLOGI", "main": "Hitung Jenis Leukosit", "sub": "Basofil", "normal": "0-5%", "satuan": "%", "tarif": 10000},
        {"bidang": "HEMATOLOGI", "main": "Hitung Jenis Leukosit", "sub": "Neutrofil Batang", "normal": "0-6%", "satuan": "%", "tarif": 10000},
        {"bidang": "HEMATOLOGI", "main": "Hitung Jenis Leukosit", "sub": "Neutrofil Segmen", "normal": "40-70%", "satuan": "%", "tarif": 10000},
        {"bidang": "HEMATOLOGI", "main": "Hitung Jenis Leukosit", "sub": "Limfosit", "normal": "20-40%", "satuan": "%", "tarif": 10000},
        {"bidang": "HEMATOLOGI", "main": "Hitung Jenis Leukosit", "sub": "Monosit", "normal": "2-8%", "satuan": "%", "tarif": 10000},
    ]

    st.subheader("📋 Pilih Komponen Pemeriksaan")
    st.caption("Centang parameter langsung pada kotak kelompok di bawah ini:")

    kelompok_pemeriksaan = {}
    for p in master_parameters:
        key = (p["bidang"], p["main"])
        if key not in kelompok_pemeriksaan:
            kelompok_pemeriksaan[key] = []
        kelompok_pemeriksaan[key].append(p)

    parameters_terpilih = []

    # Tampilan pilihan bergaya Box Kotak Kontainer
    for (bidang, main), items in kelompok_pemeriksaan.items():
        with st.container(border=True):
            col_header1, col_header2 = st.columns([2, 1])
            with col_header1:
                st.markdown(f"#### 📦 {bidang} — *{main}*")
            with col_header2:
                st.checkbox(
                    "Pilih Semua Paket", 
                    key=f"all_{bidang}_{main}".replace(" ", "_"),
                    on_change=toggle_all_paket,
                    args=(bidang, main, items, patient_id)
                )

            st.markdown("<div style='margin-top: -10px;'></div>", unsafe_allow_html=True)
            
            cols = st.columns(3)
            for idx, item in enumerate(items):
                col_target = cols[idx % 3]
                with col_target:
                    safe_key = f"{item['bidang']}_{item['main']}_{item['sub']}".replace(" ", "_").replace("/", "_").replace("-", "_")
                    chk_key = f"chk_{safe_key}"
                    
                    is_checked = st.checkbox(label=item["sub"], key=chk_key)
                    if is_checked:
                        parameters_terpilih.append(item)

    if not parameters_terpilih:
        st.info("ℹ️ Silakan centang salah satu parameter kotak di atas untuk memunculkan form input data.")
        return

    st.markdown("---")
    st.subheader("🔬 Form Input Pemeriksaan (Sesuai Layout Asli)")

    list_input_data = []
    total_biaya = 0.0

    # 3. RENDER FORM INPUT 2 KOLOM
    for item in parameters_terpilih:
        safe_key = f"{item['bidang']}_{item['main']}_{item['sub']}".replace(" ", "_").replace("/", "_").replace("-", "_")
        
        with st.expander(f"📝 Pengujian: {item['sub']} ({item['bidang']})", expanded=True):
            col_left, col_right = st.columns(2)
            
            with col_left:
                input_bidang = st.text_input("Bidang Periksa", value=item['bidang'], key=f"bdg_in_{safe_key}")
                input_pemeriksaan = st.text_input("Pemeriksaan", value=item['main'], key=f"main_in_{safe_key}")
                input_sub = st.text_input("Sub Periksa", value=item['sub'], key=f"sub_in_{safe_key}")
                hasil = st.text_input("Hasil Pemeriksaan", placeholder="Ketik hasil pemeriksaan...", key=f"hasil_in_{safe_key}")
                
            with col_right:
                normal = st.text_input("Nilai Normal", value=item['normal'], key=f"norm_in_{safe_key}")
                satuan = st.text_input("Satuan", value=item['satuan'], key=f"sat_in_{safe_key}")
                tarif_item = st.number_input("Tarif (Rp)", value=item['tarif'], step=1000, key=f"trf_in_{safe_key}")
                
            list_input_data.append({
                "patient_id": patient_id,
                "bidang_periksa": input_bidang,
                "pemeriksaan": input_pemeriksaan,
                "sub_periksa": input_sub,
                "hasil_pemeriksaan": hasil if hasil else "-",
                "nilai_normal": normal,
                "satuan": satuan,
                "tarif": tarif_item
            })
            total_biaya += tarif_item

    st.markdown("---")
    
    # INPUT DATA OTORISASI PETUGAS & PENANGGUNG JAWAB
    st.subheader("👤 Otorisasi Petugas Laboratorium")
    with st.container(border=True):
        col_auth1, col_auth2 = st.columns(2)
        with col_auth1:
            penanggung_jawab = st.text_input("Penanggung Jawab (PJ)", value="Astri Nur Aini, S.Tr.Kes", key=f"pj_{patient_id}")
        with col_auth2:
            # MEMANGGIL USERNAME LOGIN SECARA OTOMATIS
            username_aktif = st.session_state.get("username", "Analis")
            analis_pemeriksa = st.text_input("Analis Pemeriksa", value=username_aktif, key=f"analis_{patient_id}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.metric(label="Total Biaya Pemeriksaan Pasien", value=f"Rp {int(total_biaya):,}".replace(",", "."))
    
    # 4. PROSES SIMPAN KE DATABASE & CONVERT PDF
    if st.button("💾 Simpan Hasil Lab Ke Database", type="primary", use_container_width=True):
        try:
            supabase.table("pemeriksaan_lab").delete().eq("patient_id", patient_id).execute()
            supabase.table("pemeriksaan_lab").insert(list_input_data).execute()
            supabase.table("patients").update({"status": "Selesai"}).eq("id", patient_id).execute()
            
            patient_pdf = patient.copy()
            patient_pdf["penanggung_jawab"] = penanggung_jawab
            patient_pdf["analis_pemeriksa"] = analis_pemeriksa
            patient_pdf["tanggal_registrasi_clean"] = tgl_formatted
            
            st.session_state[f"pdf_kuitansi_{patient_id}"] = bytes(generate_kuitansi_pdf(patient_pdf, list_input_data, total_biaya))
            st.session_state[f"pdf_hasil_{patient_id}"] = bytes(generate_hasil_lab_pdf(patient_pdf, list_input_data))
            st.session_state[f"saved_{patient_id}"] = True
            
            st.success("✅ Seluruh data parameter pemeriksaan laboratorium berhasil direkam ke database!")
            st.rerun()
        except Exception as e:
            st.error(f"Gagal menyimpan data ke database: {e}")
            
    # 5. INTEGRASI TOMBOL CETAK DOWNLOAD DOKUMEN PDF
    if st.session_state[f"saved_{patient_id}"]:
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🖨️ Cetak Dokumen Resmi (Format A4)")
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            if st.session_state[f"pdf_kuitansi_{patient_id}"]:
                st.download_button(
                    label="📄 Download Kuitansi Pembayaran (PDF)",
                    data=st.session_state[f"pdf_kuitansi_{patient_id}"],
                    file_name=f"Kuitansi_{patient['no_rm']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        with col_dl2:
            if st.session_state[f"pdf_hasil_{patient_id}"]:
                st.download_button(
                    label="🧬 Download Hasil Pemeriksaan Lab (PDF)",
                    data=st.session_state[f"pdf_hasil_{patient_id}"],
                    file_name=f"Hasil_Lab_{patient['no_rm']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    else:
        st.caption("💡 *Tombol cetak dokumen PDF akan aktif di sini secara otomatis setelah kamu menekan tombol simpan di atas.*")

    # ============================================================
    # REAL-TIME LOCK ENGINE: Amankan Ketikan Analis di Setiap Rerun
    # ============================================================
    for k in list(st.session_state.keys()):
        if any(k.startswith(prefix) for prefix in ["chk_", "hasil_in_", "norm_in_", "sat_in_", "trf_in_", "all_", "bdg_in_", "main_in_", "sub_in_", "pj_", "analis_"]):
            st.session_state[f"lab_cache_{patient_id}"][k] = st.session_state[k]
