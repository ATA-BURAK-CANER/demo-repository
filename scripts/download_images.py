"""
Gelişmiş indirme betiği (Wikimedia Commons arama + indirme).

Betik `app.YERLER` listesindeki mekan isimlerini kullanarak Wikimedia Commons'ta
her mekan için uygun bir dosya arar ve ilk bulunan görselin orijinal dosya
URL'sini indirir. İndirilen dosyalar `static/images/place-<id>.<ext>` olarak
kaydedilir.

Kullanım (PowerShell):
    pip install -r requirements.txt; python .\scripts\download_images.py

Uyarılar:
- Betik otomatik eşleştirme yapar, yanlış resim seçebilir. Lütfen indirilenleri
  kontrol edin.
- Wikimedia Commons üzerindeki lisans bilgilerini kontrol edin. Sadece izinli
  kullanım amaçlı görselleri dağıtın.
"""

import os
import time
import requests
from urllib.parse import quote

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IMG_DIR = os.path.join(ROOT, 'static', 'images')
os.makedirs(IMG_DIR, exist_ok=True)

API_ENDPOINT = 'https://commons.wikimedia.org/w/api.php'

session = requests.Session()
session.headers.update({'User-Agent': 'AnkaraTarihiMekanlarBot/1.0 (ozbeb)'} )

try:
    from app import YERLER
except Exception as e:
    print('Hata: app.YERLER yüklenemedi:', e)
    YERLER = []


def find_file_title(query):
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srsearch': query,
        'srnamespace': 6,  # File namespace
        'srlimit': 1
    }
    r = session.get(API_ENDPOINT, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    hits = data.get('query', {}).get('search', [])
    if not hits:
        return None
    return hits[0].get('title')


def get_imageinfo_for_title(title):
    params = {
        'action': 'query',
        'format': 'json',
        'titles': title,
        'prop': 'imageinfo',
        'iiprop': 'url|extmetadata'
    }
    r = session.get(API_ENDPOINT, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    pages = data.get('query', {}).get('pages', {})
    for pid, page in pages.items():
        ii = page.get('imageinfo')
        if ii:
            return ii[0]
    return None


def download_url(url, dest):
    try:
        with session.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(dest, 'wb') as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
        return True
    except Exception as e:
        print('  İndirme hatası:', e)
        return False


def main():
    if not YERLER:
        print('YERLER listesi boş veya app.py yüklenemedi.')
        return

    results = []
    for yer in YERLER:
        pid = yer.get('id')
        name = yer.get('isim')
        print(f'[{pid}] Aranıyor: {name}')

        title = find_file_title(name + ' Turkey') or find_file_title(name)
        if not title:
            print('  Görsel bulunamadı.')
            results.append((pid, name, 'not found'))
            time.sleep(1)
            continue

        print('  Bulunan başlık:', title)
        info = get_imageinfo_for_title(title)
        if not info:
            print('  imageinfo alınamadı.')
            results.append((pid, name, 'no-imageinfo'))
            time.sleep(1)
            continue

        img_url = info.get('url')
        if not img_url:
            print('  URL yok.')
            results.append((pid, name, 'no-url'))
            time.sleep(1)
            continue

        ext = os.path.splitext(img_url)[1].lower()
        if ext not in ('.jpg', '.jpeg', '.png', '.webp'):
            ext = '.jpg'
        dest_name = f'place-{pid}{ext}'
        dest_path = os.path.join(IMG_DIR, dest_name)

        print('  İndiriliyor:', img_url)
        ok = download_url(img_url, dest_path)
        if ok:
            print('  Kaydedildi ->', dest_name)
            results.append((pid, name, dest_name))
        else:
            results.append((pid, name, 'download-failed'))

        time.sleep(1)

    print('\nÖzet:')
    for r in results:
        print(' -', r)


if __name__ == '__main__':
    main()
