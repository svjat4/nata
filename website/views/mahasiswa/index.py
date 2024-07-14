from datetime import datetime
import os
import time

from website.utils.filters import day_and_date
from website.utils.func import allowed_file_size, pdf_only
from ...models.user import BookedRoom, BookedTool, Room, Tool, User
from flask import Blueprint, jsonify, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from pathlib import Path
from ... import app
from os import path
from ... import db

students = Blueprint('students', __name__)

upload_images = path.join(Path(__file__).parents[2], "static", app.config['UPLOAD_FOLDER'])
upload_folder = path.join(Path(__file__).parents[2], app.config['UPLOAD_FOLDER'])

@students.route('/dashboard-mahasiswa', methods=['GET', 'POST'])
@login_required
def dashboard():
    booked = BookedRoom.query.filter_by(isUsed="Yes", user_id=current_user.id).all()
    booked1 = BookedRoom.query.filter_by(isUsed="No", user_id=current_user.id).all()
    booked_room_with_tunggakan = BookedRoom.query.filter_by(isUsed="Yes", tunggakan="Ada", user_id=current_user.id, verifikasi3="Diterima").all()
    return render_template('mahasiswa/beranda.html', booked=booked, booked1=booked1, booked_room_with_tunggakan=booked_room_with_tunggakan)

@students.route('/form-peminjaman', methods=['GET', 'POST'])
@login_required
def form_peminjaman():
    rooms = Room.query.filter_by(status="Tidak Terpakai").all() 
    data = Tool.query.all()
    tools = []
    for tool in data:
        total_booked = sum(int(booked_tool.quantity) for booked_tool in tool.tool_booked if booked_tool.booked_relationship.tunggakan == "Ada")
        remaining_stock = int(tool.capacity) - total_booked
        
        tools.append({
            'id': tool.id, 
            'name': tool.name,
            'capacity': tool.capacity,
            'remaining_stock': remaining_stock,
        })
    
    # baru saja melakukan proses peminjaman
    isUsed = BookedRoom.query.filter_by(isUsed='Yes', tunggakan="-", user_id=current_user.id).first() 
    # sudah di acc
    isUsed1 = BookedRoom.query.filter_by(isUsed='Yes', tunggakan="Ada", verifikasi1="Diterima", verifikasi2="Diterima", verifikasi3="Diterima", user_id=current_user.id).first() 
    # sedang mengembalikan
    isUsed2 = BookedRoom.query.filter_by(isUsed='No', tunggakan="Ada", user_id=current_user.id, verifikasi1="Diterima", verifikasi2="Diterima", verifikasi3="Diterima").first() 

    return render_template('mahasiswa/peminjaman.html', rooms=rooms, tools=tools, isUsed=isUsed, isUsed1=isUsed1, isUsed2=isUsed2)

# Route untuk halaman form peminjaman
@students.route('/add-peminjaman', methods=['GET', 'POST'])
@login_required
def add_peminjaman():
    if request.method == 'POST':
        # Ambil data dari form
        room_id = request.form['room']
        starttime = request.form['starttime']
        endtime = request.form['endtime']
        date = request.form['date']
        tools_selected = request.form.getlist('tools[]')
        quantities = request.form.getlist('quantities[]')
        peminjaman = request.files.get('peminjaman') 

        # Convert starttime and endtime to datetime objects for comparison
        start_datetime = datetime.strptime(f"{date} {starttime}", '%Y-%m-%d %H:%M')
        end_datetime = datetime.strptime(f"{date} {endtime}", '%Y-%m-%d %H:%M')

        # Check for overlapping bookings
        overlapping_bookings = BookedRoom.query.filter(
            BookedRoom.room_id == room_id,
            BookedRoom.date == date,
            BookedRoom.starttime < end_datetime.time(),
            BookedRoom.endtime > start_datetime.time()
        ).all()

        if overlapping_bookings:
            flash('Peminjaman sudah ada pada jam tersebut.', 'danger')
            return redirect(url_for('students.form_peminjaman'))

        if peminjaman and pdf_only(peminjaman.filename):
            user_dir = path.join(upload_folder, current_user.username)
            if not path.exists(user_dir):
                os.makedirs(user_dir)
            peminjaman.filename = f'{int(time.time())}-peminjaman.pdf'
            filename = path.join(user_dir, peminjaman.filename)
            db_file_name1 = path.join(app.config['UPLOAD_FOLDER'], current_user.username, peminjaman.filename)
            peminjaman.save(filename)

            # Buat objek BookedRoom
            new_booked_room = BookedRoom(
                starttime=start_datetime.time(),
                endtime=end_datetime.time(),
                date=start_datetime.date(),
                verifikasi1="Pending", 
                verifikasi2="Pending", 
                verifikasi3="Pending", 
                user_id=current_user.id, 
                tunggakan="-", 
                room_id=room_id,
                surat=db_file_name1
            )

            db.session.add(new_booked_room)
            db.session.commit()

            if tools_selected and quantities :
            
                for i in range(len(tools_selected)):
                    tool_id = tools_selected[i]
                    quantity = quantities[i]

                    new_booked_tool = BookedTool(
                        quantity=quantity,
                        tool_id=tool_id,
                        bookedrooms_id=new_booked_room.id
                    )

                    db.session.add(new_booked_tool)

                db.session.commit()

        flash('Peminjaman berhasil dibuat.', 'success')
        return redirect(url_for('students.data_peminjaman'))

    rooms = Room.query.filter_by(status="Tidak Terpakai").all() 
    tools = Tool.query.all()
    return render_template('mahasiswa/peminjaman.html', rooms=rooms, tools=tools)
    
@students.route('/peminjaman-saya', methods=['GET', 'POST'])
@login_required
def data_peminjaman():
    booked = BookedRoom.query.filter_by(user_id=current_user.id, isUsed="Yes").all()
    results = []
    for data in booked:
        user = data.user_relationship
        biodata = user.profile_relationship
        room = data.room_relationship
        results.append({
            'id': data.id,
            'timestamp': day_and_date(data.timestamp),
            'username': user.username,
            'role': user.role,
            'surat': data.surat,
            'tunggakan': data.tunggakan,
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
            'room' : room.name,
            'tools' : [
                {
                    'name': booked_tool.tool_relationship.name,
                    'capacity': booked_tool.tool_relationship.capacity
                }
                for booked_tool in data.bookedtool_relationship
            ]
        })

    return render_template('mahasiswa/datapeminjaman.html', results=results)

@students.route('/form-pengembalian', methods=['GET', 'POST'])
@login_required
def form_pengembalian():
    
    # setelah ngisi form
    booked_room1 = BookedRoom.query.filter_by(isUsed="Yes", tunggakan="-", user_id=current_user.id).first()

    # semua sudah di acc
    booked_room_with_tunggakan = BookedRoom.query.filter_by(isUsed="Yes", tunggakan="Ada", user_id=current_user.id, verifikasi3="Diterima").first()

    # sudah klik pengembalian
    booked_room3 = BookedRoom.query.filter_by(isUsed="No", tunggakan="Ada", user_id=current_user.id).first()

    # tidak ada tunggakan
    booked_room4 = BookedRoom.query.filter_by(isUsed="No", tunggakan="Tidak ada", user_id=current_user.id).first()
    
    booked_tools = []
    tools = []
    if booked_room_with_tunggakan:
        booked_tools = BookedTool.query.filter_by(bookedrooms_id=booked_room_with_tunggakan.id).all()
        tool_ids = [booked_tool.tool_id for booked_tool in booked_tools]
        tools = Tool.query.filter(Tool.id.in_(tool_ids)).all()
    
    return render_template('mahasiswa/pengembalian.html', booked_room=booked_room_with_tunggakan, booked_room1=booked_room1, booked_tools=booked_tools, tools=tools, booked_room3=booked_room3, booked_room4=booked_room4)
    
@students.route('/konfirmasi-pengembalian-mhs', methods=['POST'])
@login_required
def konfirmasi_pengembalian_mhs():
    if request.method == 'POST':
        dataId = request.form.get('dataId')

        data = BookedRoom.query.filter_by(id=dataId).first()
        
        if data:
            data.isUsed = "No"
            db.session.commit()
            return redirect(url_for('students.data_pengembalian'))
        else:
            return redirect(url_for('students.form_pengembalian'))

    return render_template('mahasiswa/datapeminjaman.html')

import json
@students.route('/data-pengembalian-mahasiswa', methods=['GET', 'POST'])
@login_required
def data_pengembalian():
    booked = BookedRoom.query.filter_by(isUsed="No", user_id=current_user.id).all()
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
    return render_template('mahasiswa/datapengembalian.html', results=results)