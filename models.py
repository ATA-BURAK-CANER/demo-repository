from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Yer(db.Model):
    __tablename__ = 'yerler'
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.Text)
    sehir = db.Column(db.Text)
    kategori = db.Column(db.Text)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    kisa = db.Column(db.Text)
    uzun = db.Column(db.Text)
    images = db.relationship('Image', backref='yer', cascade='all, delete-orphan')

class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    yer_id = db.Column(db.Integer, db.ForeignKey('yerler.id'))
    filename = db.Column(db.Text)
