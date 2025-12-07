import sqlite3
import os
import json
from yerler_veri import YERLER as YERLER_DATA

BASE = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE, 'yerler.db')
DATA_FILE = os.path.join(BASE, 'yerler_data.json')

# Load source data: prefer yerler_data.json if present
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    data = list(YERLER_DATA)

if os.path.exists(DB_PATH):
    print('Removing existing DB at', DB_PATH)
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Create tables
cur.execute('''
CREATE TABLE yerler (
    id INTEGER PRIMARY KEY,
    isim TEXT,
    sehir TEXT,
    kategori TEXT,
    lat REAL,
    lon REAL,
    kisa TEXT,
    uzun TEXT
)
''')

cur.execute('''
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    yer_id INTEGER,
    filename TEXT,
    FOREIGN KEY(yer_id) REFERENCES yerler(id)
)
''')

# Insert data
for yer in data:
    cur.execute(
        'INSERT INTO yerler (id, isim, sehir, kategori, lat, lon, kisa, uzun) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (
            yer.get('id'),
            yer.get('isim'),
            yer.get('sehir'),
            yer.get('kategori'),
            yer.get('lat') or 0.0,
            yer.get('lon') or 0.0,
            yer.get('kisa') or '',
            yer.get('uzun') or ''
        )
    )
    # images can be stored in mekan['images'] or discovered from 'images/' prefix list
    images = yer.get('images') or []
    for img in images:
        # normalize if contains 'images/' prefix
        fn = img.replace('images/', '')
        cur.execute('INSERT INTO images (yer_id, filename) VALUES (?, ?)', (yer.get('id'), fn))

conn.commit()
conn.close()

print('Migration complete. DB created at', DB_PATH)