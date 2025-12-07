# Tarihi Yerler — Lokal Flask Uygulaması

Bu proje, yerel olarak çalışan küçük bir Flask uygulamasıdır ve tarihi mekanların listelenmesi, detaylarının gösterilmesi, harita entegrasyonu ve fotoğraf yönetimi özelliklerini içerir.

Özet (güncel)
- Veri deposu: SQLite (`yerler.db`) — uygulama artık veriyi veritabanında tutar.
- Yönetim (admin): Basit bir admin paneli var; admin kullanıcı adı `admin`, şifre `adana01`.
- Fotoğraflar: Yüklenen resimler `static/images/` içindedir.

Hızlı kurulum
1. Python 3.11+ kullanın.
2. Sanal ortam oluşturun ve etkinleştirin (önerilir):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Gerekli paketleri yükleyin:

```powershell
pip install -r requirements.txt
```

4. Uygulamayı çalıştırın:

```powershell
python app.py
```

Uygulama sonra `http://127.0.0.1:5000/` üzerinde erişilebilir.

Admin paneli
- Giriş: `http://127.0.0.1:5000/admin` (kullanıcı: `admin`, şifre: `adana01`).
- Fotoğraf yüklemek, yeni mekan eklemek ve mevcut kayıtları düzenlemek için admin panelini kullanın.

Notlar ve temizlik
- Proje geçmişinde oluşturulmuş bazı test/bakım dosyaları kaldırıldı (yedeği `.bak` dosyası vb.).
- Veriler artık `yerler.db` içindedir; eğer JSON dosyaları veya yedekler görünüyorsa, bunlar silinmiştir.

Destek ve geliştirme
- Yeni mekan eklemek için admin panelini kullanın veya doğrudan veritabanını düzenleyin (SQLite araçları).
- İsterseniz uygulamayı bir WSGI sunucusuna (gunicorn/uwsgi) taşıyıp üretime alabilirsiniz.

İyi çalışmalar!

-Burak Özbebek 240307040
-Ata Bakır
-Caner Gezek
