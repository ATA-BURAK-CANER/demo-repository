# Ankara Kültür & Sanat - Temel Flask Projesi

Bu repo, proje ödevi için hızlı bir Flask iskeleti sağlar: etkinlik listesi, kategori filtreleme, takvim API'si ve basit admin CRUD.

Hızlı başlatma

1. Python sanal ortam oluşturun ve aktif edin (PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Bağımlılıkları yükleyin:

```powershell
pip install -r requirements.txt
```

3. Çevresel değişkenleri ayarlayın (örnek: `.env.example`):

```powershell
copy .env.example .env
# Düzenleyin .env içinde ADMIN_PASSWORD ve SECRET_KEY
```

4. Veritabanını başlatın ve örnek veri ekleyin:

```powershell
python init_db.py
```

5. Uygulamayı çalıştırın:

```powershell
python app.py
```

Admin paneli: `http://127.0.0.1:5000/admin/login` (şifre `.env` içinde `ADMIN_PASSWORD`).

Geliştirme notları:
- `templates/` içinde basit Jinja2 şablonları var.
- Takvim verisi: `/api/calendar` (ISO tarih ile filtreleme desteklenir).
- Bu temel iskeleti isteklerinize göre genişletebiliriz (e-posta bildirimleri, API auth, front-end takvim entegrasyonu vb.).
