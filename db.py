import sqlite3
import os
from flask import current_app

DB_NAME = 'yerler.db'

def get_db_path():
    base = os.path.dirname(__file__)
    return os.path.join(base, DB_NAME)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_conn():
    path = get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = dict_factory
    return conn

# Read helpers
def get_all_yerler():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM yerler ORDER BY id')
    rows = cur.fetchall()
    for r in rows:
        # attach images list
        cur.execute('SELECT filename FROM images WHERE yer_id = ?', (r['id'],))
        imgs = [i['filename'] for i in cur.fetchall()]
        r['images'] = imgs
    conn.close()
    return rows

def get_yer(yer_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM yerler WHERE id = ?', (yer_id,))
    r = cur.fetchone()
    if not r:
        conn.close()
        return None
    cur.execute('SELECT filename FROM images WHERE yer_id = ?', (yer_id,))
    imgs = [i['filename'] for i in cur.fetchall()]
    r['images'] = imgs
    conn.close()
    return r

# Write helpers (basic)
def add_yer(yer):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO yerler (id, isim, sehir, kategori, lat, lon, kisa, uzun) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (yer.get('id'), yer.get('isim'), yer.get('sehir'), yer.get('kategori'), yer.get('lat') or 0.0, yer.get('lon') or 0.0, yer.get('kisa') or '', yer.get('uzun') or '')
    )
    conn.commit()
    conn.close()

def update_yer(yer_id, updates):
    conn = get_conn()
    cur = conn.cursor()
    # Only update known fields
    fields = ['isim','sehir','kategori','lat','lon','kisa','uzun']
    set_parts = []
    values = []
    for f in fields:
        if f in updates:
            set_parts.append(f + ' = ?')
            values.append(updates[f])
    if set_parts:
        values.append(yer_id)
        cur.execute('UPDATE yerler SET ' + ', '.join(set_parts) + ' WHERE id = ?', values)
        conn.commit()
    conn.close()

def delete_yer(yer_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM images WHERE yer_id = ?', (yer_id,))
    cur.execute('DELETE FROM yerler WHERE id = ?', (yer_id,))
    conn.commit()
    conn.close()

# Image helpers
def add_image(yer_id, filename):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('INSERT INTO images (yer_id, filename) VALUES (?, ?)', (yer_id, filename))
    conn.commit()
    conn.close()

def delete_image(yer_id, filename):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM images WHERE yer_id = ? AND filename = ?', (yer_id, filename))
    conn.commit()
    conn.close()
