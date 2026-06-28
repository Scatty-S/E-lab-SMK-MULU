import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def draw_header_dan_kop(pdf, patient):
    """Fungsi pembantu untuk menggambar KOP Surat resmi SMK Muhammadiyah Lumajang"""
    # 1. CETAK LOGO DI SEBELAH KIRI KOP
    logo_path = "assets/logo_smk.png"
    if os.path.exists(logo_path):
        try:
            pdf.drawImage(logo_path, 40, 745, width=65, height=65, mask='auto')
        except Exception:
            pdf.rect(40, 745, 65, 65, stroke=1, fill=0)
            pdf.setFont("Helvetica", 8)
            pdf.drawCentredString(72.5, 775, "[ LOGO ]")
    else:
        pdf.rect(40, 745, 65, 65, stroke=1, fill=0)
        pdf.setFont("Helvetica", 8)
        pdf.drawCentredString(72.5, 775, "[ LOGO ]")

    # 2. TEKS IDENTITAS KOP SURAT
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(120, 795, "SMK MUHAMMADIYAH LUMAJANG")
    
    pdf.setFont("Helvetica", 9)
    pdf.drawString(120, 780, "Jl. Letkol Slamet Wardoyo No. 103 Labruk Lor, Lumajang, Jawa Timur")
    pdf.drawString(120, 765, "Telepon: 082288212014 | Email: smkm.lmj@gmail.com | Website: smkmulu.sch.id")
    
    # Garis pembatas ganda KOP
    pdf.setLineWidth(1.5)
    pdf.line(40, 735, 555, 735)
    pdf.setLineWidth(0.5)
    pdf.line(40, 732, 555, 732)


def draw_patient_info_grid(pdf, patient):
    """Fungsi pembantu untuk mencetak grid data identitas pasien secara simetris"""
    # 🔍 MULTI-KEY BACKUP TRACKER: Deteksi otomatis key apapun yang dikirim dari backend/DB
    tgl_reg = (
        patient.get("tanggal_registrasi_clean") or 
        patient.get("tanggal_registrasi") or 
        patient.get("tanggal") or 
        patient.get("tgl_registrasi") or 
        "-"
    )
    
    # Keamanan ekstra: Jika tipenya string, potong spasi dan bersihkan huruf 'T' (Format ISO)
    if isinstance(tgl_reg, str):
        tgl_reg = tgl_reg.replace("T", " ").strip()
        if not tgl_reg: # Jika ternyata string kosong ""
            tgl_reg = "-"

    pdf.setFont("Helvetica", 9)
    # GRID KIRI
    pdf.drawString(40, 690, "NO RM")
    pdf.drawString(110, 690, f": {patient.get('no_rm', '-')}")
    
    pdf.drawString(40, 675, "Nama Pasien")
    pdf.drawString(110, 675, f": {patient.get('nama_pasien', '-')}")
    
    pdf.drawString(40, 660, "Gender")
    pdf.drawString(110, 660, f": {patient.get('jenis_kelamin', patient.get('gender', '-'))}")
    
    pdf.drawString(40, 645, "Alamat")
    pdf.drawString(110, 645, f": {patient.get('alamat', '-')}")

    # GRID KANAN
    pdf.drawString(320, 690, "Tgl. Registrasi")
    pdf.drawString(395, 690, f": {tgl_reg}")
    
    pdf.drawString(320, 675, "Pengirim")
    pdf.drawString(395, 675, f": {patient.get('dokter', '-')}")
    
    pdf.drawString(320, 660, "Kategori Pasien")
    pdf.drawString(395, 660, f": {patient.get('kategori_pasien', 'UMUM')}")
    
    pdf.drawString(320, 645, "Gol. Darah")
    pdf.drawString(395, 645, f": {patient.get('gol_darah', '-')}")


def generate_hasil_lab_pdf(patient, list_input_data):
    """Fungsi Utama Lembar Hasil Pemeriksaan Laboratorium"""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    
    draw_header_dan_kop(pdf, patient)
    
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawCentredString(297, 712, "HASIL PEMERIKSAAN LABORATORIUM")
    
    draw_patient_info_grid(pdf, patient)
    
    # Header Tabel Utama
    y = 610
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(40, y, "Pemeriksaan / Parameter")
    pdf.drawString(260, y, "Hasil")
    pdf.drawString(380, y, "Nilai Normal")
    pdf.drawString(480, y, "Satuan")
    
    pdf.line(40, y-5, 555, y-5)
    y -= 20
    
    current_bidang = ""
    
    for item in list_input_data:
        # Validasi batas bawah halaman sebelum menulis baris baru
        if y < 120:
            pdf.showPage()
            draw_header_dan_kop(pdf, patient)
            y = 610
            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawString(40, y, "Pemeriksaan / Parameter")
            pdf.drawString(260, y, "Hasil")
            pdf.drawString(380, y, "Nilai Normal")
            pdf.drawString(480, y, "Satuan")
            pdf.line(40, y-5, 555, y-5)
            y -= 20

        # Jika masuk ke Kelompok/Bidang baru
        if item['bidang_periksa'] != current_bidang:
            current_bidang = item['bidang_periksa']
            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawString(40, y, current_bidang.upper())
            y -= 15
            
        pdf.setFont("Helvetica", 9)
        pdf.drawString(50, y, f"- {item['sub_periksa']}")
        pdf.drawString(260, y, str(item['hasil_pemeriksaan']))
        pdf.drawString(380, y, str(item['nilai_normal']))
        pdf.drawString(480, y, str(item['satuan'] if item['satuan'] else "-"))
        y -= 15
            
    pdf.line(40, y+5, 555, y+5)
    
    # Jarak aman penulisan tanda tangan bawah
    y -= 20
    if y < 140:
        pdf.showPage()
        draw_header_dan_kop(pdf, patient)
        y = 650
        
    tgl_cetak = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(40, y, f"Tanggal Cetak: {tgl_cetak}")
    
    y -= 20
    pdf.setFont("Helvetica", 9)
    pdf.drawString(40, y, "Analis Pemeriksa,")
    pdf.drawString(380, y, "Penanggung Jawab,")
    
    y -= 55  
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(40, y, str(patient.get('analis_pemeriksa', 'Ahmad Dani')))
    pdf.drawString(380, y, str(patient.get('penanggung_jawab', 'Astri Nur Aini, S.Tr.Kes')))
    
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def generate_kuitansi_pdf(patient, list_input_data, total_biaya):
    """Fungsi Utama Lembar Nota / Kuitansi Pembayaran"""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    
    draw_header_dan_kop(pdf, patient)
    
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawCentredString(297, 712, "KUITANSI PEMBAYARAN LABORATORIUM")
    
    draw_patient_info_grid(pdf, patient)
    
    # Header Tabel Rincian Biaya
    y = 610
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(40, y, "Item Pemeriksaan")
    pdf.drawString(450, y, "Tarif Harga")
    
    pdf.line(40, y-5, 555, y-5)
    y -= 20
    
    for item in list_input_data:
        if y < 120:
            pdf.showPage()
            draw_header_dan_kop(pdf, patient)
            y = 610
            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawString(40, y, "Item Pemeriksaan")
            pdf.drawString(450, y, "Tarif Harga")
            pdf.line(40, y-5, 555, y-5)
            y -= 20

        pdf.setFont("Helvetica", 9)
        pdf.drawString(40, y, f"Pemeriksaan {item['pemeriksaan']} ({item['sub_periksa']})")
        pdf.drawString(450, y, f"Rp {int(item['tarif']):,}".replace(",", "."))
        y -= 15
        
    pdf.line(40, y+5, 555, y+5)
    y -= 20
    
    # Total Biaya
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(320, y, "TOTAL PEMBAYARAN :")
    pdf.drawString(450, y, f"Rp {int(total_biaya):,}".replace(",", "."))
    
    y -= 30
    if y < 140:
        pdf.showPage()
        draw_header_dan_kop(pdf, patient)
        y = 650

    pdf.setFont("Helvetica", 9)
    pdf.drawString(380, y, "Petugas Kasir Lab,")
    
    y -= 55  
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(380, y, str(patient.get('analis_pemeriksa', 'Ahmad Dani')))
    
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()