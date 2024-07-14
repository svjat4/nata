import uuid
from flask_login import UserMixin
from .. import db
from datetime import datetime
from sqlalchemy import Date

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(150), nullable=False)

    profile_relationship = db.relationship('Biodata', backref='user', uselist=False)
    booked_rooms = db.relationship('BookedRoom', backref='users')

class Biodata(db.Model):
    __tablename__ = 'biodatas'

    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), default="")
    position = db.Column(db.String(255), default="")
    organizer = db.Column(db.String(255), default="")

    user_id = db.Column(db.String(150), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user_relationship = db.relationship('User', backref='biodatas')

class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), default="")
    capacity = db.Column(db.String(255), default="")
    status = db.Column(db.String(255), default="")
    default = db.Column(db.String(255), default="True")

class Tool(db.Model):
    __tablename__ = 'tools'

    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), default="")
    capacity = db.Column(db.String(255), default="")

    tool_booked = db.relationship('BookedTool', backref='tools')

class BookedRoom(db.Model):
    __tablename__ = 'bookedrooms'

    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = db.Column(db.DateTime, default=datetime.now)
    starttime = db.Column(db.Time, nullable=False)
    endtime = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    disposisi = db.Column(db.String(255), default="-")
    surat = db.Column(db.String(255), default="-")
    tunggakan = db.Column(db.String(255), default="")
    isUsed = db.Column(db.String(255), default="Yes")
    verifikasi1 = db.Column(db.String(255), default="")
    komentar1 = db.Column(db.String(1000), default="")
    verifikasi2 = db.Column(db.String(255), default="")
    komentar2 = db.Column(db.String(1000), default="")
    verifikasi3 = db.Column(db.String(255), default="")
    komentar3 = db.Column(db.String(1000), default="")

    user_id = db.Column(db.String(150), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    room_id = db.Column(db.String(150), db.ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False)

    user_relationship = db.relationship('User', backref='bookedrooms')
    room_relationship = db.relationship('Room', backref='bookedrooms')
    bookedtool_relationship = db.relationship('BookedTool', backref='bookedrooms')

class BookedTool(db.Model):
    __tablename__ = 'bookedtools'

    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    quantity = db.Column(db.String(255), default="")

    bookedrooms_id = db.Column(db.String(150), db.ForeignKey('bookedrooms.id', ondelete='CASCADE'), nullable=False)
    tool_id = db.Column(db.String(150), db.ForeignKey('tools.id', ondelete='CASCADE'), nullable=False)

    tool_relationship = db.relationship('Tool', backref='bookedtools')
    booked_relationship = db.relationship('BookedRoom', backref='bookedtools')

# class Disposisi(db.Model):
#     __tablename__ = 'disposisi'

#     id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
#     nomor_disposisi = db.Column(db.String(255), nullable=False)
#     from_disposisi = db.Column(db.String(255), nullable=False)
#     nomor_surat = db.Column(db.String(255), nullable=False)
#     tanggal_surat = db.Column(db.Date, nullable=True)
#     perihal = db.Column(db.String(255), nullable=False)
#     lampiran = db.Column(db.Boolean, default=False)

#     tanggal_diterima = db.Column(db.Date, nullable=True)
#     penerima = db.Column(db.String(255), nullable=False)
#     sifat = db.Column(db.String(255), nullable=True)
#     klasifikasi = db.Column(db.String(255), nullable=True)

#     ditunjukkan_wadek1 = db.Column(db.Boolean, default=False)
#     ditunjukkan_wadek2 = db.Column(db.Boolean, default=False)

#     ditembuskan_ka_spm = db.Column(db.Boolean, default=False)
#     ditembuskan_ka_prodi_si = db.Column(db.Boolean, default=False)
#     ditembuskan_ka_prodi_ti = db.Column(db.Boolean, default=False)
#     ditembuskan_ka_informatika = db.Column(db.Boolean, default=False)
#     ditembuskan_ka_gkm = db.Column(db.Boolean, default=False)
#     ditembuskan_kabag_ak = db.Column(db.Boolean, default=False)
#     ditembuskan_kabag_uk = db.Column(db.Boolean, default=False)
#     ditembuskan_ka_lab = db.Column(db.Boolean, default=False)

#     disposisi_ditindaklanjuti = db.Column(db.Boolean, default=False)
#     disposisi_siap_sambutan = db.Column(db.Boolean, default=False)
#     disposisi_siap_menghadiri = db.Column(db.Boolean, default=False)
#     disposisi_koordinasikan = db.Column(db.Boolean, default=False)
#     disposisi_wakili_dekan = db.Column(db.Boolean, default=False)
#     disposisi_review_feasibility = db.Column(db.Boolean, default=False)
#     disposisi_pertimbangkan = db.Column(db.Boolean, default=False)
#     disposisi_fasilitasi = db.Column(db.Boolean, default=False)
#     disposisi_arsipkan = db.Column(db.Boolean, default=False)

#     catatan = db.Column(db.String(255), nullable=True)
#     tanggal_ttd = db.Column(db.Date, nullable=True)
#     nama_ttd = db.Column(db.String(255), nullable=True)