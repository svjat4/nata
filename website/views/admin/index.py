from flask_login import login_required

from website.utils.filters import day_and_date
from ... import db
from ...models.user import Biodata, BookedRoom, Room, Tool, User
from flask import Blueprint, jsonify, render_template, redirect, send_from_directory, url_for, request, flash
from werkzeug.security import generate_password_hash
from pathlib import Path
from ... import db, app
from os import path

admin = Blueprint('admin', __name__)

upload_images = path.join(Path(__file__).parents[2], "static", app.config['UPLOAD_FOLDER'])

@admin.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    booked = BookedRoom.query.filter_by(isUsed="Yes").all()
    booked1 = BookedRoom.query.filter_by(isUsed="No").all()
    return render_template('admin/beranda.html', booked=booked, booked1=booked1)

################################################ USER ################################################

@admin.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    user = Biodata.query.all()
    return render_template('admin/user.html', user=user)

@admin.route('/add-user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        nama = request.form.get('nama')
        role = request.form.get('role')
        prodi = request.form.get('prodi')
        jabatan = request.form.get('jabatan')
        username = request.form.get('username')
        password = request.form.get('password')

        # Validasi data
        if not all([nama, role, prodi, jabatan, username, password]):
            flash('Semua bidang harus diisi.', 'error')
            return redirect(url_for('admin.user'))

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('NPM sudah terdaftar. Silakan gunakan NPM lain.', category='error')
            return redirect(url_for('admin.user'))

        else :

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            new_user = User(username=username, password=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()

            # Tambahkan data ke database
            new_profile = Biodata(name=nama, position=jabatan, organizer=prodi,user_id=new_user.id)
            db.session.add(new_profile)
            db.session.commit()
            
            flash('Akun berhasil ditambahkan!', 'success')
            return redirect(url_for('admin.user'))
        
    return render_template('admin/user.html')

@admin.route('/get-user-data/<user_id>', methods=['GET'])
@login_required
def get_user_data(user_id):
    data = Biodata.query.filter_by(id=user_id).first()
    if not data:
        return jsonify({'message': 'Data tidak ditemukan'}), 404

    user = {
        'id': user_id,
        'user_relationship': {
            'username': data.user_relationship.username,
            'role': data.user_relationship.role
        },
        'name': data.name,
        'organizer': data.organizer,
        'position': data.position
    }
    return jsonify(user)

@admin.route('/update-user', methods=['POST'])
@login_required
def update_user():
    if request.method == 'POST':
        editId = request.form.get('editId')
        name = request.form.get('name')
        prodi = request.form.get('prodi')
        jabatan = request.form.get('jabatan')
        username = request.form.get('username')
        password = request.form.get('password')

        biodata = Biodata.query.filter_by(id=editId).first()

        # Update data user dan biodata
        user = User.query.get(biodata.user_id)
        if not user:
            flash('User tidak ditemukan.', 'error')
            return redirect(url_for('admin.user'))

        user.username = username

        if not biodata:
            flash('Biodata user tidak ditemukan.', 'error')
            return redirect(url_for('admin.user'))

        biodata.name = name
        biodata.organizer = prodi
        biodata.position = jabatan

        if password:
            user.password = generate_password_hash(password, method='pbkdf2:sha256')

        db.session.commit()

        flash('Data user berhasil diperbarui!', 'success')
        return redirect(url_for('admin.user'))

    return render_template('admin/user.html')

@app.route('/delete-user/<string:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    biodata = Biodata.query.filter_by(user_id=user_id).first()
    try:
        db.session.delete(biodata)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user'}), 500
    
################################################ RUANGAN ################################################
    
@admin.route('/ruangan', methods=['GET', 'POST'])
@login_required
def ruangan():
    room = Room.query.filter_by(default="True").all()
    return render_template('admin/ruangan.html', room=room)

@admin.route('/add-room', methods=['GET', 'POST'])
@login_required
def add_room():
    if request.method == 'POST':
        name = request.form.get('name')
        capacity = request.form.get('capacity')

        # Validasi data
        if not all([name, capacity]):
            flash('Semua bidang harus diisi.', 'error')
            return redirect(url_for('admin.ruangan'))

        # Check if username already exists
        existing = Room.query.filter_by(name=name).first()
        if existing:
            flash('Ruangan sudah terdaftar.', category='error')
            return redirect(url_for('admin.ruangan'))

        else :

            new = Room(name=name, capacity=capacity, status="Tidak Terpakai")
            db.session.add(new)
            db.session.commit()

            flash('Akun berhasil ditambahkan!', 'success')
            return redirect(url_for('admin.ruangan'))
        
    return render_template('admin/user.html')

@admin.route('/get-room-data/<id>', methods=['GET'])
@login_required
def get_room_data(id):
    data = Room.query.filter_by(id=id).first()
    if not data:
        return jsonify({'message': 'Data tidak ditemukan'}), 404

    user = {
        'id': id,
        'name': data.name,
        'capacity': data.capacity,
        'status': data.status
    }
    return jsonify(user)

@admin.route('/update-room', methods=['POST'])
@login_required
def update_room():
    if request.method == 'POST':
        editId = request.form.get('editId')
        name = request.form.get('name')
        capacity = request.form.get('capacity')

        data = Room.query.filter_by(id=editId).first()
        if not data:
            flash('Data ruangan tidak ditemukan.', 'error')
            return redirect(url_for('admin.ruangan'))

        data.name = name
        data.capacity = capacity
        db.session.commit()

        # flash('Data berhasil diperbarui!', 'success')
        return redirect(url_for('admin.room'))

    return render_template('admin/ruangan.html')

@app.route('/delete-room/<string:id>', methods=['DELETE'])
@login_required
def delete_room(id):
    data = Room.query.get_or_404(id)
    try:
        db.session.delete(data)
        db.session.commit()
        return jsonify({'message': 'Data deleted successfully'}), 200
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'error': 'Failed to delete data'}), 500

################################################ ALAT ################################################

@admin.route('/alat-alat', methods=['GET', 'POST'])
@login_required
def alat():
    data = Tool.query.all()
    results = []
    for tool in data:
        tool_booked = [{'quantity': '0'}] if not tool.tool_booked else []
        for booked_tool in tool.tool_booked:
            if booked_tool.booked_relationship.tunggakan == "Ada":
                tool_booked.append({'quantity': booked_tool.quantity})
            else:
                tool_booked.append({'quantity': "0"})
        
        results.append({
            'id': tool.id,
            'name': tool.name,
            'capacity': tool.capacity,
            'tool_booked': tool_booked,
        })

    return render_template('admin/alat.html', data=results)

@admin.route('/add-alat', methods=['GET', 'POST'])
@login_required
def add_alat():
    if request.method == 'POST':
        name = request.form.get('name')
        capacity = request.form.get('capacity')

        # Validasi data
        if not all([name, capacity]):
            flash('Semua bidang harus diisi.', 'error')
            return redirect(url_for('admin.alat'))

        existing = Tool.query.filter_by(name=name).first()
        if existing:
            flash('Alat sudah terdaftar.', category='error')
            return redirect(url_for('admin.alat'))

        else :

            new = Tool(name=name, capacity=capacity)
            db.session.add(new)
            db.session.commit()

            flash('Data berhasil ditambahkan!', 'success')
            return redirect(url_for('admin.alat'))
        
    return render_template('admin/alat.html')

@admin.route('/get-alat-data/<id>', methods=['GET'])
@login_required
def get_alat_data(id):
    data = Tool.query.filter_by(id=id).first()
    if not data:
        return jsonify({'message': 'Data tidak ditemukan'}), 404

    user = {
        'id': id,
        'name': data.name,
        'capacity': data.capacity,
    }
    return jsonify(user)

@admin.route('/update-alat', methods=['POST'])
@login_required
def update_alat():
    if request.method == 'POST':
        editId = request.form.get('editId')
        name = request.form.get('name')
        capacity = request.form.get('capacity')

        data = Tool.query.filter_by(id=editId).first()
        if not data:
            flash('Data alat tidak ditemukan.', 'error')
            return redirect(url_for('admin.alat'))

        data.name = name
        data.capacity = capacity
        db.session.commit()

        # flash('Data berhasil diperbarui!', 'success')
        return redirect(url_for('admin.alat'))

    return render_template('admin/alat.html')

@app.route('/delete-alat/<string:id>', methods=['DELETE'])
@login_required
def delete_alat(id):
    data = Tool.query.get_or_404(id)
    try:
        db.session.delete(data)
        db.session.commit()
        return jsonify({'message': 'Data deleted successfully'}), 200
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'error': 'Failed to delete data'}), 500
    

################################################ DATA PEMINAJMAN ################################################

@admin.route('storage/<path:filename>')
@login_required
def storage(filename):
    npm = filename.split('/')[0]
    name = filename.split('_')[-1]
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True, download_name=f'{npm}_{name}')

@admin.route('/data-peminjaman', methods=['GET', 'POST'])
@login_required
def data_peminjaman():
    booked = BookedRoom.query.filter_by(isUsed="Yes").all()
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
            'disposisi': data.disposisi,
            'surat': data.surat,
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
    return render_template('admin/datapeminjaman.html', results=results)

@admin.route('/konfirmasi-tiga', methods=['POST'])
@login_required
def konfirmasi_tiga():
    dataId = request.form.get('dataId')
    roomId = request.form.get('roomId')
    actionSelect = request.form.get('actionSelect')
    rejected = request.form.get('rejected')

    data = BookedRoom.query.filter_by(id=dataId).first()
    dataRoom = Room.query.filter_by(id=roomId).first()

    if actionSelect == "Diterima" :
        if data:
            data.verifikasi3 = actionSelect
            data.tunggakan = "Ada"
            if dataRoom.name != "Tidak Meminjam Ruangan" :
                dataRoom.status = "Terpakai"
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Konfirmasi berhasil!'})
        else:
            return jsonify({'status': 'error', 'message': 'Data tidak ditemukan!'})
            
    else :
                
        if data:
            data.verifikasi3 = actionSelect
            data.komentar3 = rejected
            data.tunggakan = "Peminjaman Ditolak"
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Konfirmasi berhasil!'})
        else:
            return jsonify({'status': 'error', 'message': 'Data tidak ditemukan!'})
    
import json

@admin.route('/data-pengembalian', methods=['GET', 'POST'])
@login_required
def data_pengembalian():
    booked = BookedRoom.query.filter_by(isUsed="No").all()
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
            'verifikasi1': data.verifikasi1,
            'verifikasi2': data.verifikasi2,
            'verifikasi3': data.verifikasi3,
            'starttime': data.starttime,
            'endtime': data.endtime,
            'date': day_and_date(data.date),
            'name': biodata.name if biodata else '',
            'organizer': biodata.organizer if biodata else '',
            'room': room.name,
            'room_id': room.id,
            'tools': json.dumps(tools)
        })
    return render_template('admin/datapengembalian.html', results=results)


@admin.route('/konfirmasi-pengembalian', methods=['POST'])
@login_required
def konfirmasi_pengembalian():
    dataId = request.form.get('dataId')
    roomId = request.form.get('roomId')

    data = BookedRoom.query.filter_by(id=dataId).first()
    dataRoom = Room.query.filter_by(id=roomId).first()

    if data and dataRoom:
        data.tunggakan = "Tidak ada"
        dataRoom.status = "Tidak Terpakai"
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Konfirmasi berhasil!'})
    else:
        return jsonify({'status': 'error', 'message': 'Data tidak ditemukan!'})