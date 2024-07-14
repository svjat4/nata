from flask_login import current_user, login_required

from website.utils.filters import day_and_date
from website.utils.func import pdf_only
from ... import db
from ...models.user import Biodata, BookedRoom, Room, Tool, User
from flask import Blueprint, jsonify, render_template, redirect, url_for, request, flash
from pathlib import Path
from ... import db, app
from os import path
import json
from flask import Flask, render_template, request, send_file
import pdfkit
from io import BytesIO
import os
import time

wadek = Blueprint('wadek', __name__)

upload_images = path.join(Path(__file__).parents[2], "static", app.config['UPLOAD_FOLDER'])
upload_folder = path.join(Path(__file__).parents[2], app.config['UPLOAD_FOLDER'])

@wadek.route('/dashboard/data', methods=['GET', 'POST'])
def dashboard():
    booked = BookedRoom.query.filter_by(isUsed="Yes").all()
    return render_template('wadek_2/beranda.html', booked=booked, current_user=current_user)

################################################ USER ################################################

@wadek.route('/surat/disposisi', methods=['GET', 'POST'])
def disposisi():
    return render_template('wadek_2/disposisi.html', current_user=current_user)

path_to_wkhtmltopdf = 'C:\\wkhtmltopdf\\bin\\wkhtmltopdf.exe' 
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

def generate_pdf(form_data):
    rendered = render_template('wadek_2/pdf.html', data=form_data)

    options={
        "enable-local-file-access": "",
        "--header-font-size": "6",
        "--header-font-name": "Times New Roman",
    }

    pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)
    buffer = BytesIO()
    buffer.write(pdf)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='disposisi.pdf', mimetype='application/pdf')

@wadek.route('/add_disposisi', methods=['POST'])
def add_disposisi():
    if request.method == 'POST':
        if 'cetak' in request.form:
            return generate_pdf(request.form)
        
        # nomor_disposisi = request.form['nomor_disposisi']
        # from_disposisi = request.form['from_disposisi']
        # nomor_surat = request.form['nomor_surat']
        # tanggal_surat = datetime.strptime(request.form['tanggal_surat'], '%Y-%m-%d') if request.form['tanggal_surat'] else None
        # perihal = request.form['perihal']
        # lampiran = True if request.form.get('lampiran') == 'Ada' else False
        # tanggal_diterima = datetime.strptime(request.form['tanggal_diterima'], '%Y-%m-%d') if request.form['tanggal_diterima'] else None
        # penerima = request.form['penerima']
        # sifat = request.form.get('sifat')
        # klasifikasi = request.form.get('klasifikasi')

        # ditunjukkan_wadek1 = True if request.form.get('ditunjukkan_wadek1') == 'true' else False
        # ditunjukkan_wadek2 = True if request.form.get('ditunjukkan_wadek2') == 'true' else False

        # ditembuskan_ka_spm = True if request.form.get('ditembuskan_ka_spm') == 'true' else False
        # ditembuskan_ka_prodi_si = True if request.form.get('ditembuskan_ka_prodi_si') == 'true' else False
        # ditembuskan_ka_prodi_ti = True if request.form.get('ditembuskan_ka_prodi_ti') == 'true' else False
        # ditembuskan_ka_informatika = True if request.form.get('ditembuskan_ka_informatika') == 'true' else False
        # ditembuskan_ka_gkm = True if request.form.get('ditembuskan_ka_gkm') == 'true' else False
        # ditembuskan_kabag_ak = True if request.form.get('ditembuskan_kabag_ak') == 'true' else False
        # ditembuskan_kabag_uk = True if request.form.get('ditembuskan_kabag_uk') == 'true' else False
        # ditembuskan_ka_lab = True if request.form.get('ditembuskan_ka_lab') == 'true' else False

        # disposisi_ditindaklanjuti = True if request.form.get('disposisi_ditindaklanjuti') == 'true' else False
        # disposisi_siap_sambutan = True if request.form.get('disposisi_siap_sambutan') == 'true' else False
        # disposisi_siap_menghadiri = True if request.form.get('disposisi_siap_menghadiri') == 'true' else False
        # disposisi_koordinasikan = True if request.form.get('disposisi_koordinasikan') == 'true' else False
        # disposisi_wakili_dekan = True if request.form.get('disposisi_wakili_dekan') == 'true' else False
        # disposisi_review_feasibility = True if request.form.get('disposisi_review_feasibility') == 'true' else False
        # disposisi_pertimbangkan = True if request.form.get('disposisi_pertimbangkan') == 'true' else False
        # disposisi_fasilitasi = True if request.form.get('disposisi_fasilitasi') == 'true' else False
        # disposisi_arsipkan = True if request.form.get('disposisi_arsipkan') == 'true' else False

        # catatan = request.form['catatan']
        # tanggal_ttd = datetime.strptime(request.form['tanggal_ttd'], '%Y-%m-%d') if request.form['tanggal_ttd'] else None
        # # nama_ttd = request.form['nama_ttd']

        # disposisi = Disposisi(
        #     nomor_disposisi=nomor_disposisi,
        #     from_disposisi=from_disposisi,
        #     nomor_surat=nomor_surat,
        #     tanggal_surat=tanggal_surat,
        #     perihal=perihal,
        #     lampiran=lampiran,
        #     tanggal_diterima=tanggal_diterima,
        #     penerima=penerima,
        #     sifat=sifat,
        #     klasifikasi=klasifikasi,
        #     ditunjukkan_wadek1=ditunjukkan_wadek1,
        #     ditunjukkan_wadek2=ditunjukkan_wadek2,
        #     ditembuskan_ka_spm=ditembuskan_ka_spm,
        #     ditembuskan_ka_prodi_si=ditembuskan_ka_prodi_si,
        #     ditembuskan_ka_prodi_ti=ditembuskan_ka_prodi_ti,
        #     ditembuskan_ka_informatika=ditembuskan_ka_informatika,
        #     ditembuskan_ka_gkm=ditembuskan_ka_gkm,
        #     ditembuskan_kabag_ak=ditembuskan_kabag_ak,
        #     ditembuskan_kabag_uk=ditembuskan_kabag_uk,
        #     ditembuskan_ka_lab=ditembuskan_ka_lab,
        #     disposisi_ditindaklanjuti=disposisi_ditindaklanjuti,
        #     disposisi_siap_sambutan=disposisi_siap_sambutan,
        #     disposisi_siap_menghadiri=disposisi_siap_menghadiri,
        #     disposisi_koordinasikan=disposisi_koordinasikan,
        #     disposisi_wakili_dekan=disposisi_wakili_dekan,
        #     disposisi_review_feasibility=disposisi_review_feasibility,
        #     disposisi_pertimbangkan=disposisi_pertimbangkan,
        #     disposisi_fasilitasi=disposisi_fasilitasi,
        #     disposisi_arsipkan=disposisi_arsipkan,
        #     catatan=catatan,
        #     tanggal_ttd=tanggal_ttd,
        #     nama_ttd="Aris Wahyu Murdiyanto, S.Kom., M.Cs."
        # )

        # try:
        #     db.session.add(disposisi)
        #     db.session.commit()
        #     return redirect(url_for('wadek.disposisi'))
        # except Exception as e:
        #     print(e)
        #     return redirect(url_for('wadek.disposisi'))

@wadek.route('/peminjaman-data', methods=['GET', 'POST'])
def data_peminjaman():
    booked = BookedRoom.query.all()
    results = []
    for data in booked:
        user = data.user_relationship
        biodata = user.profile_relationship
        room = data.room_relationship
        tools = [
            {
                'name': booked_tool.tool_relationship.name,
                'capacity': booked_tool.tool_relationship.capacity
            }
            for booked_tool in data.bookedtool_relationship
        ]
        results.append({
            'id': data.id,
            'timestamp': day_and_date(data.timestamp),
            'username': user.username,
            'role': user.role,
            'tunggakan': data.tunggakan,
            'surat': data.surat,
            'disposisi': data.disposisi,
            'verifikasi1': data.verifikasi1,
            'komentar1': data.komentar1,
            'verifikasi2': data.verifikasi2,
            'komentar2': data.komentar2,
            'verifikasi3': data.verifikasi3,
            'komentar3': data.komentar3,
            'starttime': data.starttime,
            'endtime': data.endtime,
            'date': day_and_date(data.date),
            'name': biodata.name if biodata else '',
            'organizer': biodata.organizer if biodata else '',
            'room': room.name,
            'room_id': room.id,
            'tools': json.dumps(tools)
        })
    return render_template('wadek_2/datapeminjaman.html', results=results)

@wadek.route('/konfirmasi-satu', methods=['POST'])
@login_required
def konfirmasi_satu():
    if request.method == 'POST':
        dataId = request.form.get('dataId')
        actionSelect = request.form.get('actionSelect')
        rejected1 = request.form.get('rejected1')
        surat = request.files.get('suratDisposisiFile')

        data = BookedRoom.query.filter_by(id=dataId).first()

        if data :

            if actionSelect == "Diterima" :
                if surat and pdf_only(surat.filename):
                    user_dir = path.join(upload_folder, current_user.username)
                    if not path.exists(user_dir):
                        os.makedirs(user_dir)
                    surat.filename = f'{int(time.time())}-surat.pdf'
                    filename = path.join(user_dir, surat.filename)
                    db_file_name1 = path.join(app.config['UPLOAD_FOLDER'], current_user.username, surat.filename)
                    surat.save(filename)
                
                    if data:
                        data.verifikasi1 = actionSelect
                        data.komentar1 = rejected1
                        data.disposisi = db_file_name1
                        db.session.commit()
                        return jsonify({'status': 'success', 'message': 'Konfirmasi berhasil!'})
                    else:
                        return jsonify({'status': 'error', 'message': 'Data tidak ditemukan!'})
            
            else :

                if data:
                    data.verifikasi1 = actionSelect
                    data.komentar1 = rejected1
                    data.tunggakan = "Peminjaman Ditolak"
                    db.session.commit()
                    return jsonify({'status': 'success', 'message': 'Konfirmasi berhasil!'})
                else:
                    return jsonify({'status': 'error', 'message': 'Data tidak ditemukan!'})

    return render_template('admin/datapeminjaman.html')

@wadek.route('/konfirmasi-dua', methods=['POST'])
@login_required
def konfirmasi_dua():
    if request.method == 'POST':
        dataId = request.form.get('dataId1')
        actionSelect = request.form.get('actionSelect1')
        rejected2 = request.form.get('rejected2')

        data = BookedRoom.query.filter_by(id=dataId).first()
        
        if actionSelect == "Diterima" :
            if data:
                data.verifikasi2 = actionSelect
                db.session.commit()
                return jsonify({'status': 'success', 'message': 'Konfirmasi berhasil!'})
            else:
                return jsonify({'status': 'error', 'message': 'Data tidak ditemukan!'})
            
        else :
                
            if data:
                data.verifikasi2 = actionSelect
                data.komentar2 = rejected2
                data.tunggakan = "Peminjaman Ditolak"
                db.session.commit()
                return jsonify({'status': 'success', 'message': 'Konfirmasi berhasil!'})
            else:
                return jsonify({'status': 'error', 'message': 'Data tidak ditemukan!'})

    return render_template('admin/datapeminjaman.html')

