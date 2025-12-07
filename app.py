from flask import (
    Flask, render_template, jsonify, abort, request, redirect,
    url_for, flash, session
)
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import timedelta
import os
import glob
import json
from yerler_veri import YERLER as YERLER_DATA
from models import db, Yer, Image

app = Flask(__name__)
CORS(app)
app.secret_key = 'dev_secret_key_adana'
app.permanent_session_lifetime = timedelta(days=30)
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'images')
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Configure SQLAlchemy to reuse the migrated SQLite DB (created by migrate_to_sqlite.py)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'yerler.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'adana01'
DATA_FILE = os.path.join(app.root_path, 'yerler_data.json')


def load_data():
    """Load yerler data from JSON file if present, otherwise use
    bundled data.
    """
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            # If load fails, fall back to bundled data
            return list(YERLER_DATA)
    return list(YERLER_DATA)


def save_data(data):
    """Persist yerler data to JSON file."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        app.logger.error('Failed to save data: %s', e)


# Load data into memory (will persist to `yerler_data.json` when changed)
YERLER = load_data()


def model_to_dict(yer):
    """Convert a `Yer` SQLAlchemy model to a plain dict compatible with templates."""
    return {
        'id': yer.id,
        'isim': yer.isim,
        'sehir': yer.sehir,
        'kategori': yer.kategori,
        'lat': yer.lat,
        'lon': yer.lon,
        'kisa': yer.kisa,
        'uzun': yer.uzun,
    }


def get_all_yerler_db():
    """Return list of yer dicts from DB in the same shape as old `YERLER` list."""
    try:
        with app.app_context():
            rows = Yer.query.order_by(Yer.id).all()
            return [model_to_dict(r) for r in rows]
    except Exception:
        return YERLER


def get_yer_db(yer_id):
    try:
        with app.app_context():
            y = Yer.query.get(yer_id)
            return model_to_dict(y) if y else None
    except Exception:
        return next((y for y in YERLER if y['id'] == yer_id), None)


def get_images_for_place(place_id, position='all'):
    """Find images from disk for a specific place ID."""
    img_files = []
    for pattern in [f'{place_id}-*', f'{place_id}.*']:
        img_files.extend(glob.glob(os.path.join(UPLOAD_FOLDER, pattern)))

    if img_files:
        return [
            'images/' + os.path.basename(f)
            for f in sorted(set(img_files))
        ]
    return []


def allowed_file(filename):
    """Check if file extension is allowed."""
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT
    )


def is_admin():
    """Check if user is logged in as admin."""
    return session.get('admin_logged_in', False)


@app.context_processor
def inject_utils():
    """Inject utility functions into templates."""
    return dict(get_images_for_place=get_images_for_place, is_admin=is_admin)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page with remember me functionality."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember_me')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            if remember:
                session.permanent = True
            session['admin_logged_in'] = True
            flash('Admin girişi başarılı', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Kullanıcı adı veya şifre hatalı', 'error')

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    """Logout from admin panel."""
    session.clear()
    flash('Çıkış yapıldı', 'success')
    return redirect(url_for('index'))


@app.route('/admin')
def admin_dashboard():
    """Admin dashboard - list all locations."""
    if not is_admin():
        flash('Admin girişi gereklidir', 'error')
        return redirect(url_for('admin_login'))

    # prefer DB-backed data; fallback to JSON list
    yerler = get_all_yerler_db()
    return render_template('admin_dashboard.html', yerler=yerler)


@app.route('/admin/mekan/new', methods=['GET', 'POST'])
def admin_new_mekan():
    """Add new location."""
    if not is_admin():
        flash('Admin girişi gereklidir', 'error')
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        # create a new Yer via SQLAlchemy
        try:
            with app.app_context():
                # determine new id (auto if missing) - we allow specifying id by DB auto-increment
                yer = Yer(
                    isim=request.form.get('isim', ''),
                    sehir=request.form.get('sehir', ''),
                    kategori=request.form.get('kategori', ''),
                    lat=float(request.form.get('lat', 0) or 0),
                    lon=float(request.form.get('lon', 0) or 0),
                    kisa=request.form.get('kisa', ''),
                    uzun=request.form.get('uzun', ''),
                )
                db.session.add(yer)
                db.session.commit()
                flash(f'Yeni mekan eklendi (ID: {yer.id})', 'success')
                return redirect(url_for('admin_dashboard'))
        except Exception as e:
            app.logger.exception('Failed to create new mekan via DB: %s', e)
            flash('Yeni mekan eklenirken hata oluştu (DB)', 'error')
            return redirect(url_for('admin_dashboard'))

    rows = get_all_yerler_db()
    cities = sorted(set(y['sehir'] for y in rows))
    categories = sorted(set(y['kategori'] for y in rows))
    return render_template(
        'admin_mekan_form.html',
        mekan=None,
        cities=cities,
        categories=categories
    )


@app.route('/admin/mekan/<int:mekan_id>/edit', methods=['GET', 'POST'])
def admin_edit_mekan(mekan_id):
    """Edit existing location."""
    if not is_admin():
        flash('Admin girişi gereklidir', 'error')
        return redirect(url_for('admin_login'))

    mekan = get_yer_db(mekan_id)
    if not mekan:
        abort(404)

    if request.method == 'POST':
        # update via DB if possible
        try:
            with app.app_context():
                y = Yer.query.get(mekan_id)
                if not y:
                    abort(404)
                y.isim = request.form.get('isim', '')
                y.sehir = request.form.get('sehir', '')
                y.kategori = request.form.get('kategori', '')
                y.lat = float(request.form.get('lat', y.lat or 0) or 0)
                y.lon = float(request.form.get('lon', y.lon or 0) or 0)
                y.kisa = request.form.get('kisa', '')
                y.uzun = request.form.get('uzun', '')
                db.session.commit()
                flash('Mekan güncellendi', 'success')
                return redirect(url_for('admin_dashboard'))
        except Exception as e:
            app.logger.exception('Failed to update mekan via DB: %s', e)
            flash('Mekan güncellenirken hata oluştu (DB)', 'error')
            return redirect(url_for('admin_dashboard'))

    cities = sorted(set(y['sehir'] for y in YERLER))
    categories = sorted(set(y['kategori'] for y in YERLER))
    images = get_images_for_place(mekan_id)

    return render_template(
        'admin_mekan_form.html',
        mekan=mekan,
        cities=cities,
        categories=categories,
        images=images
    )


@app.route('/admin/mekan/<int:mekan_id>/delete', methods=['POST'])
def admin_delete_mekan(mekan_id):
    """Delete a location."""
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    # prefer DB deletion
    try:
        with app.app_context():
            y = Yer.query.get(mekan_id)
            if y:
                db.session.delete(y)
                db.session.commit()
        flash('Mekan silindi', 'success')
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        app.logger.exception('Failed to delete mekan via DB: %s', e)
        flash('Mekan silinirken hata oluştu (DB)', 'error')
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/upload/<int:mekan_id>', methods=['POST'])
def admin_upload_image(mekan_id):
    """Upload image for a location from admin panel."""
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    if 'file' not in request.files:
        flash('Dosya seçilmedi', 'error')
        return redirect(url_for('admin_edit_mekan', mekan_id=mekan_id))

    file = request.files['file']
    if file.filename == '':
        flash('Dosya adı boş', 'error')
        return redirect(url_for('admin_edit_mekan', mekan_id=mekan_id))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        new_filename = f"{mekan_id}-both-{base}{ext}"
        dest = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(dest)
        # record the uploaded filename in the DB if possible
        try:
            with app.app_context():
                y = Yer.query.get(mekan_id)
                if y:
                    img = Image(yer_id=mekan_id, filename=new_filename)
                    db.session.add(img)
                    db.session.commit()
        except Exception as e:
            app.logger.exception(
                'Failed to record uploaded image in DB: %s', e
            )
            flash(
                'Görsel kaydı veritabanına yazılırken hata oluştu',
                'error'
            )
        flash('Görsel yüklendi', 'success')
    else:
        flash('İzin verilmeyen dosya türü', 'error')

    return redirect(url_for('admin_edit_mekan', mekan_id=mekan_id))


@app.route('/admin/image/delete/<int:mekan_id>/<filename>', methods=['POST'])
def admin_delete_image(mekan_id, filename):
    """Delete an image file."""
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath) and str(mekan_id) in filename:
        os.remove(filepath)
        # remove from DB if possible
        try:
            with app.app_context():
                Image.query.filter_by(
                    yer_id=mekan_id,
                    filename=filename
                ).delete()
                db.session.commit()
        except Exception as e:
            app.logger.exception(
                'Failed to delete image record from DB: %s', e
            )
            flash('Görsel veritabanından silinirken hata oluştu', 'error')
        flash('Görsel silindi', 'success')
    else:
        flash('Dosya bulunamadı', 'error')

    return redirect(url_for('admin_edit_mekan', mekan_id=mekan_id))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Public upload endpoint used by the simple upload form.
    Accepts POST with `yer_id`, `position` and `file` and saves the
    uploaded image into `static/images` and records it on the mekan.
    """
    if request.method == 'POST':
        yer_id = request.form.get('yer_id')
        position = request.form.get('position', 'both')
        if 'file' not in request.files:
            flash('Dosya seçilmedi')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Dosya adı boş')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                yid = int(yer_id) if yer_id else None
            except Exception:
                yid = None
            if yid:
                base, ext = os.path.splitext(filename)
                filename = f"{yid}-{position}-{base}{ext}"
            dest = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(dest)
            # attach to mekan if id found
            if yid:
                try:
                    with app.app_context():
                        img = Image(yer_id=yid, filename=filename)
                        db.session.add(img)
                        db.session.commit()
                except Exception as e:
                    app.logger.exception(
                        'Failed to record uploaded image in DB: %s', e
                    )
                    flash('Görsel veritabanına kaydedilemedi', 'error')
            flash('Yükleme tamamlandı')
            return redirect(url_for('index'))
        else:
            flash('İzin verilmeyen dosya türü')
            return redirect(request.url)

    # GET -> show public upload form
    yerler = get_all_yerler_db()
    return render_template('upload.html', yerler=yerler)


@app.route('/')
def index():
    """Main page - list all locations."""
    yerler_for_template = []
    # prefer DB-backed source
    rows = get_all_yerler_db()
    for yer in rows:
        imgs = get_images_for_place(yer['id'], position='all')
        thumb = imgs[0] if imgs else ''
        y = dict(yer)
        y['thumb'] = thumb
        yerler_for_template.append(y)
    return render_template('index_clean.html', yerler=yerler_for_template)


@app.route('/harita')
def harita():
    """Map page."""
    return render_template('harita.html')


@app.route('/hakkimizda')
def hakkimizda():
    """About page."""
    return render_template('hakkimizda.html')


@app.route('/ekip')
def ekip():
    """Team page."""
    return render_template('ekip.html')


@app.route('/yer/<int:yer_id>')
def yer_detay(yer_id):
    """Location detail page."""
    yer = get_yer_db(yer_id)
    if not yer:
        abort(404)
    return render_template('place.html', yer=yer)


@app.route('/api/yerler')
def api_yerler():
    """API endpoint for locations (adds thumb URLs for static clients)."""
    yerler = get_all_yerler_db()
    enriched = []
    for y in yerler:
        imgs = get_images_for_place(y['id'], position='all')
        thumb = imgs[0] if imgs else ''
        row = dict(y)
        row['thumb'] = thumb
        if thumb:
            row['thumb_url'] = url_for('static', filename=thumb, _external=True)
        enriched.append(row)
    return jsonify(enriched)


if __name__ == '__main__':
    app.run(debug=True)
